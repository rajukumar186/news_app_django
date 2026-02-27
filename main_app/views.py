from django.shortcuts import render,redirect
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


from django.contrib.auth.decorators import login_required,user_passes_test
 
from .models import Promotion, NewsPost, VisitorLog,VideoPost # Import your models
from django.contrib.auth.models import User

from .forms import EmailSignUpForm

def signup_view(request):
    if request.method == 'POST':
        form = EmailSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login') # Redirect to your login page
    else:
        form = EmailSignUpForm()
    return render(request, 'signup.html', {'form': form})

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
            return redirect('dashboard') # Redirect to a page of your choice
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
            return redirect('profile')
    else:
        form = VideoUploadForm()
        return render(request, 'profile.html', {'form': form})

def weather_view(request):
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
    # Fetch the last 50 visits, newest first
     
    return render(request, 'contact.html' )

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
    
    return render(request, 'stocks.html')


