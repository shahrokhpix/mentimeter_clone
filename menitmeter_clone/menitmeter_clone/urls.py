# menitmeter_clone/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # مسیرهای اصلی پروژه شما
    path('accounts/', include('allauth.urls')),  # مسیرهای ورود و ثبت‌نام
    path('phone/', include('phone_login.urls')),  # مسیرهای ورود با شماره تلفن
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
