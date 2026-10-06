from prometheus_client import Gauge

PREDICTIONS_EN_BASE = Gauge(
    "cnn_predictions_en_base",
    "Nombre de prédictions actuellement enregistrées dans la base de données",
)

PREDICTIONS_LISTE_COHERENCE = Gauge(
    "cnn_predictions_liste_coherence_ok",
    "1 si lister_predictions renvoie autant de prédictions que la base en contient (ticket-4), 0 sinon",
)

RETOURS_POSITIFS = Gauge(
    "cnn_retours_positifs",
    "Nombre de prédictions actuellement évaluées positivement (pouce vert) par les utilisateurs",
)

RETOURS_NEGATIFS = Gauge(
    "cnn_retours_negatifs",
    "Nombre de prédictions actuellement évaluées négativement (pouce rouge) par les utilisateurs",
)