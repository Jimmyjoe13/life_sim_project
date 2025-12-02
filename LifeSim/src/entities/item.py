# src/entities/item.py
from dataclasses import dataclass

@dataclass
class Item:
    name: str
    hunger_value: float = 0.0  # Combien de faim ça restaure
    energy_value: float = 0.0  # Combien d'énergie ça restaure
    price: int = 0  # Prix de l'objet
    
    def __repr__(self):
        return f"{self.name} ({self.price} E)" 

# --- Catalogue d'objets (Pour faciliter la création) ---
def create_apple():
    return Item(name="Pomme Rouge", hunger_value=20.0, energy_value=5.0, price=10)

def create_coffee():
    return Item(name="Café Noir", hunger_value=2.0, energy_value=15.0, price=25)