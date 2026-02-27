# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 12:04:24 2026

@author: Raju
"""

# middleware.py
from ipware import get_client_ip
import ipinfo
from .models import VisitorLog
from django.conf import settings

 

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Get your token from ipinfo.io
        self.handler = ipinfo.getHandler(getattr(settings, 'IPINFO_TOKEN', None))

    def __call__(self, request):
        # 1. Get Client IP
        client_ip, is_routable = get_client_ip(request)
        
        if client_ip:
            # 2. Get Geolocation (City, Country)
            try:
                details = self.handler.getDetails(client_ip)
                location_str = f"{details.city}, {details.country_name}"
            except:
                location_str = "Unknown"

            # 3. Log to Database
            VisitorLog.objects.create(
                ip_address=client_ip,
                page_visited=request.path,
                location=location_str,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

        return self.get_response(request)