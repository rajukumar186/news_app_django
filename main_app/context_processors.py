# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 11:50:41 2026

@author: Raju
"""

from .models import Promotion

def sidebar_promotions(request):
    # Fetch only active promotions, maybe ordered by newest first
    header_promos = Promotion.objects.filter(is_active=True, plan__in=['gold'  ])
    active_promos = Promotion.objects.filter(is_active=True,plan__in=['basic']).order_by('-created_at')[:3]
    full_promos = Promotion.objects.filter(is_active=True, plan__in=[  'premium'])
    return {
        'header_promos': header_promos,
        'active_promos': active_promos,
        'full_promos':full_promos
    }