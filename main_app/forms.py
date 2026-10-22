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
from django.contrib.auth import get_user_model
from .models import IDCard
User = get_user_model()
class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideoPost
        fields = ['title','caption', 'video_file']
        
DESIGNATION_CHOICES = [
    ('', 'Select Designation'),
    ('Editor-in-Chief', 'Editor-in-Chief'),
    ('Managing Editor', 'Managing Editor'),
    ('Senior Journalist', 'Senior Journalist'),
    ('Investigative Reporter', 'Investigative Reporter'),
    ('Staff Reporter', 'Staff Reporter'),
    ('Bureau Chief', 'Bureau Chief'),
    ('Photojournalist', 'Photojournalist'),
    ('Video Producer', 'Video Producer'),
    ('News Anchor', 'News Anchor'),
    ('Field Producer', 'Field Producer'),
    ('Media Coordinator', 'Media Coordinator'),
] 

GENDER_CHOICES = [
    ('', 'Select Gender'),
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

BLOOD_GROUP_CHOICES = [
    ('', 'Select Blood Group'),
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
    ('NA', 'NA (Not Known)'),
]      
class IDCardForm(forms.ModelForm):
  designation = forms.ChoiceField(
      choices=DESIGNATION_CHOICES,
      widget=forms.Select(attrs={'class': 'form-control'}),
  )
  gender = forms.ChoiceField(
      choices=GENDER_CHOICES,
      widget=forms.Select(attrs={'class': 'form-control'}),
  )
  blood_group = forms.ChoiceField(
      choices=BLOOD_GROUP_CHOICES,
      widget=forms.Select(attrs={'class': 'form-control'}),
  )

  class Meta:
    model = IDCard
    # Excluded 'employee_id' since it auto-generates in the model's save method
    fields = [
        'full_name',
        'designation',
        'gender',
        'blood_group',
        'email',
        'photo',
    ]
    widgets = {
        'full_name': forms.TextInput(attrs={'class': 'form-control'}),
        'email': forms.EmailInput(attrs={'class': 'form-control'}),
        'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
    }
# class EmailSignUpForm(UserCreationForm):
#     email = forms.EmailField(required=True)

#     class Meta:
#         model = User
#         # We only show the email field. 
#         # Password and Confirm Password are included by UserCreationForm automatically.
#         fields = ("email",)

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.username = self.cleaned_data["email"]  # Sync username with email
#         if commit:
#             user.save()
#         return user
class SignupEmailForm(forms.ModelForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'style': 'width: 100%; padding: 10px; border: 1px solid #cbd5e0; border-radius: 4px;'})
    )

    class Meta:
        model = User
        fields = ['email']
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