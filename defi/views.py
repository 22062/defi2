from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import pandas as pd
from .models import Ville

def importer_fichier_excel(request):
    if request.method == 'POST' and request.FILES['fichier_excel']:
        fichier_excel = request.FILES['fichier_excel']
        fs = FileSystemStorage()
        nom_fichier = fs.save(fichier_excel.name, fichier_excel)
        chemin_fichier = fs.path(nom_fichier)
        # Traiter le fichier Excel
        data = pd.read_excel(chemin_fichier)
        
        # Insérer les données dans la table Ville
        for index, row in data.iterrows():
            ville = Ville(
                nom=row['Ville'],
                latitude=row['Latitude'],
                longitude=row['Longitude']
            )
            ville.save()
        
        # Passez les données à un autre modèle ou affichez-les sur la même page
        return render(request, 'resultats_importation.html', {'data': data})
    return render(request, 'importation_fichier_excel.html')



def resultats_importation(request):
    villes = Ville.objects.all()
    return render(request, 'resultats_importation.html', {'villes': villes})
