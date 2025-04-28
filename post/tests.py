from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from .models import Post, PostEditHistory
from topic.models import Topic, Category
import datetime
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

class PostEditWindowTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # Create test topic
        self.topic = Topic.objects.create(
            title='Test Topic',
            content='Test topic content',
            author=self.user,
            category=self.category
        )
        
        # Create test post
        self.post = Post.objects.create(
            content='Test post content',
            author=self.user,
            topic=self.topic
        )
        
        # Set up test client
        self.client = Client()
    
    @override_settings(POST_EDIT_WINDOW_MINUTES=10)  # 10 minutes edit window
    def test_edit_button_visibility(self):
        """Test C3255: Edit button unavailability after edit window"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        
        # Check edit button is visible for a fresh post
        response = self.client.get(reverse('topic:topic_detail', args=[self.topic.id]))
        # Using a more specific text match for the Edit button
        self.assertContains(response, 'class="px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"')
        
        # Simulate post being created 11 minutes ago (outside edit window)
        self.post.created_at = timezone.now() - datetime.timedelta(minutes=11)
        self.post.save()
        
        # Check edit button is no longer visible
        response = self.client.get(reverse('topic:topic_detail', args=[self.topic.id]))
        # Check that the Edit button's CSS class is not present for this post
        self.assertNotContains(response, f'<a href="/posts/{self.post.id}/edit/"')

class PostContentEditTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # Create test topic
        self.topic = Topic.objects.create(
            title='Test Topic',
            content='Test topic content',
            author=self.user,
            category=self.category
        )
        
        # Create test post
        self.post = Post.objects.create(
            content='Test post content',
            author=self.user,
            topic=self.topic
        )
        
        # Set up test client
        self.client = Client()
        
    def test_edit_all_content_types(self):
        """Test C3256: Check whether users can edit all types of content"""
        # Login
        self.client.login(username='testuser', password='testpassword')
        
        # Edit with text and embedded link
        url = reverse('post:edit_post', args=[self.post.id])
        new_content = 'Updated content with <a href="https://example.com">link</a>'
        
        response = self.client.post(url, {
            'content': new_content,
            'edit_reason': 'Adding link'
        })
        
        # Get the updated post
        self.post.refresh_from_db()
        
        # Check post content was updated with link
        self.assertIn('<a href="https://example.com">link</a>', self.post.content)
        
        # Now test with an image upload
        image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        test_image = SimpleUploadedFile('test_image.gif', image_content, content_type='image/gif')
        
        response = self.client.post(url, {
            'content': 'Updated content with image',
            'edit_reason': 'Adding image',
            'image': test_image
        })
        
        # Get the updated post again
        self.post.refresh_from_db()
        
        # Check that the image HTML was added to the post content
        self.assertIn('<img src="/media/uploads/test_image.gif"', self.post.content)
        self.assertIn('class="post-image"', self.post.content)

class PostReversionTest(TestCase):
    def setUp(self):
        # Create test user and moderator
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        self.moderator = User.objects.create_user(
            username='moduser',
            password='modpassword'
        )
        
        # Create moderator group and assign permissions
        mod_group, created = Group.objects.get_or_create(name='Moderators')
        change_post_perm = Permission.objects.get(codename='change_post')
        mod_group.permissions.add(change_post_perm)
        self.moderator.groups.add(mod_group)
        
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        # Create test topic
        self.topic = Topic.objects.create(
            title='Test Topic',
            content='Test topic content',
            author=self.user,
            category=self.category
        )
        
        # Create test post with initial content
        self.post = Post.objects.create(
            content='Initial post content',
            author=self.user,
            topic=self.topic
        )
        
        # Create an edit history for the post
        self.post.content = 'Updated post content'
        self.post.save()
        
        self.history = PostEditHistory.objects.create(
            post=self.post,
            old_content='Initial post content',
            edited_by=self.user,
            edit_reason='Test edit'
        )
        
        # Set up test client
        self.client = Client()
        
    def test_post_reversion(self):
        """Test C3257: Verify that users with permission can revert a post"""
        # Login as moderator
        self.client.login(username='moduser', password='modpassword')
        
        # Get the history page
        history_url = reverse('post:post_history', args=[self.post.id])
        history_response = self.client.get(history_url)
        
        # Confirm history page contains revert option
        self.assertContains(history_response, 'Revert to this version')
        
        # Get the revert page
        revert_url = reverse('post:revert_post', args=[self.history.id])
        revert_get_response = self.client.get(revert_url)
        
        # Confirm revert page loads correctly
        self.assertContains(revert_get_response, 'Confirm Post Reversion')
        
        # Submit the revert form with follow=True to follow redirects
        revert_post_response = self.client.post(revert_url, {
            'confirm': True
        }, follow=True)
        
        # Check for success message in the response content
        self.assertContains(revert_post_response, 'Post reverted to previous version')
        
        # Get the updated post
        self.post.refresh_from_db()
        
        # Verify post has been reverted to the old content
        self.assertEqual(self.post.content, 'Initial post content')
        
    def test_regular_user_cannot_revert(self):
        """Test that regular users cannot revert posts"""
        # Login as regular user
        self.client.login(username='testuser', password='testpassword')
        
        # Try to revert the post
        revert_url = reverse('post:revert_post', args=[self.history.id])
        response = self.client.get(revert_url)
        
        # Should be redirected with an error
        self.assertEqual(response.status_code, 302)  # Redirect status
