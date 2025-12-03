# src/entities/quest.py
from dataclasses import dataclass

@dataclass
class Quest:
    title: str          # Titre (ex: "Une faim de loup")
    description: str    # Description (ex: "Apporte une Pomme Rouge à Bob")
    target_item: str    # Nom de l'objet requis (ex: "Pomme Rouge")
    reward_amount: int  # Argent gagné
    is_completed: bool = False
    is_active: bool = False