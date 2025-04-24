from django.urls import path
from . import views

app_name = 'topic'

urlpatterns = [
    # FR-TC-001: Topic creation URL
    path('create/', views.create_topic, name='create_topic'),
    # FR-TC-005: Topic detail view
    path('<int:pk>/', views.topic_detail, name='topic_detail'),
]