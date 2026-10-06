
# Ticket d'incident 4

## Étapes pour reproduire le problème
1. A la première utilisation, lorsqu'il n'y a aucune prédiction.
2. Lancer l'application.
3. Ajouter une image satellite du désert sur la page *Upload image*.
4. *Envoyer*
6. Passer sur la page *Voir les prédictions*.
7. La *Liste des prédictions enregistrées* est vide.

## Résultat actuel
Malgré l'ajout d'une première prédiction, la *Liste des prédictions enregistrées* affiche *Aucune prédiction enregistrée pour le moment.*.

![Capture d'écran de l'incident](./ressources/ticket4.png)

## Comportement attendu
La *Liste des prédictions enregistrées* doit afficher la première *prédiction*.

## Conclusion

Réglé le 2026-10-05 à 14h14.
Ajout d'un test unitaire pour éviter régression.
Ajout monitoring pour traquer évolutions.