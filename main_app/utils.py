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
 
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def send_verification_invite(request,user):
    current_site = get_current_site(request)
    domain = current_site.domain    
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user) 
    protocol = 'https' if request.is_secure() else 'http'
    
    link = f"{protocol}://{domain}/set-password/{uid}/{token}/"
    print(link)
    subject = "Verify your account - The Peoples Era"
    context = {'link': link, 'user': user}
    
    # Render the HTML template
    html_message = render_to_string('varification_email.html', context)
    plain_message = strip_tags(html_message) 
    
    # send_mail(
    #     subject,
    #     plain_message,
    #     settings.DEFAULT_FROM_EMAIL,
    #     [user.email],
    #     html_message=html_message,
    #     fail_silently=False,
    # )
def send_password_reset_email(request, user):
    domain = request.get_host()
    
    # Ensures 'https' is selected when deployed on Render
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
    
    # Render the HTML template
    html_content = render_to_string("registration/password_reset_email.html", context)
    
    # Create the plain-text alternative automatically
    text_content = strip_tags(html_content) 

    # Create a multi-part email instance
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  # Plain text version for fallback
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    
    # Attach the HTML version with the correct MIME type
    email.attach_alternative(html_content, "text/html")
    print(html_content)
    # Send the email
    # email.send(fail_silently=False)
    
 