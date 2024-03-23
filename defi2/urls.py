from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('defi.urls')),  # Remplacez 'votre_app' par le nom de votre application
    # Ajoutez d'autres inclusions d'URL ici si nécessaire
]
