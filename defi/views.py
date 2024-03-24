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
import random

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
    
    # Création d'un graphe NetworkX
    G = construire_graphe(coords_list)

    # Création d'un sous-graphe contenant seulement le chemin optimal
    edges = [(chemin_optimal[i], chemin_optimal[i+1]) for i in range(len(chemin_optimal)-1)]
    edges.append((chemin_optimal[-1], chemin_optimal[0]))  # Ajout du lien entre le dernier et le premier point
    optimal_subgraph = G.edge_subgraph(edges).copy()  # Copie du sous-graphe pour éviter l'erreur de graphe gelé

    # Affichage du graphe avec les noms des villes
    pos = nx.spring_layout(G)
    nx.draw(optimal_subgraph, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=8, font_weight='bold',
            edge_color='green')  # Changer la couleur de la ligne en vert

    # Annoter le point de départ (Nouakchott) et le point d'arrivée
    plt.annotate('Départ (Nouakchott)', xy=pos[depart], xytext=(pos[depart][0]-0.1, pos[depart][1]+0.05),
                 arrowprops=dict(facecolor='black', arrowstyle='->'))
    plt.annotate('Arrivée', xy=pos[chemin_optimal[-1]], xytext=(pos[chemin_optimal[-1]][0]+0.05, pos[chemin_optimal[-1]][1]-0.1),
                 arrowprops=dict(facecolor='blue', arrowstyle='->'))

    # Ajouter une flèche pour afficher le prochain ville
    prochain_ville_index = (chemin_optimal[1] if len(chemin_optimal) > 1 else chemin_optimal[0])
    plt.annotate('Ville suivante', xy=pos[prochain_ville_index], xytext=(pos[prochain_ville_index][0]+0.05, pos[prochain_ville_index][1]+0.05),
                 arrowprops=dict(facecolor='blue', arrowstyle='->'))

    plt.title('Solution Optimale en Mauritanie')
    plt.axis('off')  # Masquer les axes
    plt.tight_layout()  # Ajuster la mise en page
    
    # Enregistrer le graphique en tant qu'image
    image_path = os.path.join('static', 'img', 'graph.png')
    plt.savefig(image_path)  # Sauvegarder le graphique en tant qu'image
    plt.close()

    # Obtenir l'URL absolue du graphique
    image_url = request.build_absolute_uri(image_path)

    return render(request, 'result.html', {'image_url': image_url})



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


  
def effacer_villes(request):
    # Supprimer toutes les instances de la table Ville
    Ville.objects.all().delete()

    # Afficher un message de confirmation
    message = "Les données des villes ont été effacées avec succès."
    return HttpResponse(message)
  
def carte_mauritanie(request):
    villes = Ville.objects.all()
    villes_json = json.dumps([{'Ville': ville.nom, 'Latitude': ville.latitude, 'Longitude': ville.longitude} for ville in villes])
    return render(request, 'carte.html', {'villes_json': villes_json})
  

def init_pheromone(G):
    # Fonction pour initialiser la quantité de phéromone sur les arêtes
    pheromone = {}
    for u, v in G.edges():
        pheromone[(u, v)] = 1.0
        pheromone[(v, u)] = 1.0
    return pheromone

def choisir_ville_suivante(G, pheromone, villes_visitees, alpha, beta):
    # Fonction pour choisir la prochaine ville à visiter pour une fourmi donnée
    non_visitees = [v for v in G.nodes() if v not in villes_visitees]
    probabilites = []
    for ville in non_visitees:
        pheromone_edge = pheromone[(villes_visitees[-1], ville)]
        visibilite_edge = 1 / G[villes_visitees[-1]][ville]['weight']
        probabilite = (pheromone_edge ** alpha) * (visibilite_edge ** beta)
        probabilites.append((ville, probabilite))
    if not probabilites:  # Si aucun voisin valide n'est disponible, revenir à la ville de départ
        return villes_visitees[0]
    somme_probabilites = sum(probabilite for _, probabilite in probabilites)
    probabilites = [(ville, probabilite / somme_probabilites) for ville, probabilite in probabilites]
    ville_suivante = random.choices([v for v, _ in probabilites], weights=[probabilite for _, probabilite in probabilites])[0]
    return ville_suivante

def mettre_a_jour_pheromone(pheromone, chemins, Q):
    # Fonction pour mettre à jour la quantité de phéromone sur les arêtes
    for chemin in chemins:
        for i in range(len(chemin) - 1):
            pheromone[(chemin[i], chemin[i + 1])] += Q / len(chemin)
            pheromone[(chemin[i + 1], chemin[i])] += Q / len(chemin)

def tsp_aco(G, iterations, alpha, beta, Q):
    # Fonction pour résoudre le TSP en utilisant l'algorithme de colonie de fourmis (ACO)
    pheromone = init_pheromone(G)
    meilleure_solution = None
    meilleure_distance = float('inf')
    for _ in range(iterations):
        chemins = []
        for _ in range(len(G.nodes())):
            ville_depart = random.choice(list(G.nodes()))
            villes_visitees = [ville_depart]
            distance_totale = 0
            while len(villes_visitees) < len(G.nodes()):
                ville_suivante = choisir_ville_suivante(G, pheromone, villes_visitees, alpha, beta)
                villes_visitees.append(ville_suivante)
                distance_totale += G[villes_visitees[-2]][ville_suivante]['weight']
            chemins.append(villes_visitees)
            if distance_totale < meilleure_distance:
                meilleure_solution = villes_visitees
                meilleure_distance = distance_totale
        mettre_a_jour_pheromone(pheromone, chemins, Q)
    return meilleure_solution, meilleure_distance

def ant_colony_algorithm(request):
    # Vue pour l'algorithme de colonie de fourmis
    villes = Ville.objects.all()

    # Création du graphe pondéré à partir des coordonnées des villes
    G = nx.Graph()
    for ville1 in villes:
        for ville2 in villes:
            if ville1 != ville2:
                distance = geopy.distance.geodesic((ville1.latitude, ville1.longitude), (ville2.latitude, ville2.longitude)).km
                G.add_edge(ville1.nom, ville2.nom, weight=distance)

    # Paramètres de l'algorithme ACO
    iterations = 100
    alpha = 1
    beta = 2
    Q = 1

    # Résoudre le TSP en utilisant l'algorithme ACO
    meilleure_solution, meilleure_distance = tsp_aco(G, iterations, alpha, beta, Q)

    # Dessiner le graphe des résultats
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10)
    nx.draw_networkx_nodes(G, pos, nodelist=meilleure_solution, node_color='red', node_size=500)
    nx.draw_networkx_edges(G, pos, edgelist=[(meilleure_solution[i], meilleure_solution[i + 1]) for i in range(len(meilleure_solution) - 1)], edge_color='red', width=2)
    nx.draw_networkx_edges(G, pos, edgelist=[(meilleure_solution[-1], meilleure_solution[0])], edge_color='red', width=2)
    plt.title('Résultat de l\'algorithme de colonie de fourmis')
    plt.axis('off')
    plt.savefig('resultat_aco.png')  # Sauvegarde du graphe sous forme d'image
    plt.close()  # Fermer le graphe pour éviter les superpositions lors du rendu de la page

    # Passer les résultats à la template
    context = {
        'meilleure_solution': meilleure_solution,
        'meilleure_distance': meilleure_distance,
    }
    return render(request, 'ACO.html', context)