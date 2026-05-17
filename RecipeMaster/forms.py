from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .auth_backend import FirestoreUser


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class FirestoreSignUpForm(forms.Form):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if "/" in username:
            raise forms.ValidationError("Username cannot contain /")

        from google.cloud import firestore

        user = firestore.Client().collection("users").document(username).get()
        if user.exists:
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "The two password fields didn't match.")
        return cleaned_data

    def save(self):
        from google.cloud import firestore

        username = self.cleaned_data["username"]
        password = make_password(self.cleaned_data["password1"])
        firestore.Client().collection("users").document(username).set({
            "username": username,
            "password": password,
        })
        return FirestoreUser(username, password)
