# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 18:20:59 2026

@author: Raju
"""

# news_app/utils.py

from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags 
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
    html_message = render_to_string('varification_email.html', context)
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
    domain = request.get_host()
    protocol = "https" if request.is_secure() else "http"

    context = {
        "email": user.email,
        "domain": domain,
        "site_name": "The People's Era",
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        "token": default_token_generator.make_token(user),
        "protocol": protocol,
    }

    subject = "Password Reset Requested - The People's Era"
    
    # Render both Plain Text and HTML templates
    # text_content = render_to_string("registration/password_reset_email.txt", context)
    html_content = render_to_string("registration/password_reset_email.html", context)
    plain_message = strip_tags(html_content) 
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_content,
        fail_silently=False,
    )
    # Create multi-part email
    # msg = EmailMultiAlternatives(
    #     subject=subject,
    #     body=text_content, # Plain text fallback
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     to=[user.email]
    # )
    # msg.attach_alternative(html_content, "text/html") # HTML version
    # msg.send(fail_silently=False)