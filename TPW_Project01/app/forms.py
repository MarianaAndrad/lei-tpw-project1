
from django import forms
from app.models import Hashtag, Profile

# *** This is the form for the user to register ***
class FormSingup(forms.Form):
    username = forms.CharField( widget=forms.TextInput(
        attrs={'class': 'input input-bordered w-full',
                'placeholder': 'Username',
                'id': 'username',
                'name': 'username',}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'input input-bordered w-full',
                'placeholder': 'Password',
                'id': 'password',
                'name': 'password',}))

    email = forms.EmailField( widget=forms.EmailInput(
        attrs={'class': 'input input-bordered w-full',
                'placeholder': 'Email',
                'id': 'email',
                'name': 'email',}))

    confirmation = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'input input-bordered w-full',
                'placeholder': 'Confirm Password',
                'id': 'password2',
                'name': 'confirmation',}))
    
    photo = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={'class': 'file-input file-input-bordered file-input-primary w-full',
                'placeholder': 'Photo',
                'id': 'photo',
                'name': 'photo',}))

    bio = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'textarea h-24 textarea-bordered textarea-primary w-full',
                'placeholder': 'Bio',
                'id': 'bio',
                'name': 'bio',}))

# *** This is the form for the user to login ***
class FormLogin(forms.Form):
    username = forms.CharField( widget=forms.TextInput(
        attrs={'class': 'input input-bordered w-3/4',
                'placeholder': 'bobross',
                'id': 'username',
                'name': 'username',}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'input input-bordered w-3/4',
                'placeholder': '********',
                'id': 'password',
                'name': 'password',}))

# *** This is the form for the user to edit a post***
class EditPostForm(forms.Form):
    caption = forms.CharField(max_length=256, widget=forms.TextInput(
        attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Caption", 
            "id": "caption", 
            "name": "caption",
    }))
    image = forms.ImageField(widget=forms.FileInput(
        attrs={
            "class": "file-input file-input-bordered file-input-primary w-full",
            "id": "image",
            "name": "image",
    }))

# *** This is the form for the user to add a comment ***
class CommentForm(forms.Form):
    comment = forms.CharField(max_length=256 ,widget=forms.TextInput(
        attrs={
            "class": "input input-bordered w-full",  
            "placeholder": "Comment", 
            "id": "comment", 
            "name": "comment",
    }))

# *** This is the form for the user to edit a image profile ***
class ImageForm(forms.Form):
    image = forms.ImageField(widget=forms.FileInput(
        attrs={
            "class": "file-input file-input-bordered file-input-primary w-full",
            "id": "image",
            "name": "image",
    }))

# *** This is the form for the user to edit a password profile ***
class PasswordForm(forms.Form):
    old_password = forms.CharField(max_length=256, widget=forms.PasswordInput(
        attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Old Password",
            "id": "old_password",
            "name": "old_password",
    }))

    new_password = forms.CharField(max_length=256, widget=forms.PasswordInput(
        attrs={
            "class": "input input-bordered w-full",
            "placeholder": "New Password",
            "id": "new_password",
            "name": "new_password",
    }))

    password_confirm = forms.CharField(max_length=256, widget=forms.PasswordInput(
        attrs={
            "class": "input input-bordered w-full", 
            "placeholder": "Confirm New Password",
            "id": "password_confirm",
            "name": "password_confirm",
    }))

# *** This is the form for the user to edit a bio profile ***
class BioForm(forms.Form):
    bio = forms.CharField(max_length=256, widget=forms.Textarea(
        attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Bio",
            "id": "bio",
            "name": "bio",
    }))

# *** This is the form for the user to search by a username ***
class SearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(
        attrs={
            "class": "input input-bordered w-full",
            "placeholder": "Search User",
            "id": "search",
            "name": "search",
    }))