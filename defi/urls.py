from django.urls import path
from . import views

urlpatterns = [
    path('', views.import_excel, name='importer_fichier_excel'),
    path('approximation_algorithm/', views.approximation_algorithm, name='approximation_algorithm'),
     path('ant-colony/', views.ant_colony_algorithm, name='ant_colony_algorithm'),
     path('effacer_villes/', views.effacer_villes, name='effacer_villes'),
  #  path('choose_algorithm/', views.choose_algorithm, name='choose_algorithm'),  # Ajoutez cette ligne
    #path('resultats/', views.resultats_importation, name='resultats_importation'),
     #path('afficher-graphe/', views.afficher_graphe, name='afficher_graphe'),
    # Ajoutez d'autres URL ici si nécessaire
]
