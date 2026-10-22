from django.shortcuts import render,redirect,get_object_or_404
import requests
# Create your views here.
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
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
 

from django.contrib.auth.decorators import login_required,user_passes_test
 
from .models import Promotion, NewsPost, VisitorLog,VideoPost,ContactMessage # Import your models
from django.contrib.auth.models import User

# from .forms import EmailSignUpForm
from django.shortcuts import get_object_or_404, redirect, render
from .forms import IDCardForm
from .models import IDCard

#updated code based on validation

import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .forms import SignupEmailForm  # The form we discussed
from .utils import send_verification_invite,send_password_reset_email # Your email function

User = get_user_model()
 
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect

from django.shortcuts import render, redirect

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            # Call our new helper function
            send_password_reset_email(request, user)
            
        # We always redirect to 'done' for security (so users can't fish for emails)
        return redirect("password_reset_done")
        
    return render(request, 'registration/password_reset.html')

def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')
# View 1: Request the reset
# def password_reset_request(request):
#     if request.method == "POST":
#         email = request.POST.get('email')
#         user = User.objects.filter(email=email).first()
#         # if user:
#         #     pass
#             # send_password_reset_email(user)
#         # Always show the 'done' message so hackers don't know if an email exists
#         return render(request, 'registration/password_reset_done.html', {'email': email})
#     return render(request, 'registration/password_reset.html')

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
            user.set_password(password)
            user.save()
            return redirect('login') 
        return render(request, 'registration/password_reset_confirm.html')
    else:
        return render(request, 'registration/link_invalid.html')
    

def signup_view(request):
    if request.method == 'POST':
        form = SignupEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            
            # Check if user exists, otherwise create a placeholder user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0] + str(uuid.uuid4())[:8],
                    'is_active': False
                }
            )
            
            if created or not user.is_active:
                send_verification_invite(user)
                #comment only testing purpose
                return render(request, 'registration/signup_done.html', {'email': email})
            else:
                # User exists and is already active
                return render(request, 'registration/signup.html', {
                    'form': form, 
                    'error': "This email is already verified. Please log in."
                })
    else:
        form = SignupEmailForm()
    return render(request, 'registration/signup.html', {'form': form})

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
                return render(request, 'registration/set_password_form.html', {
                    'error': "Passwords do not match. Please try again."
                })
            user.set_password(password)
            user.is_active = True # Activate the user now
            user.save()
            return redirect('login')
        
        return render(request, 'registration/set_password_form.html')
    else:
        return render(request, 'registration/link_invalid.html')

 



def toggle_theme(request):
    # Get the current theme from cookies, default to 'light'
    current_theme = request.COOKIES.get('theme', 'light')
    
    # Switch the value
    new_theme = 'dark' if current_theme == 'light' else 'light'
    
    # Redirect to the previous page the user was looking at
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    
    # Save the new theme in a cookie (valid for 1 year)
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
            return redirect('home') # Replace with your news feed URL name
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
  import pandas as pd
  # Open-Meteo historical weather API for Delhi coordinates (Lat: 28.6139, Lon: 77.2090)
  url = (
      "https://archive-api.open-meteo.com/v1/archive?latitude=28.6139&longitude=77.2090&start_date=2026-09-28&end_date=2026-10-07&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean"
  )

  try:
    response = requests.get(url)
    data = response.json()

    # Convert to Pandas DataFrame
    df = pd.DataFrame({
        "date": data["daily"]["time"],
        "max_temp": data["daily"]["temperature_2m_max"],
        "min_temp": data["daily"]["temperature_2m_min"],
        "precipitation": data["daily"]["precipitation_sum"],
        "humidity": data["daily"]["relative_humidity_2m_mean"],
    })

    # Extract lists for chart visualization in your template
    dates = df["date"].tolist()
    max_temps = df["max_temp"].tolist()
    min_temps = df["min_temp"].tolist()

    # Get the latest day's metrics for quick stats display
    latest = df.iloc[-1]

    context = {
        "city": "Delhi",
        "date": latest["date"],
        "temp": latest["max_temp"],
        "humidity": latest["humidity"],
        "precipitation": latest["precipitation"],
        "chart_labels": dates,
        "chart_max_temps": max_temps,
        "chart_min_temps": min_temps,
        "weather_table": df.to_dict(orient="records"),  # Optional: for table display
    }
  except Exception as e:
    context = {
        "error": "Could not fetch weather data. Please check your network or API URL."
    }

  return render(request, "weather.html", context)

def weather_vi(request):
    # 1. Get Client IP
    # client_ip, is_routable = get_client_ip(request)
    
    # # 2. Get City from search or default to "Auto"
    # city = request.GET.get('city', '')
    
    # # If no city is searched, wttr.in uses the IP address to find the location
    # if not city:
    #     query = client_ip if client_ip and client_ip != '127.0.0.1' else 'Noida'
    # else:
    #     query = city

    # try:
    #     # We append ?format=j1 to get a professional JSON response
    #     url = f"https://wttr.in/{query}?format=j1"
    #     response = requests.get(url)
    #     data = response.json()

    #     # Extracting current conditions
    #     current = data['current_condition'][0]
        
    #     # Extracting hourly forecast for the chart (next 8 data points)
    #     # wttr.in provides data in 3-hour intervals
    #     forecast_list = data['weather'][0]['hourly']
    #     labels = [f"{h['time'][:-2]}:00" for h in forecast_list]
    #     temps = [h['tempC'] for h in forecast_list]

    #     context = {
    #         'city': data['nearest_area'][0]['areaName'][0]['value'],
    #         'temp': current['temp_C'],
    #         'humidity': current['humidity'],
    #         'wind': current['windspeedKmph'],
    #         'description': current['weatherDesc'][0]['value'],
    #         'chart_labels': labels,
    #         'chart_temps': temps,
    #     }
    # except Exception as e:
    #     context = {'error': "Could not fetch weather data. Try a specific city name."}
    context={}
    return render(request, 'weather.html', context)

def home(request):
    posts = NewsPost.objects.all().order_by('-created_at')
    videos = VideoPost.objects.all().order_by('-uploaded_at')
    context = {
        'posts': posts,
        'videos': videos
    }
    
   
    return render(request, 'home.html', context)

def log_view(request):
    # Fetch the last 50 visits, newest first
    logs = VisitorLog.objects.all().order_by('-timestamp')[:50]
    return render(request, 'log.html', {'logs': logs})
def contact(request):
    if request.method == "POST":
        # Extract data from the POST request using the 'name' attribute from your HTML
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Create and save the object in the database
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Redirect or show a success message
        return render(request, 'contact.html', {'success': True})

    return render(request, 'contact.html')

def about(request):
    # Fetch the last 50 visits, newest first
     
    return render(request, 'about.html' )

 
 
def get_trending_news(request):
    # 1. Initialize GNews
    google_news = GNews(language='en', country='US', period='7d', max_results=10)
    
    # 2. Fetch the news (returns a list of dictionaries)
    trending_news = google_news.get_top_news()
    
    # 3. Return as JsonResponse
    # 'safe=False' is required because we are passing a List, not a Dictionary
    return JsonResponse(trending_news, safe=False, json_dumps_params={'indent': 4})


def homett(request):
    # Your logic goes here
    return render(request, 'home.html')

def get_stock_data(request):
    
    data = []
    # STOCKS = ["RELIANCE", "TCS", "INFY", "SBI", "HINDALCO"]
    # for symbol in STOCKS:
    #     try:
    #         price = nse_quote_ltp(symbol)
    #         data.append({'symbol': symbol, 'price': price})
    #     except Exception as err:
    #         print(err)
    #         continue
    # print(data) 
    return JsonResponse({'stocks': data})

def stocks(request):
    ticker_data = [
        {'name': 'RELIANCE', 'price': '2,985.40', 'change': 1.25},
        {'name': 'HDFC BANK', 'price': '1,442.15', 'change': -0.40},
        {'name': 'TCS', 'price': '4,120.00', 'change': 0.82},
        {'name': 'INFY', 'price': '1,490.10', 'change': -1.10},
        {'name': 'ICICI BANK', 'price': '1,085.00', 'change': 0.55},
    ]
    
    context = {
        'ticker_data': ticker_data,
    }
    return render(request, 'stocks.html',context)
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


