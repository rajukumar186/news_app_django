"""
URL configuration for my_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path,reverse_lazy
from main_app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    
    
    path('', views.home, name='home'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    path('superadmin/', views.superadmin_dashboard, name='superadmin'),
    path('profile/', views.profile_view, name='profile'),
    path('promotion/', views.create_promotion, name='promotion'),
    path('news/', views.create_news, name='news'),
    path('stocks/', views.stocks, name='stocks'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('weather/', views.weather_view, name='weather'),
    path('fullnews/<slug:slug>/', views.news_detail, name='news_detail'),
    path(
        'set-password/<str:uidb64>/<str:token>/', 
        views.set_password_confirm, 
        name='set_password_confirm'
    ),
    path('get_news/', views.get_trending_news, name='news'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    #password forget
   path('forgot-password/', views.password_reset_request, name='password_reset_new'),
    
    # 2. THE FIX: You MUST define this exact name to stop the Admin redirect
    path('forgot-password/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),

    # 3. The link from the email (needed for the next step)
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), 
         name='password_reset_confirm'),
    
    
    path('generate/', views.create_id_card, name='create_id_card'),
    path('card/<uuid:card_id>/', views.view_id_card, name='view_id_card'),
    path('verify/<uuid:card_id>/', views.verify_id_card, name='verify_id_card'),
    
    
    # path('forgot-password/', views.password_reset_request, name='password_reset_new'),
    # path('reset-password-confirm/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html',success_url=reverse_lazy('password_reset_done')), name='password_reset_new'),
    # path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    # path('password-reset/done/', views.password_reset, name='password_reset_done'),
    path('log/', views.log_view, name='log'),
    path('api/stocks/', views.get_stock_data, name='stock_api'),
    path("admin/", admin.site.urls),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
