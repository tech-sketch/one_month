# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from .models import UserProfile
from django import forms

class User_form(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'required': 'true'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'true'}))

    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(User_form, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserProfile_form(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'work_place', 'division']

