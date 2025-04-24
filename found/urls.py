from django.urls import path
from . import views

app_name = 'found'
urlpatterns = [
    path('report/', views.report_found_item, name='report'),
    path('list/', views.found_items, name='found_items'),
    path('claim/<int:pk>/', views.claim_item, name='claim'),
    path('my-claims/', views.my_claims, name='my_claims'),
    path('manage-claims/', views.manage_claims, name='manage_claims'),
    path('process-claim/<int:pk>/', views.process_claim, name='process_claim'),
]