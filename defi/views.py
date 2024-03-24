# views.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
import pandas as pd
import networkx as nx
import geopy.distance
import matplotlib.pyplot as plt
from django.http import JsonResponse
from .models import Ville, Arete
from django.http import HttpResponse
import json
import plotly.graph_objs as go

def import_excel(request):
    if request.method == 'POST' and request.FILES.get('fichier_excel'):
        excel_file = request.FILES['fichier_excel']
        data = pd.read_excel(excel_file)

        villes_importees = set()  # Utiliser un ensemble pour garder une trace des villes importées

        for index, jrow in data.iterrows():
            nom_ville = jrow['Ville']
            latitude = jrow['Latitude']
            longitude = jrow['Longitude']

            # Vérifier si la ville a déjà été importée pour éviter les doublons
            if nom_ville in villes_importees:
                continue  # Passer à la prochaine itération si la ville a déjà été importée

            # Vérifier si la ville existe déjà dans la base de données
            villes_existantes = Ville.objects.filter(nom=nom_ville)

            # Si la ville existe déjà, mettre à jour ses coordonnées
            if villes_existantes.exists():
                for ville in villes_existantes:
                    ville.latitude = latitude
                    ville.longitude = longitude
                    ville.save()
            else:
                # Si la ville n'existe pas, créer une nouvelle instance
                Ville.objects.create(nom=nom_ville, latitude=latitude, longitude=longitude)
            
            # Ajouter la ville à l'ensemble des villes importées
            villes_importees.add(nom_ville)

        # Récupérer toutes les villes après l'importation
        villes = Ville.objects.all()

        # Passer les données au template
        return render(request, 'import_success.html', {'villes': villes})
    return render(request, 'import_excel.html')


import os

# Dans votre vue approximation_algorithm
def approximation_algorithm(request):
    villes = Ville.objects.all()
    coords_list = [(ville.nom, (ville.latitude, ville.longitude)) for ville in villes]
    depart = 8  # Indice de la ville de départ (Nouakchott)
    chemin_optimal = voyage_mauritanie(coords_list, depart)
    villes_optimales = [villes[i] for i in chemin_optimal]  # Liste des villes dans l'ordre optimal
    distance_totale = calculer_distance_totale(coords_list, chemin_optimal)
    
    # Création d'un graphe NetworkX
    G = construire_graphe(coords_list)

    # Affichage du graphe avec les noms des villes
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=8, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): f"{G[u][v]['weight']:.2f} km" for u, v in G.edges()}, font_color='red')

    plt.title('Itinéraire Optimal en Mauritanie')
    plt.axis('off')  # Masquer les axes
    plt.tight_layout()  # Ajuster la mise en page
    
    # Enregistrer le graphique en tant qu'image
    image_path = os.path.join('static', 'graph.png')
    plt.savefig(image_path)  # Sauvegarder le graphique en tant qu'image
    plt.close()

    # Obtenir l'URL absolue du graphique
    image_url = request.build_absolute_uri(image_path)

    # Passer l'URL de l'image au template
    return render(request, 'result.html', {'villes': villes_optimales, 'distance_totale': distance_totale, 'image_url': image_url})


def construire_graphe(coords_list):
    G = nx.Graph()
    for i, (nom_ville, coords) in enumerate(coords_list):
        G.add_node(nom_ville)
    # Ajouter les arêtes directement au graphe avec les distances
    for i in range(len(coords_list)):
        for j in range(i+1, len(coords_list)):
            distance = calculer_distance(coords_list[i][1], coords_list[j][1])
            G.add_edge(coords_list[i][0], coords_list[j][0], weight=distance)
    return G

    

    

def calculer_distance_totale(coords_list, chemin_optimal):
    distance_totale = 0
    for i in range(len(chemin_optimal) - 1):
        ville_depart = coords_list[chemin_optimal[i]][1]
        ville_arrivee = coords_list[chemin_optimal[i + 1]][1]
        distance_totale += calculer_distance(ville_depart, ville_arrivee)
    # Ajouter la distance du dernier au premier point pour fermer la boucle
    distance_totale += calculer_distance(coords_list[chemin_optimal[-1]][1], coords_list[chemin_optimal[0]][1])
    return distance_totale

def voyage_mauritanie(coords_list, depart):
    G = construire_graphe(coords_list)
    arbre_couvrant = nx.minimum_spanning_tree(G)
    chemin_optimal = trouver_chemin_optimal(arbre_couvrant, depart)
    return chemin_optimal

def construire_graphe(coords_list):
    G = nx.Graph()
    for i, (nom_ville, coords) in enumerate(coords_list):
        G.add_node(i, ville=nom_ville, coords=coords)
    # Ajouter les arêtes directement au graphe avec les distances
    for i in range(len(coords_list)):
        for j in range(i+1, len(coords_list)):
            distance = calculer_distance(coords_list[i][1], coords_list[j][1])
            G.add_edge(i, j, weight=distance)
    return G


def trouver_chemin_optimal(arbre_couvrant, depart):
    chemin = [depart]
    sommets_visites = set([depart])
    for u, v in nx.dfs_edges(arbre_couvrant, source=depart):
        if v not in sommets_visites:
            chemin.append(v)
            sommets_visites.add(v)
    chemin.append(depart)  # Retour au point de départ
    return chemin

def calculer_distance(coords1, coords2):
    return geopy.distance.geodesic(coords1, coords2).km

from django.shortcuts import render

def ant_colony_algorithm(request):
    # Your view logic goes here
    return render(request, 'alg2.html')
  
def effacer_villes(request):
    # Supprimer toutes les instances de la table Ville
    Ville.objects.all().delete()

    # Afficher un message de confirmation
    message = "Les données des villes ont été effacées avec succès."
    return HttpResponse(message)



