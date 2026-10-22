# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 18:20:59 2026

@author: Raju
"""

# news_app/utils.py

from django.utils.http import urlsafe_base64_encode
 
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def send_verification_invite(user):
    # Create the secure token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # The URL the user clicks in the email
    # Make sure 'set_password_confirm' matches the 'name' in your urls.py
    link = f"https://thepeoplesera.onrender.com/set-password/{uid}/{token}/"
    
    subject = "Verify your account - The Peoples Era"
    context = {'link': link, 'user': user}
    
    # Render the HTML template
    html_message = render_to_string('emails/verification_email.html', context)
    plain_message = strip_tags(html_message) 
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
def send_password_reset_email(request, user):
    """
    Separated logic to generate token and send the reset email.
    """
    subject = "Password Reset Requested"
    context = {
        "email": user.email,
        "domain": get_current_site(request).domain,
        "site_name": "The People's Era",
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        "token": default_token_generator.make_token(user),
        "protocol": "http", # Use 'https' in production
    }
    
    email_body = render_to_string("registration/password_reset_email.txt", context)
    
    return send_mail(
        subject, 
        email_body, 
        'admin@thepeoplesera.com', 
        [user.email], 
        fail_silently=False
    )