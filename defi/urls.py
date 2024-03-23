from django.urls import path
from . import views

urlpatterns = [
    path('', views.importer_fichier_excel, name='importer_fichier_excel'),
    path('resultats/', views.resultats_importation, name='resultats_importation'),
    # Ajoutez d'autres URL ici si nécessaire
]
