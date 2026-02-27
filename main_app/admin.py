from django.contrib import admin
from .models import VisitorLog, VideoPost
admin.site.site_header = "The People's Voice Admin"       # Text in the top blue bar
admin.site.site_title = "Admin Portal"                    # Text in the browser tab
admin.site.index_title = "Website Systems Management"
from .models import Promotion

from django.utils.html import format_html
from .models import NewsPost

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('title', 'category', 'author', 'created_at', 'image_preview')
    
    # Sidebar filters for easier navigation
    list_filter = ('category', 'created_at', 'author')
    
    # Search functionality for headlines and content
    search_fields = ('title', 'content')
    
    # Automatically set the author to the logged-in superuser when creating a post
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If the post is new
            obj.author = request.user
        super().save_model(request, obj, form, change)

    # Show a small thumbnail of the news image in the list
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto; border-radius: 4px;" />', obj.image.url)
        return "No Image"
    
    image_preview.short_description = 'Preview'

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    # Columns to show in the list view
    list_display = ('business_name', 'plan', 'user', 'created_at', 'is_active')
    
    # Add a sidebar filter for status and plans
    list_filter = ('is_active', 'plan', 'created_at')
    
    # Add a search box for business names and titles
    search_fields = ('business_name', 'promotion_title')
    
    # Allow clicking the checkbox directly in the list view to approve ads
    list_editable = ('is_active',)

    # Display a thumbnail of the ad in the detail view
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.ad_image:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.ad_image.url)
        return "No image uploaded"
    
    preview_image.short_description = "Ad Preview"


# Customize how Visitor Logs appear
@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    # These columns will appear in the admin list view
    list_display = ('ip_address', 'location', 'page_visited', 'timestamp')
    
    # Add a filter sidebar on the right
    list_filter = ('location', 'timestamp')
    
    # Add a search bar for IP addresses
    search_fields = ('ip_address', 'location')
    
    # Order by newest first
    ordering = ('-timestamp',)

# Customize how Video Posts appear
@admin.register(VideoPost)
class VideoPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploader_location', 'uploader_ip', 'uploaded_at')
    list_filter = ('uploader_location', 'uploaded_at')
    search_fields = ('title', 'uploader_ip')
    ordering = ('-uploaded_at',)