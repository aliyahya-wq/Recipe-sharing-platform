from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('recipes/', include('recipes.urls')),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('accountes/', include('accountes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

