
from django.shortcuts import render,redirect,get_object_or_404
import requests 
from django.http import JsonResponse
from nsepython import nse_quote_ltp
from django.http import HttpResponse 
from gnews import GNews
from django.contrib import messages
from django.conf import settings
from ipware import get_client_ip
import ipinfo
from .forms import VideoUploadForm
from django.core.mail import send_mail 
from django.contrib.auth.tokens import default_token_generator 
from django.contrib.auth.decorators import login_required,user_passes_test 
from .models import Promotion, NewsPost, SiteNotice, VisitorLog,VideoPost,ContactMessage  
from django.contrib.auth.models import User 
from .forms import IDCardForm 
import uuid 
import pandas as pd
from django.utils.http import  urlsafe_base64_decode
from django.utils.encoding import force_str
from .forms import SignupEmailForm  # The form we discussed
from .utils import send_verification_invite,send_password_reset_email # Your email function  
from django.contrib.auth.models import User 
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
from django.core.cache import cache
from django.contrib.auth.views import PasswordResetDoneView 
import yfinance as yf
from .models import VisitorLog, VideoPost, Promotion, ContactMessage, NewsPost, IDCard, SiteNotice, AdminReplyMessage
from django.views.decorators.http import require_POST, require_safe
from django.forms import modelform_factory
from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime, timedelta
import pytz





GNEWS_CACHE_KEY = 'gnews_top_headlines'
INEWS_CACHE_KEY='inews_top_headlines'
GNEWS_CACHE_TIMEOUT = 60 * 15




MODEL_MAP = {
    'visitors': apps.get_model('main_app', 'VisitorLog'),
    'videos': apps.get_model('main_app', 'VideoPost'),
    'promotions': apps.get_model('main_app', 'Promotion'),
    'messages': apps.get_model('main_app', 'ContactMessage'),
    'news': apps.get_model('main_app', 'NewsPost'),
    'idcards': apps.get_model('main_app', 'IDCard'),
    'sitenotices': apps.get_model('main_app', 'SiteNotice'),
    'users': apps.get_model('auth', 'User'),
    'groups': apps.get_model('auth', 'Group'),
}


@staff_member_required
def custom_super_admin_dashboard(request):
    # Dynamically fetch counts for all models
    context = {
            'total_users': User.objects.count(),
            'pending_promos': Promotion.objects.filter(is_active=False).count(),
            'active_promos': Promotion.objects.filter(is_active=True).count(),
            'recent_posts': NewsPost.objects.order_by('-created_at')[:5],
            'all_promotions': Promotion.objects.all().order_by('-created_at'),
            'employees' : IDCard.objects.all().order_by("-created_at"),
            'unique_visitors': MODEL_MAP['visitors'].values('ip_address').distinct().count(),
            'counts' : {
                    name: model.objects.count() for name, model in MODEL_MAP.items()
                }
        }
    
    return render(request, 'admin/custom_dashboard.html', {'context': context})

@staff_member_required
def dynamic_model_list(request, model_name):
    if model_name not in MODEL_MAP:
        return redirect('custom_admin_dashboard')
    
    model = MODEL_MAP[model_name]
    objects = model.objects.all().order_by('-pk')[:100]
    fields = [f.name for f in model._meta.fields]
    
    context = {
        'model_name': model_name,
        'model_verbose': model._meta.verbose_name_plural.title(),
        'objects': objects,
        'fields': fields,
    }
    return render(request, 'admin/dynamic_list.html', context)

@staff_member_required
def dynamic_model_create(request, model_name):
    if model_name not in MODEL_MAP:
        return redirect('custom_admin_dashboard')
    
    model = MODEL_MAP[model_name]
    DynamicForm = modelform_factory(model, exclude=[])
    
    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Record created successfully!")
            return redirect('dynamic_model_list', model_name=model_name)
    else:
        form = DynamicForm()
        
    return render(request, 'admin/dynamic_form.html', {'form': form, 'model_name': model_name, 'action': 'Create'})

@staff_member_required
def dynamic_model_edit(request, model_name, pk):
    if model_name not in MODEL_MAP:
        return redirect('custom_admin_dashboard')
    
    model = MODEL_MAP[model_name]
    obj = get_object_or_404(model, pk=pk)
    DynamicForm = modelform_factory(model, exclude=[])
    
    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Record updated successfully!")
            return redirect('dynamic_model_list', model_name=model_name)
    else:
        form = DynamicForm(instance=obj)
        
    return render(request, 'admin/dynamic_form.html', {'form': form, 'model_name': model_name, 'action': 'Edit'})

@staff_member_required
def dynamic_model_delete(request, model_name, pk):
    if model_name not in MODEL_MAP:
        return redirect('custom_admin_dashboard')
    
    model = MODEL_MAP[model_name]
    obj = get_object_or_404(model, pk=pk)
    obj.delete()
    messages.success(request, f"Record deleted successfully!")
    return redirect('dynamic_model_list', model_name=model_name)
 

 



def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
             
            send_password_reset_email(request, user)
             
            return redirect("password_reset_done")
        else:
            messages.error(request, "No user found with this email address.")
        
    return render(request, 'user/password_reset.html')

def password_reset_done(request):
    
    return render(request, 'user/password_reset_done.html')
 

# View 2: The actual reset (Using your existing logic)
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if not password or password != confirm_password:
                return render(request, 'user/password_reset_confirm.html', {
                    'error': 'Passwords do not match or are empty.'
                })

            user.set_password(password)
            user.save()
            auth_login(request, user)
             
        return render(request, 'user/password_reset_confirm.html')
    else:
        return render(request, 'user/link_invalid.html')
    

def signup_view(request):
    '''
    This method is updated using ai
    '''
    if request.method == 'POST':
        form = SignupEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            
            # Safely check if a user with this email already exists
            user = User.objects.filter(email=email).first()
            
            if user is None:
                # Create the user with username EXACTLY matching the email
                user = User.objects.create(
                    email=email,
                    username=email,  # <-- Username and email are identical
                    is_active=False
                )
                created = True
            else:
                created = False

            if created or not user.is_active:
                try: 
                    send_verification_invite(request,user)
                except Exception as e:
                    print(f"DEBUG - Email sending failed: {e}")
                    messages.error(request, "Could not send verification email. Please try again.")
                    return render(request, 'user/signup.html', {'form': form})
                
                return render(request, 'user/signup_done.html', {'email': email})
            else:
                messages.error(request, "This email is already verified. Please log in.")
                return render(request, 'user/signup.html', {
                    'form': form, 
                    'error': "This email is already verified. Please log in."
                })
    else:
        form = SignupEmailForm()
        
    return render(request, 'user/signup.html', {'form': form})

def set_password_confirm(request, uidb64, token):
    """ The view users land on from their email """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                return render(request, 'user/set_password_form.html', {
                    'error': "Passwords do not match. Please try again."
                })
            user.set_password(password)
            user.is_active = True # Activate the user now
            user.save()
            auth_login(request, user)
            return redirect('home')
        
        return render(request, 'user/set_password_form.html')
    else:
        return render(request, 'user/link_invalid.html')

 
 
def toggle_theme(request):
     
    current_theme = request.COOKIES.get('theme', 'light') 
    new_theme = 'dark' if current_theme == 'light' else 'light' 
    response = redirect(request.META.get('HTTP_REFERER', '/')) 
    response.set_cookie('theme', new_theme, max_age=31536000, path='/') 
    return response
 
def news_detail(request, slug):
    # This finds the post or returns a 404 error if it doesn't exist
    post = get_object_or_404(NewsPost, slug=slug)
    return render(request, 'full_artical.html', {'post': post})
@login_required
def create_news(request):
    # Optional: Restrict to staff or specific users
    # if not request.user.is_staff:
    #     messages.error(request, "You do not have permission to publish news.")
    #     return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        if title and content and category:
            # Create the instance but don't save to DB yet
            post = NewsPost(
                author=request.user,
                title=title,
                category=category,
                content=content,
                image=image
            )
            post.save()

            messages.success(request, f"Successfully published: {title}")
            return redirect('home')  
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'news_artical.html')

@login_required
def create_promotion(request):
    if request.method == 'POST':
        # Get data from the POST request
        business_name = request.POST.get('business_name')
        promotion_title = request.POST.get('promotion_title')
        target_url = request.POST.get('target_url')
        plan = request.POST.get('plan')
        
        # Files are handled separately in request.FILES
        ad_image = request.FILES.get('ad_image')

        # Basic validation
        if business_name and promotion_title and ad_image:
            # Create the object without saving to DB yet
            promo = Promotion(
                user=request.user,
                business_name=business_name,
                promotion_title=promotion_title,
                target_url=target_url,
                ad_image=ad_image,
                plan=plan,
                is_active=False  # Keep inactive until admin review
            )
            promo.save()

            messages.success(request, "Your promotion has been submitted! We will review it shortly.")
            return redirect('home') # Redirect to a page of your choice
        else:
            messages.error(request, "Please fill out all required fields and upload an image.")

    return render(request, 'promotional.html')

@user_passes_test(lambda u: u.is_superuser)
def superadmin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'pending_promos': Promotion.objects.filter(is_active=False).count(),
        'active_promos': Promotion.objects.filter(is_active=True).count(),
        'recent_posts': NewsPost.objects.order_by('-created_at')[:5],
        'all_promotions': Promotion.objects.all().order_by('-created_at'),
        'employees' : IDCard.objects.all().order_by("-created_at")
    }
    return render(request, 'superadmin.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_instance = form.save(commit=False) # Create object but don't save yet
            
            # 1. Get IP
            client_ip, is_routable = get_client_ip(request)
            video_instance.uploader_ip = client_ip
            
            # 2. Get Location
            try:
                handler = ipinfo.getHandler(getattr(settings, 'IPINFO_TOKEN', None))
                details = handler.getDetails(client_ip)
                video_instance.uploader_location = f"{details.city}, {details.country_name}"
            except:
                video_instance.uploader_location = "Unknown"
            
            # 3. Get Device Info
            video_instance.uploader_device = request.META.get('HTTP_USER_AGENT', 'Unknown')
            
            video_instance.save() # Now save everything to DB
            return redirect('home')
    else:
        form = VideoUploadForm()
        return render(request, 'profile.html', {'form': form})
    
def weather_view(request):
    # Get the city name from request parameters, defaulting to "Delhi"
    city_name = request.GET.get("city", "Delhi")

    # 1. Use Open-Meteo Geocoding API to find latitude, longitude, and actual city name
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
    
    try:
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        # Check if any location matched the search query
        if "results" in geo_data and len(geo_data["results"]) > 0:
            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            resolved_city = location.get("name", city_name)
            country = location.get("country", "")
            display_location = f"{resolved_city}, {country}" if country else resolved_city
        else:
            # Fallback to Delhi if city is not found
            lat, lon = 28.6139, 77.2090
            display_location = f"Delhi ('{city_name}' not found)"

        # 2. Fetch Forecast Weather Data using the resolved coordinates
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean"
            f"&timezone=auto"
        )

        response = requests.get(weather_url)
        data = response.json()

        # Convert to Pandas DataFrame
        df = pd.DataFrame({
            "date": data["daily"]["time"],
            "max_temp": data["daily"]["temperature_2m_max"],
            "min_temp": data["daily"]["temperature_2m_min"],
            "precipitation": data["daily"]["precipitation_sum"],
            "humidity": data["daily"]["relative_humidity_2m_mean"],
        })

        # Extract lists for charts
        dates = df["date"].tolist()
        max_temps = df["max_temp"].tolist()
        min_temps = df["min_temp"].tolist()
        print(df)
        # Get latest day's metrics
        latest = df.iloc[-1]

        context = {
            "city": display_location,
            "latitude": lat,
            "longitude": lon,
            "date": latest["date"],
            "temp": latest["max_temp"],
            "humidity": latest["humidity"],
            "precipitation": latest["precipitation"],
            "chart_labels": dates,
            "chart_max_temps": max_temps,
            "chart_min_temps": min_temps,
            "weather_table": df.to_dict(orient="records"),
        }

    except Exception as e:
        context = {
            "error": "Could not fetch weather data. Please check your network or city name."
        }

    return render(request, "weather.html", context)

def get_india_news(api_key):
  url = 'https://newsdata.io/api/1/news'
  params = {'apikey': api_key, 'country': 'in', 'language': 'en'}

  try:
    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
      data = response.json()
      articles = []
      for item in data.get('results', []):
        articles.append({
            'title': item.get('title'),
            'description': item.get('description'),
            'image_url': item.get('image_url'),
            'url': item.get('link'),
            'source': item.get('source_id'),
            'published_at': item.get('pubDate'),
        })
      return articles
    else:
      print(f'API Error: {response.status_code} - {response.text}')
      return []
  except requests.RequestException as e:
    print(f'Request failed: {e}')
    return []


def home(request):
   
  posts = NewsPost.objects.all().order_by('-created_at')
  videos = VideoPost.objects.all().order_by('-uploaded_at')
  active_notice = SiteNotice.objects.filter(is_active=True).first() 
  articles = cache.get(GNEWS_CACHE_KEY)

  # 3. If cache is empty (Cache Miss), fetch fresh data from GNews API
  if articles is None:
    print("Cache miss: Fetching fresh data from GNews API")
    api_key = settings.GNEWS_API_KEY
    url = f'https://gnews.io/api/v4/top-headlines?category=general&lang=en&apikey={api_key}'

    try:
      response = requests.get(url, timeout=5)
      if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
 
        cache.set(GNEWS_CACHE_KEY, articles, GNEWS_CACHE_TIMEOUT)
      else:
        print(f'GNews API Error: {response.status_code} {response.text}')
        articles = []
    except requests.RequestException as e:
      print(f'Error fetching news: {e}')
      articles = []
  indian_articles = cache.get(INEWS_CACHE_KEY)
  if indian_articles is None:
    print("Cache miss: Fetching fresh data from INews API")
    api_key = settings.NEWS_API_KEY
     
    indian_articles = get_india_news(api_key)
    cache.set(INEWS_CACHE_KEY, indian_articles, 900)
      

  # 4. Serve response
  context = {'posts': posts, 
             'videos': videos, 
             'api_news': articles,
             'india_news':indian_articles,
             'active_notice': active_notice}

  return render(request, 'home.html', context)
 

def log_view(request):
    # Fetch the last 50 visits, newest first
    logs = VisitorLog.objects.all().order_by('-timestamp') 
    
     

    context = {
        'logs': logs, # Passed to template for client-side search & pagination
    }
    return render(request, 'log.html', context)

def contact(request):
    if request.method == "POST":
        # Extract data from the POST request using the 'name' attribute from your HTML
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Create and save the object in the database
       
        if not email or not message:
             
            messages.error( request,  'Error 400 :Email and message are required.')
            return redirect('contact')

        try:
            ContactMessage.objects.create(
                        name=name,
                        email=email,
                        subject=subject,
                        message=message
                    )
            messages.success(request, "Thank you for your query, we will be back as soon as possible.")
            return redirect('contact')
        except Exception as e:
            messages.error( request,  f'Error 500 :{str(e)}.')
            return redirect('contact')
             
    return render(request, 'contact.html')

@staff_member_required
@require_safe
def api_admin_notifications(request):
  queries = ContactMessage.objects.filter(is_read=False).order_by('-created_at')
  data = [
      {
          'id': q.id,
          'name': q.name,
          'email': q.email,
          'subject': q.subject,
          'message': q.message,
          'created_at': q.created_at.strftime('%b %d, %H:%M'),
      }
      for q in queries
  ]
  return JsonResponse({'status': 'success', 'notifications': data})

@staff_member_required
@require_POST
def api_admin_send_reply(request):
  query_id = request.POST.get('query_id')
  recipient_email = request.POST.get('recipient_email')
  message_body = request.POST.get('message_body')
  subject = request.POST.get('subject', 'Response to your inquiry')

  if not recipient_email or not message_body:
    return JsonResponse(
        {'status': 'error', 'message': 'Recipient and body are required.'},
        status=400,
    )

  try:
    query_obj = None
    if query_id:
      query_obj = ContactMessage.objects.filter(id=query_id).first()
      if query_obj:
        query_obj.is_read = True  # Mark notification as read/handled
        query_obj.save()

    # Save to chat/reply history log
    AdminReplyMessage.objects.create(
        query=query_obj,
        recipient_email=recipient_email,
        message_body=message_body,
        sent_by=request.user,
    )

    # Automatically send the email to the user
    send_mail(
        subject=subject,
        message=message_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )

    return JsonResponse(
        {'status': 'success', 'message': 'Reply emailed successfully!'}
    )
  except Exception as e:
    return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def about(request):
    # Fetch the last 50 visits, newest first
     
    return render(request, 'about.html' )

 
 
def get_trending_news(request):
    # 1. Initialize GNews
    pass
     
 
def stocks(request):
  CACHE_KEY = 'nse_market_dashboard_data'
  cache_timeout = 300  # Cache for 5 minutes to keep it fast and protect rate limits

  dashboard_data = cache.get(CACHE_KEY)

  if not dashboard_data:
    try:
      # 1. Define target Indian stocks & market indices
      ticker_symbols = [
          'RELIANCE.NS',
          'TCS.NS',
          'INFY.NS',
          'HDFCBANK.NS',
          'ICICIBANK.NS',
          'ITC.NS',
      ]
      index_symbols = {
          'Nifty 50': '^NSEI',
          'Bank Nifty': '^NSEBANK',
          'Market VIX': '^INDIAVIX',
      }

      # 2. Fetch Ticker Watch Data
      ticker_data = []
      for symbol in ticker_symbols:
        t = yf.Ticker(symbol)
        hist = t.history(period='1d')
        clean_name = symbol.replace('.NS', '')
        if not hist.empty:
          current_price = hist['Close'].iloc[-1]
          open_price = hist['Open'].iloc[-1]
          change_pct = (
              ((current_price - open_price) / open_price) * 100
              if open_price
              else 0
          )
          ticker_data.append({
              'name': clean_name,
              'price': f'{current_price:,.2f}',
              'change': round(change_pct, 2),
          })

      # 3. Fetch Key Indices Data
      indices_data = []
      for name, symbol in index_symbols.items():
        t = yf.Ticker(symbol)
        hist = t.history(period='1d')
        icon = (
            'N' if 'Nifty 50' in name else ('BN' if 'Bank' in name else 'VIX')
        )
        if not hist.empty:
          current_price = hist['Close'].iloc[-1]
          open_price = hist['Open'].iloc[-1]
          change_pct = (
              ((current_price - open_price) / open_price) * 100
              if open_price
              else 0
          )
          is_up = change_pct >= 0
          sign = '+' if is_up else ''
          indices_data.append({
              'name': name,
              'icon': icon,
              'price': f'{current_price:,.2f}',
              'change': f'{sign}{change_pct:.2f}%',
              'is_up': is_up,
          })

      # 4. Find Top Gainer dynamically from ticker watch list
      if ticker_data:
        top_gainer = max(ticker_data, key=lambda x: x['change'])
        indices_data.append({
            'name': f"Top gainer · {top_gainer['name']}",
            'icon': top_gainer['name'][:1],
            'price': top_gainer['price'],
            'change': f"+{top_gainer['change']}%",
            'is_up': top_gainer['change'] >= 0,
        })

      # 5. Fetch Intraday Chart Data for Nifty 50 (^NSEI)
      nifty_hist = yf.Ticker('^NSEI').history(period='1d', interval='5m')
      if not nifty_hist.empty and len(nifty_hist) > 2:
        min_p = nifty_hist['Close'].min()
        max_p = nifty_hist['Close'].max()
        price_range = max_p - min_p if max_p != min_p else 1

        x_step = 900 / max(len(nifty_hist) - 1, 1)
        points = []
        for i, (_, row) in enumerate(nifty_hist.iterrows()):
          x = 80 + (i * x_step)
          # Map price to SVG Y coordinate (height range 54 to 228)
          y = 228 - ((row['Close'] - min_p) / price_range) * 174
          points.append((x, y))

        path_d = f'M {points[0][0]} {points[0][1]}'
        for px, py in points[1:]:
          path_d += f' L {px:.1f} {py:.1f}'

        chart_line = path_d
        chart_area = f'{path_d} L {points[-1][0]} 228 L {points[0][0]} 228 Z'
        last_cx, last_cy = points[-1]
      else:
        # Fallback SVG coordinates if intraday data is temporarily unavailable
        chart_area = (
            'M 80 170 C 155 174, 218 188, 262 184 S 405 146, 442 150 S 588'
            ' 130, 622 132 S 770 92, 802 100 S 920 112, 980 104 L 980 228 L 80'
            ' 228 Z'
        )
        chart_line = (
            'M 80 170 C 155 174, 218 188, 262 184 S 405 146, 442 150 S 588'
            ' 130, 622 132 S 770 92, 802 100 S 920 112, 980 104'
        )
        last_cx, last_cy = 980, 104

      dashboard_data = {
          'ticker_data': ticker_data,
          'indices_data': indices_data,
          'chart_area': chart_area,
          'chart_line': chart_line,
          'last_cx': last_cx,
          'last_cy': last_cy,
      }

      # Cache the result to prevent hitting Yahoo Finance too frequently
      if ticker_data and indices_data:
        cache.set(CACHE_KEY, dashboard_data, cache_timeout)

    except Exception as e:
      print(f'Live stock fetch error: {e}')
      dashboard_data = None

  # Fallback sample data if the live API request fails or times out
  if not dashboard_data or not dashboard_data.get('ticker_data'):
    print("Using fallback sample data for dashboard due to API failure or timeout.")
    dashboard_data = {
        'ticker_data': [
            {'name': 'Reliance', 'price': '2,985.40', 'change': 1.25},
            {'name': 'TCS', 'price': '3,840.10', 'change': -0.45},
            {'name': 'Infosys', 'price': '1,520.60', 'change': 0.85},
            {'name': 'HDFC Bank', 'price': '1,450.00', 'change': -1.12},
            {'name': 'ICICI Bank', 'price': '1,080.25', 'change': 0.40},
            {'name': 'ITC', 'price': '435.50', 'change': 0.65},
        ],
        'indices_data': [
            {
                'name': 'Nifty 50',
                'icon': 'N',
                'price': '22,713.10',
                'change': '+0.15%',
                'is_up': True,
            },
            {
                'name': 'Bank Nifty',
                'icon': 'BN',
                'price': '48,250.30',
                'change': '+0.32%',
                'is_up': True,
            },
            {
                'name': 'Market VIX',
                'icon': 'VIX',
                'price': '12.45',
                'change': '−2.10%',
                'is_up': False,
            },
            {
                'name': 'Top gainer · Reliance',
                'icon': 'R',
                'price': '2,985.40',
                'change': '+1.25%',
                'is_up': True,
            },
        ],
        'chart_area': (
            'M 80 170 C 155 174, 218 188, 262 184 S 405 146, 442 150 S 588'
            ' 130, 622 132 S 770 92, 802 100 S 920 112, 980 104 L 980 228 L 80'
            ' 228 Z'
        ),
        'chart_line': (
            'M 80 170 C 155 174, 218 188, 262 184 S 405 146, 442 150 S 588'
            ' 130, 622 132 S 770 92, 802 100 S 920 112, 980 104'
        ),
        'last_cx': 980,
        'last_cy': 104,
    }

  context = {
      'ticker_data': dashboard_data['ticker_data'],
      'indices_data': dashboard_data['indices_data'],
      'chart_area': dashboard_data['chart_area'],
      'chart_line': dashboard_data['chart_line'],
      'last_cx': dashboard_data['last_cx'],
      'last_cy': dashboard_data['last_cy'],
  }

  return render(request, 'stocks.html', context)

SYMBOLS_MAP = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "ITC": "ITC.NS",
    "SBIN": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "LT": "LT.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "AXISBANK": "AXISBANK.NS",
    "NTPC": "NTPC.NS",
}

def stocks_view(request):
  """Renders the initial HTML page with market overview data."""
  ticker_data = [
      {"name": "RELIANCE", "price": "2,940.50", "change": 1.45},
      {"name": "TCS", "price": "4,120.00", "change": -0.80},
      {"name": "INFY", "price": "1,650.25", "change": 0.65},
      {"name": "HDFCBANK", "price": "1,450.10", "change": 0.30},
      {"name": "ICICIBANK", "price": "1,105.00", "change": -0.45},
      {"name": "SBIN", "price": "780.20", "change": 1.12},
  ]

  indices_data = [
      {"name": "Nifty 50", "icon": "NF", "price": "22,650.30", "change": "+1.2%", "is_up": True},
      {"name": "Sensex", "icon": "BS", "price": "74,482.78", "change": "+0.9%", "is_up": True},
      {"name": "Gold", "icon": "AU", "price": "72,150.00", "change": "-0.2%", "is_up": False},
      {"name": "Silver", "icon": "AG", "price": "84,300.00", "change": "+1.5%", "is_up": True},
  ]

  context = {
      "ticker_data": ticker_data,
      "indices_data": indices_data,
      "chart_area": "M 78 200 L 250 160 L 450 180 L 650 110 L 980 90 L 980 265 L 78 265 Z",
      "chart_line": "M 78 200 L 250 160 L 450 180 L 650 110 L 980 90",
      "last_cx": "980",
      "last_cy": "90",
  }
  return render(request, "stocks.html", context)

def is_nse_market_open():
  """Checks if current time is during NSE trading hours (Mon-Fri, 9:15 AM - 3:30 PM IST)."""
  ist = pytz.timezone("Asia/Kolkata")
  now = datetime.now(ist)

  # Weekend check (Saturday = 5, Sunday = 6)
  if now.weekday() >= 5:
    return False

  market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
  market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)

  return market_open <= now <= market_close


def stock_live_api(request):
  """Real-time live ticker API endpoint with caching and IST market hour checks."""
  # 1. If market is closed, immediately return last synced data without hitting yfinance
  if not is_nse_market_open():
    cached_close = cache.get("last_market_close_tickers")
    if cached_close:
      return JsonResponse({
          "status": "success",
          "market": "CLOSED",
          "ticker_data": cached_close,
      })

  # 2. If market is open, check cache (valid for 30s) to protect against rate limits
  cached_tickers = cache.get("live_stock_tickers")
  if cached_tickers:
    return JsonResponse({
        "status": "success",
        "market": "OPEN",
        "ticker_data": cached_tickers,
    })

  try:
    live_tickers = []
    for name, symbol in SYMBOLS_MAP.items():
      t = yf.Ticker(symbol)
      hist = t.history(period="2d")
      if hist is not None and not hist.empty and "Close" in hist.columns:
        current_price = float(hist["Close"].iloc[-1])
        prev_close = (
            float(hist["Close"].iloc[-2]) if len(hist) >= 2 else current_price
        )
        change_pct = (
            ((current_price - prev_close) / prev_close) * 100
            if prev_close > 0
            else 0.0
        )

        live_tickers.append({
            "name": name,
            "price": f"{current_price:,.2f}",
            "change": round(change_pct, 2),
        })
      else:
        live_tickers.append({"name": name, "price": "0.00", "change": 0.00})

    # Save to live cache (30s) and permanent close backup (no timeout)
    cache.set("live_stock_tickers", live_tickers, 30)
    cache.set("last_market_close_tickers", live_tickers, None)

    return JsonResponse(
        {"status": "success", "market": "OPEN", "ticker_data": live_tickers}
    )
  except Exception as e:
    # Fallback to last known cache if yfinance throws an error
    fallback = cache.get("last_market_close_tickers") or []
    return JsonResponse(
        {"status": "error", "message": str(e), "ticker_data": fallback},
        status=500,
    )


def get_top_movers_api(request):
  """Calculates Top Gainers & Losers with caching to prevent rate-limiting."""
  # Check cache first (valid for 60 seconds)
  cached_movers = cache.get("cached_market_movers")
  if cached_movers:
    return JsonResponse(cached_movers)

  try:
    stocks_performance = []
    for name, symbol in SYMBOLS_MAP.items():
      try:
        t = yf.Ticker(symbol)
        hist = t.history(period="2d")
        if hist is not None and len(hist) >= 2 and "Close" in hist.columns:
          close_today = float(hist["Close"].iloc[-1])
          close_yesterday = float(hist["Close"].iloc[-2])
          change_pct = (
              ((close_today - close_yesterday) / close_yesterday) * 100
              if close_yesterday > 0
              else 0.0
          )

          stocks_performance.append({
              "name": name,
              "price": f"{close_today:,.2f}",
              "change": round(change_pct, 2),
          })
      except Exception:
        continue

    stocks_performance.sort(key=lambda x: x["change"], reverse=True)

    top_gainers = stocks_performance[:4]
    top_losers = stocks_performance[-4:]
    top_losers.reverse()

    response_data = {
        "status": "success",
        "gainers": top_gainers,
        "losers": top_losers,
    }

    # Store in cache for 60 seconds
    cache.set("cached_market_movers", response_data, 300)

    return JsonResponse(response_data)
  except Exception as e:
    return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
def create_id_card(request):
    if request.method == 'POST':
        form = IDCardForm(request.POST, request.FILES)
        if form.is_valid():
            id_card = form.save()
            return redirect('view_id_card', card_id=id_card.id)
    else:
        form = IDCardForm()
    return render(request, 'create_form.html', {'form': form})
@login_required
def view_id_card(request, card_id):
    id_card = get_object_or_404(IDCard, id=card_id)
    return render(request, 'id_card_template.html', {'id_card': id_card})

def verify_id_card(request, card_id):
    id_card = get_object_or_404(IDCard, id=card_id)
    return render(request, 'verify_result.html', {'id_card': id_card})







'''############################################################################
    Error handle view
   ############################################################################
'''

def custom_404_view(request, exception=None):
    """
    Custom 404 handler view to render the 404 error template.
    """
    return render(request, '404.html', status=404)
def custom_500_view(request):
    """Custom 500 handler (Server Error)."""
    return render(request, '500.html', status=500)

def custom_bad_request_view(request, exception=None):
    return render(request, '400.html', status=400)

def custom_permission_denied_view(request, exception=None):
    return render(request, '403.html', status=403)

def health_check(request):
    return HttpResponse("OK", status=200)
