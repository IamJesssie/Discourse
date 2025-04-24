from django import forms
from .models import FoundItem, ClaimRequest

class FoundItemForm(forms.ModelForm):
    class Meta:
        model = FoundItem
        fields = ['title', 'description', 'location', 'id_document']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ClaimRequestForm(forms.ModelForm):
    class Meta:
        model = ClaimRequest
        fields = ['verification_doc']