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

def send_verification_invite(user):
    # Create the secure token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # The URL the user clicks in the email
    # Make sure 'set_password_confirm' matches the 'name' in your urls.py
    link = f"https://thepeoplesera.com/set-password/{uid}/{token}/"
    
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