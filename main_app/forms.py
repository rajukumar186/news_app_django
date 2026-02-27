# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 16:34:23 2026

@author: Raju
"""

from django import forms
from .models import VideoPost
from .models import Promotion
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideoPost
        fields = ['title', 'video_file']
        
        

class EmailSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        # We only show the email field. 
        # Password and Confirm Password are included by UserCreationForm automatically.
        fields = ("email",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # Sync username with email
        if commit:
            user.save()
        return user

class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['business_name', 'promotion_title', 'target_url', 'ad_image', 'plan']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Company Name'}),
            'promotion_title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Catchy Headline'}),
            'target_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
            'plan': forms.Select(attrs={'class': 'lang-select'}), # Reusing your select style
        }