from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [
    # FR-PE-001: Post edit URL
    path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
    # FR-PE-011: Revert history URL
    path('history/<int:history_id>/revert/', views.revert_post, name='revert_post'),
]