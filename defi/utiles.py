import networkx as nx
import geopy.distance
import matplotlib.pyplot as plt

# Fonction pour calculer la distance entre deux points en utilisant les coordonnées GPS
def calculer_distance(coords1, coords2):
    return geopy.distance.geodesic(coords1, coords2).km

# Fonction pour construire le graphe à partir des coordonnées GPS
def construire_graphe(coords_list):
    G = nx.Graph()
    for i, (nom_ville, coords) in enumerate(coords_list):
        G.add_node(i, ville=nom_ville, coords=coords)
        for j in range(i):
            distance = calculer_distance(coords, coords_list[j][1])
            G.add_edge(i, j, weight=distance)
    return G

# Fonction pour trouver le chemin optimal à partir de l'arbre couvrant minimal
def trouver_chemin_optimal(arbre_couvrant, depart):
    chemin = [depart]
    sommets_visites = set([depart])
    for u, v in nx.dfs_edges(arbre_couvrant, source=depart):
        if v not in sommets_visites:
            chemin.append(v)
            sommets_visites.add(v)
    chemin.append(depart)  # Retour au point de départ
    return chemin

# Fonction pour résoudre le problème du voyageur en Mauritanie
def voyage_mauritanie(coords_list, depart):
    # Construire le graphe à partir des coordonnées GPS
    G = construire_graphe(coords_list)
    # Trouver l'arbre couvrant minimal
    arbre_couvrant = nx.minimum_spanning_tree(G)
    # Trouver le chemin optimal à partir de l'arbre couvrant minimal
    chemin_optimal = trouver_chemin_optimal(arbre_couvrant, depart)
    return chemin_optimal

# Fonction pour afficher le graphe avec le chemin optimal
def afficher_graphe_avec_chemin(coords_list, chemin_optimal):
    G = construire_graphe(coords_list)

    # Extraire les positions des noeuds (villes) pour l'affichage
    positions = {i: coords for i, (nom_ville, coords) in enumerate(coords_list)}

    # Dessiner le graphe avec les positions des noeuds
    nx.draw(G, positions, with_labels=True, node_size=200, node_color='lightblue', font_size=8)

    # Dessiner les arêtes du chemin optimal
    chemin_edges = [(chemin_optimal[i], chemin_optimal[i + 1]) for i in range(len(chemin_optimal) - 1)]
    nx.draw_networkx_edges(G, positions, edgelist=chemin_edges, edge_color='red', width=2)

    # Afficher le graphe
    plt.title("Graphe avec chemin optimal")
    plt.show()
