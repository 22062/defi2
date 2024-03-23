from django.db import models

class Ville(models.Model):
    nom = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.nom

class Arete(models.Model):
    ville_depart = models.ForeignKey(Ville, related_name='aretes_sortantes', on_delete=models.CASCADE)
    ville_arrivee = models.ForeignKey(Ville, related_name='aretes_entrantes', on_delete=models.CASCADE)
    distance = models.FloatField()

    def __str__(self):
        return f"{self.ville_depart} -> {self.ville_arrivee}"
