from django import forms
from .models import Post

class MultipleFileField(forms.FileField):
    def clean(self, value, initial=None):
        files = value
        if not files:
            return None

        if isinstance(files, list):
            return files

        return [files]

class PostForm(forms.ModelForm):
    image = MultipleFileField(widget=forms.FileInput(attrs={'accept': 'image/*'}), required=False)
    video = MultipleFileField(widget=forms.FileInput(attrs={'accept': 'video/*'}), required=False)

    class Meta:
        model = Post
        fields = ['user', 'image', 'video', 'caption']
