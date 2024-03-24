from django import forms

class AlgorithmeForm(forms.Form):
    ALGORITHMES_CHOICES = (
        ('1', 'Algorithme d\'approximation'),
        ('2', 'Heuristique inspirée des fourmis'),
    )
    algorithme = forms.ChoiceField(choices=ALGORITHMES_CHOICES, label='Choisir un algorithme')
