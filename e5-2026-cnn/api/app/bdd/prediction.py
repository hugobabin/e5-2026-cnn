from typing import Literal

from pydantic import BaseModel

class Prediction(BaseModel) :
    id: int | None = None
    image : str
    label : str
    commentaire : str
    modele : str
    retour : str | None = None


class Retour(BaseModel) :
    retour : Literal["positif", "negatif"]
