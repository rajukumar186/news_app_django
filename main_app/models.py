from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify 
import uuid
class VisitorLog(models.Model):
    ip_address = models.GenericIPAddressField()
    page_visited = models.CharField(max_length=255)
    location = models.CharField(max_length=255, default="Unknown")
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.ip_address} visited {self.page_visited} from {self.location}"
    
# models.py
class VideoPost(models.Model):
    title = models.CharField(max_length=100)
    caption= models.TextField(null=True)
    video_file = models.FileField(upload_to='videos/')
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata Fields
    uploader_ip = models.GenericIPAddressField(null=True, blank=True)
    uploader_location = models.CharField(max_length=255, null=True, blank=True)
    uploader_device = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.title} (from {self.uploader_location})"
    
class Promotion(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Sidebar - 7 Days ($10)'),
        ('premium', 'Featured Header - 3 Days ($25)'),
        ('gold', 'Full Page Takeover - 1 Day ($50)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)
    promotion_title = models.CharField(max_length=200)
    target_url = models.URLField(help_text="Where should users go when they click?")
    ad_image = models.ImageField(upload_to='promotions/')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False) # Admin approves after payment

    def __str__(self):
        return f"{self.business_name} - {self.plan}"
    
class ContactMessage(models.Model):
    # Defining the choices for the dropdown
    SUBJECT_CHOICES = [
        ('General Inquiry', 'General Inquiry'),
        ('Video Upload Help', 'Video Upload Help'),
        ('Advertising Opportunities', 'Advertising Opportunities'),
        ('Copyright Report', 'Copyright Report'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) # Useful for tracking when it was sent

    def __str__(self):
        return f"{self.name} - {self.subject}"   
class NewsPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = models.SlugField(unique=True, blank=True, null=True) # Add this
    category = models.CharField(max_length=50, choices=[('World', 'World'), ('Tech', 'Tech'), ('Sports', 'Sports'), ('Stock', 'Stock'),('Crime','Crime'),('Intertainment','Intertainment')])
    image = models.ImageField(upload_to='news_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        base_slug = slugify(self.title)
        # Check if slug exists, if so, add a random string
        if NewsPost.objects.filter(slug=base_slug).exists():
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        else:
            self.slug = base_slug
        super().save(*args, **kwargs)
        


    def __str__(self):
        return self.title