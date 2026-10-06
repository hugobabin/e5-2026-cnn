import json

import streamlit as st
import requests

# Configuration des URLs de l'API
from config import API_UPLOAD_URL, API_PREDICTIONS_URL, api_retour_url

# Titre de l'application
st.title("🛰️ Application CNN - Classification d'Images Satellites")

# Ajout de la **sidebar** pour la navigation
st.sidebar.title("🔍 Navigation")
menu = st.sidebar.radio("Navigation", ["📤 Upload d'image", "📋 Voir les prédictions"])

# Télécharger les prédictions indépendamment de la page affichée.
try:
    pourfichier = requests.post(API_PREDICTIONS_URL, timeout=(5, 30))
    pourfichier.raise_for_status()
    predictionsjson = pourfichier.json()
    st.sidebar.download_button(
        label="Télécharger le JSON",
        data=json.dumps(predictionsjson, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="predictions.json",
        mime="application/json",
    )
except requests.exceptions.RequestException as e:
    st.sidebar.error(f"Erreur lors du chargement du JSON : {e}")


def envoyer_retour(id_prediction: int, retour: str) -> None:
    """Enregistre le pouce vert/rouge de l'utilisateur et réaffiche le résultat mis à jour."""
    try:
        response = requests.put(
            api_retour_url(id_prediction),
            json={"retour": retour},
            timeout=(5, 30),
        )
        response.raise_for_status()
        st.session_state["derniere_prediction"] = response.json()
        st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de l'envoi du retour : {e}")


def afficher_retour(prediction: dict) -> None:
    """Affiche les pouces vert/rouge sous le résultat de la prédiction."""
    st.write("### 👍 Votre avis sur ce résultat")
    avis = prediction.get("retour")

    colonne_pos, colonne_neg = st.columns(2)
    with colonne_pos:
        if st.button(
            "👍 Le label est correct",
            key=f"retour_pos_{prediction['id']}",
            disabled=avis == "positif",
            use_container_width=True,
        ):
            envoyer_retour(prediction["id"], "positif")
    with colonne_neg:
        if st.button(
            "👎 Le label est incorrect",
            key=f"retour_neg_{prediction['id']}",
            disabled=avis == "negatif",
            use_container_width=True,
        ):
            envoyer_retour(prediction["id"], "negatif")

    if avis == "positif":
        st.success("Merci ! Votre retour positif a bien été pris en compte.")
    elif avis == "negatif":
        st.warning("Merci ! Votre retour négatif a bien été pris en compte.")
    else:
        st.caption(
            "Votre retour alimente la métrique de satisfaction affichée sur Grafana."
        )


# Page : Upload d'image
if menu == "📤 Upload d'image":
    st.header("📤 Upload d'une image et envoi vers l'API")

    # Formulaire de dépôt de fichier
    with st.form("upload_form"):
        uploaded_file = st.file_uploader(
            "Choisissez une image", type=["jpg", "jpeg", "png"]
        )
        submit_button = st.form_submit_button("Envoyer")

    # Si le formulaire est soumis
    if submit_button:
        if uploaded_file is not None:
            # L'image et le résultat sont conservés en session : le clic sur un
            # pouce relance le script et le résultat doit rester affiché.
            st.session_state["derniere_image"] = uploaded_file.getvalue()
            st.session_state.pop("derniere_prediction", None)

            # Préparer le fichier pour l'envoi à l'API
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

            # Envoie la requête POST à l'API
            try:
                response = requests.post(API_UPLOAD_URL, files=files, timeout=(5, 120))
                response.raise_for_status()  # Vérifie si l'API retourne une erreur HTTP
                st.session_state["derniere_prediction"] = response.json()["prediction"]
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Erreur lors de la communication avec l'API : {e}")
        else:
            st.warning("⚠️ Veuillez sélectionner une image avant d'envoyer.")

    # Affichage du dernier résultat, y compris après un clic sur un pouce
    if "derniere_image" in st.session_state:
        st.image(
            st.session_state["derniere_image"],
            caption="Image envoyée",
            use_container_width=True,
        )

    prediction = st.session_state.get("derniere_prediction")
    if prediction:
        st.success("✅ Réponse de l'API :")
        st.json(prediction)
        afficher_retour(prediction)

# Page : Voir les prédictions enregistrées
elif menu == "📋 Voir les prédictions":
    st.header("📋 Liste des prédictions enregistrées")

    # Récupérer les prédictions depuis l'API
    try:
        response = requests.get(API_PREDICTIONS_URL, timeout=(5, 30))
        response.raise_for_status()
        predictions = response.json()

        # Vérifier s'il y a des prédictions
        if predictions:
            for prediction in predictions:
                with st.expander(f"📌 Prédiction {prediction['id']}"):
                    st.write(prediction["image"])
                    st.write(f"🔹 **Label prédit** : {prediction['label']}")
                    st.write(f"📝 **Commentaire** : {prediction['commentaire']}")
                    st.write(f"🛠️ **Modèle utilisé** : {prediction['modele']}")
                    if prediction.get("retour") == "positif":
                        st.write("👍 **Retour utilisateur** : positif")
                    elif prediction.get("retour") == "negatif":
                        st.write("👎 **Retour utilisateur** : négatif")
                    else:
                        st.write("⏳ **Retour utilisateur** : en attente")
        else:
            st.info("Aucune prédiction enregistrée pour le moment.")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de la récupération des prédictions : {e}")
