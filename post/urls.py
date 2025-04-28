from django.urls import path

from . import views

app_name = 'post'

urlpatterns = [
    # FR-PE-001: Post edit URL
    path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
    # C3257: Post history URL
    path('<int:post_id>/history/', views.post_history, name='post_history'),
    # FR-PE-011: Revert history URL
    path('history/<int:history_id>/revert/', views.revert_post, name='revert_post'),
    # New: Create post (reply) URL
    path('create/<int:topic_id>/', views.create_post, name='create_post'),
]