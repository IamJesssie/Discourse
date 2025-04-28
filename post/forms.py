from django import forms
from .models import Post

# FR-PE-001: Post edit form with validation
class PostEditForm(forms.ModelForm):
    # FR-PE-003: Edit reason field
    edit_reason = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Optional edit reason'}),
        help_text="Reason for editing (visible to moderators)"
    )
    
    # C3256: Support for image uploads
    image = forms.ImageField(
        required=False,
        help_text="Upload an image to include in your post"
    )

    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 8, 
                'class': 'w-full px-3 py-2 border rounded-lg',
                'placeholder': 'Content supports text, images, and embedded links'
            }),
        }

    # FR-PE-012: Content sanitization
    def clean_content(self):
        content = self.cleaned_data['content']
        # Basic XSS prevention while preserving allowed HTML
        content = content.replace('<script>', '&lt;script&gt;').replace('</script>', '&lt;/script&gt;')
        return content

    # FR-PE-013: Content validation
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        
        if not content or len(content.strip()) == 0:
            raise forms.ValidationError("Post content cannot be empty")
            
        return cleaned_data

# FR-PE-016: Revert confirmation form
class RevertConfirmationForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        widget=forms.HiddenInput(),
        initial=True
    )

# New: Post creation form (for replies)
class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-3 py-2 border rounded-lg',
                'placeholder': 'Write your reply...'
            }),
        }

    def clean_content(self):
        content = self.cleaned_data['content']
        if not content or len(content.strip()) == 0:
            raise forms.ValidationError('Reply content cannot be empty')
        # Basic XSS prevention
        content = content.replace('<script>', '&lt;script&gt;').replace('</script>', '&lt;/script&gt;')
        return content