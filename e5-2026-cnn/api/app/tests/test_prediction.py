from app.bdd.connexion import Connexion
from app.bdd.service import Service_Prediction


def test_lister_predictions_a_le_meme_longueur_que_la_base():
    with Connexion.ouvrir_connexion() as (_, cursor):
        cursor.execute("SELECT COUNT(*) AS total FROM predictions")
        total_en_base = cursor.fetchone()["total"]

    predictions = Service_Prediction.lister_predictions()

    assert len(predictions) == total_en_base
