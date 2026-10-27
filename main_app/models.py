from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify 
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from datetime import datetime

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
        
# FOR ID CARD GENERATION AND VALIDATION LOGIC
class IDCard(models.Model):
  # Unique UUID primary key
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

  # Auto-generated serial employee ID (e.g., TPE-2026-000)
  employee_id = models.CharField(max_length=50, unique=True, blank=True)

  full_name = models.CharField(max_length=100)
  designation = models.CharField(max_length=100)
  gender = models.CharField(max_length=20,default='Other', blank=True)
  blood_group = models.CharField(max_length=10, default='NA', blank=True)
  email = models.EmailField()

  photo = models.ImageField(upload_to='id_photos/')
  qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def save(self, *args, **kwargs):
    # 1. Generate sequential employee_id if it doesn't exist yet
    if not self.employee_id:
      current_year = datetime.now().year
      prefix = f'TPE-{current_year}-'

      last_card = (
          IDCard.objects.filter(employee_id__startswith=prefix)
          .order_by('-employee_id')
          .first()
      )

      if last_card:
        last_sequence_str = last_card.employee_id.split('-')[-1]
        next_sequence = int(last_sequence_str) + 1
      else:
        next_sequence = 0  # Starts at 000

      self.employee_id = f'{prefix}{next_sequence:03d}'

    # 2. Save temporarily first so a UUID is assigned if it's a new instance
    # (Required before generating the QR code URL referencing self.id)
    is_new = self._state.adding
    if is_new:
      super().save(*args, **kwargs)

    # 3. Generate QR code pointing to the verification URL with this card's UUID
    # Replace '127.0.0.1:8000' with your live domain in production
    verification_url = f'http://127.0.0.1:8000/verify/{self.id}/'

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    file_name = f'qr_{self.employee_id}.png'

    # Save the generated QR code image file
    self.qr_code.save(file_name, File(buffer), save=False)

    # Final save to persist the QR code image path
    super().save(*args, **kwargs)

  def __str__(self):
    return f'{self.full_name} ({self.employee_id})'


class SiteNotice(models.Model):
    NOTICE_TYPES = [
        ('celebration', '🎉 Celebration / Festival (Image/Animation Popup)'),
        ('urgent', '⚠️ Urgent Notice / Alert (Top Banner)'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    notice_type = models.CharField(max_length=20, choices=NOTICE_TYPES, default='urgent')
    image = models.ImageField(upload_to='notices/', blank=True, null=True, help_text="Optional banner/festival image")
    is_active = models.BooleanField(default=False, help_text="Check to display this notice on the home page")
    created_at = models.DateTimeField(auto_now_add=True)

    def __index__(self):
        return f"{self.get_notice_type_display()} - {self.title}"

    class Meta:
        verbose_name = "Site Notice & Celebration"
        verbose_name_plural = "Site Notices & Celebrations"


        

