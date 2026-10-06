import logging

from mysql.connector import Error as DatabaseError

from app.bdd.connexion import Connexion
from app.bdd.prediction import Prediction
from app.metrics import (
    PREDICTIONS_EN_BASE,
    PREDICTIONS_LISTE_COHERENCE,
    RETOURS_NEGATIFS,
    RETOURS_POSITIFS,
)

logger = logging.getLogger(__name__)


class Service_Prediction(Connexion):
    @classmethod
    def assurer_colonne_retour(cls):
        """Ajoute la colonne predictions.retour aux bases créées avant l'ajout du retour utilisateur."""
        try:
            with cls.ouvrir_connexion() as (bdd, cursor):
                cursor.execute(
                    "SELECT COUNT(*) AS presente FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'predictions' "
                    "AND COLUMN_NAME = 'retour'"
                )
                if cursor.fetchone()["presente"]:
                    return
                cursor.execute(
                    "ALTER TABLE predictions ADD COLUMN retour VARCHAR(10) DEFAULT NULL"
                )
                bdd.commit()
                logger.info("Colonne predictions.retour ajoutée au schéma")
        except DatabaseError:
            logger.warning(
                "Impossible de vérifier/ajouter la colonne predictions.retour",
                exc_info=True,
            )

    @classmethod
    def sauvegarder_prediction(cls, prediction: Prediction):
        with cls.ouvrir_connexion() as (bdd, cursor):
            cursor.execute("SELECT id FROM labels")
            labels = cursor.fetchall()

            if labels is None:
                raise ValueError(f"Label absent de la base : {prediction.label}")

            cursor.execute(
                "INSERT INTO predictions (image, label, commentaire, modele) VALUES (%s, %s, %s, %s)",
                [
                    prediction.image,
                    labels[0]["id"],
                    prediction.commentaire,
                    prediction.modele,
                ],
            )

            bdd.commit()
            prediction.id = cursor.lastrowid

            cls._mettre_a_jour_compteurs(cursor)

        return prediction

    @classmethod
    def enregistrer_retour(cls, id_prediction: int, retour: str) -> Prediction | None:
        """Met à jour le pouce vert/rouge laissé par l'utilisateur sur une prédiction."""
        with cls.ouvrir_connexion() as (bdd, cursor):
            cursor.execute("SELECT id FROM predictions WHERE id = %s", [id_prediction])
            if cursor.fetchone() is None:
                return None

            cursor.execute(
                "UPDATE predictions SET retour = %s WHERE id = %s",
                [retour, id_prediction],
            )
            bdd.commit()

            cls._mettre_a_jour_compteurs(cursor)

            cursor.execute(
                "SELECT predictions.id as id, predictions.image as image, labels.label as label, "
                "predictions.commentaire as commentaire, predictions.modele as modele, predictions.retour as retour "
                "FROM predictions JOIN labels ON predictions.label = labels.id "
                "WHERE predictions.id = %s",
                [id_prediction],
            )
            return Prediction(**cursor.fetchone())

    @classmethod
    def lister_predictions(cls):
        with cls.ouvrir_connexion() as (_, cursor):
            cursor.execute(
                "SELECT predictions.id as id, predictions.image as image, labels.label as label, predictions.commentaire as commentaire, predictions.modele as modele, predictions.retour as retour FROM predictions JOIN labels ON predictions.label = labels.id"
            )

            rows = cursor.fetchall()
            predictions = [Prediction(**row) for row in rows]

            totaux = cls._mettre_a_jour_compteurs(cursor)

            if len(predictions) != totaux["total"]:
                PREDICTIONS_LISTE_COHERENCE.set(0)
                logger.warning(
                    "Incohérence : %d prédictions en base, %d renvoyées ( JOIN labels )",
                    totaux["total"],
                    len(predictions),
                )
            else:
                PREDICTIONS_LISTE_COHERENCE.set(1)

            return predictions

    @classmethod
    def rafraichir_metriques(cls):
        """Recharge les compteurs depuis la base : /metrics reste juste après un redémarrage."""
        try:
            with cls.ouvrir_connexion() as (_, cursor):
                cls._mettre_a_jour_compteurs(cursor)
        except DatabaseError:
            logger.warning(
                "Impossible de rafraîchir les métriques depuis la base",
                exc_info=True,
            )

    @staticmethod
    def _mettre_a_jour_compteurs(cursor) -> dict:
        cursor.execute(
            "SELECT COUNT(*) AS total, "
            "COALESCE(SUM(retour = 'positif'), 0) AS positifs, "
            "COALESCE(SUM(retour = 'negatif'), 0) AS negatifs "
            "FROM predictions"
        )
        totaux = cursor.fetchone()

        PREDICTIONS_EN_BASE.set(totaux["total"])
        RETOURS_POSITIFS.set(totaux["positifs"])
        RETOURS_NEGATIFS.set(totaux["negatifs"])

        return totaux
