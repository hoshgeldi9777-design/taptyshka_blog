from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Comment
from .models import Profile



class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }



class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text','category', 'tags', 'image']  #'text'

        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Поделитесь вашими мыслями... ✍️',
                'class': 'form-control rounded-3 shadow-sm',
                'style': 'resize: none; border: 1px solid #e0e0e0;'
            })
        }
        