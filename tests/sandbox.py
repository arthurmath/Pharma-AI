
from typing import Annotated, Literal, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class Source(BaseModel):
    medicament: str
    lien: str
    texte: str
    
    
    
source = Source(
    medicament="Doliprane",
    lien="https://base-donnees-publique.medicaments.gouv.fr/medicaments/medicament_12345678.html",
    texte="Doliprane est un médicament utilisé pour traiter la douleur et la fièvre."
)


# print(type(source.lien))




diction = {'role': 'user', 'content': "J'ai mal à la tete depuis deux jours avec des douleurs au ventre 5"}

# print(diction['content'])



