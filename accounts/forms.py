# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from .models import UserProfile, WorkPlace, Division
from django import forms

class User_form(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'required': 'true', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'required': 'true', 'class': 'form-control'}))

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
    default_work_place = WorkPlace.objects.get_or_create(name='東京')
    default_division = Division.objects.get_or_create(code=2, name='人事')
    work_place = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control'}),
                                        queryset=WorkPlace.objects.all(), initial=default_work_place)
    division = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control'}),
                                      queryset=Division.objects.all(), initial=default_division)

    class Meta:
        model = UserProfile
        fields = ['avatar', 'work_place', 'division']

