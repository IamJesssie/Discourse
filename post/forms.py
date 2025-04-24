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

    class Meta:
        model = Post
        fields = ['content']

    # FR-PE-012: Content sanitization
    def clean_content(self):
        content = self.cleaned_data['content']
        # Basic XSS prevention
        content = content.replace('<script>', '<script>').replace('</script>', '</script>')
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