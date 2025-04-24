from django.db import models
from django.contrib.auth.models import User

class FoundItem(models.Model):
    STATUS_CHOICES = [
        ('FOUND', 'Found'),
        ('PENDING', 'Pending Claim'),
        ('CLAIMED', 'Claimed'),
        ('ARCHIVED', 'Archived')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    found_date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='FOUND')
    id_document = models.FileField(upload_to='id_docs/', null=True, blank=True)
    
    def __str__(self):
        return self.title

class ClaimRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]
    
    item = models.ForeignKey(FoundItem, on_delete=models.CASCADE)
    claimant = models.ForeignKey(User, on_delete=models.CASCADE)
    claim_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    verification_doc = models.FileField(upload_to='verification_docs/')
    
    def __str__(self):
        return f"Claim for {self.item.title} by {self.claimant.username}"