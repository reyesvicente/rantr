from django import forms
from django.core.validators import FileExtensionValidator
from .models import Rant

class RantForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'What\'s on your mind?',
            'rows': 4
        }),
        max_length=230,
        help_text='Maximum 230 characters'
    )
    
    image = forms.ImageField(
        required=False,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif']
            )
        ],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Rant
        fields = ['content', 'image']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Image file too large ( > 5MB )')
        return image

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 1:
            raise forms.ValidationError('Content cannot be empty')
        return content
