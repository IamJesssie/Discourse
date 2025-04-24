from django import forms
from .models import Topic, Category

# FR-TC-001: Topic creation form
class TopicCreationForm(forms.ModelForm):
    # FR-TC-002: Form fields
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
    tags = forms.CharField(required=False, help_text="Comma-separated list of tags")
    
    class Meta:
        model = Topic
        fields = ['category', 'title', 'content', 'tags', 'notify_on_reply']
        
    # FR-TC-008: Title validation
    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 15:
            raise forms.ValidationError("Title must be at least 15 characters long.")
        if len(title) > 255:
            raise forms.ValidationError("Title cannot exceed 255 characters.")
        return title
        
    # FR-TC-010: Content sanitization
    def clean_content(self):
        content = self.cleaned_data['content']
        # Basic XSS prevention
        content = content.replace('<script>', '<script>').replace('</script>', '</script>')
        return content

# FR-TC-006: Cancel button mixin
class CancelButtonMixin:
    def add_cancel_button(self):
        self.fields['cancel'] = forms.BooleanField(
            required=False,
            widget=forms.CheckboxInput(attrs={'hidden': True}),
            label='Cancel'
        )