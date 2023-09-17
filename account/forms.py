# Start of code I wrote
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from account.models import *

"""
User Registration HTML Form for Register View
"""
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        max_length=100, help_text="Required. Enter a valid email address.")

    class Meta:
        model = UserAccount
        fields = ('f_name', 'l_name', 'gender', 'dob', 'email',
                  'username', 'password1', 'password2')

    # Clean Email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            account = UserAccount.object.get(email=email)
        except Exception as e:
            return email
        raise forms.ValidationError(f'Email {email} already exists.')

    # Clean username
    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            account = UserAccount.object.get(username=username)
        except Exception as e:
            return username
        raise forms.ValidationError(f'Username {username} already exists.')


"""
Login Authentication Form for Login View
"""
class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = UserAccount
        fields = ("email", "password")

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid Login Details")


"""
# Updating profile Form for edit profile view
"""
class AccountUpdateForm(forms.ModelForm):

    class Meta:
        model = UserAccount
        fields = ('f_name', 'l_name', 'gender', 'email',
                  'username', 'profile_picture')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = UserAccount.objects.exclude(
                pk=self.instance.pk).get(email=email)
        except UserAccount.DoesNotExist:
            return email
        raise forms.ValidationError('Email "%s" is already in use.' % account)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            account = UserAccount.objects.exclude(
                pk=self.instance.pk).get(username=username)
        except UserAccount.DoesNotExist:
            return username
        raise forms.ValidationError(
            'Username "%s" is already in use.' % username)

    def save(self, commit=True):
        account = super(AccountUpdateForm, self).save(commit=False)
        account.username = self.cleaned_data['username']
        account.email = self.cleaned_data['email'].lower()
        account.profile_image = self.cleaned_data['profile_picture']
        if commit:
            account.save()
        return account


"""
Make a post form for Profile View
"""
class PostForm(forms.ModelForm):
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
    }))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 6,
        'cols': 30,
        'placeholder': 'Say something about your new post! (Required)',
        'class': 'form-control'
    }))

    class Meta:
        model = UserPosts
        fields = ('image', 'content')

# End of code I wrote
