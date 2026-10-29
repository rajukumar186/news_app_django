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
import feedparser
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def send_verification_invite(request,user):
    current_site = get_current_site(request)
    domain = current_site.domain    
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user) 
    protocol = 'https' if request.is_secure() else 'http'
    
    link = f"{protocol}://{domain}/set-password/{uid}/{token}/"
    # print(link)
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
    if not user or not getattr(user, 'email', None):
        return False

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
    
    # Render the HTML template
    html_content = render_to_string("user/password_reset_email.html", context)
    text_content = strip_tags(html_content)
    # print(text_content)
    send_mail(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_content,
        fail_silently=False,
    ) 
    return True



def get_trending_news():
    # Google News RSS feed configured specifically for India (English)
    rss_url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    
    feed = feedparser.parse(rss_url)
    
    trending_items = []
    # Grab the top 5 trending news stories in India
    for entry in feed.entries[:5]:
        trending_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published[:16] # Clean up the date/time display
        })
        
    return trending_items

 