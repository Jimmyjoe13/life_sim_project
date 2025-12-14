# src/entities/item.py
from dataclasses import dataclass
from enum import Enum

class ItemCategory(Enum):
    FOOD = "food"
    DRINK = "drink"
    GIFT = "gift"
    TOOL = "tool"

@dataclass
class Item:
    name: str
    hunger_value: float = 0.0  # Combien de faim ça restaure
    energy_value: float = 0.0  # Combien d'énergie ça restaure
    price: int = 0  # Prix de l'objet
    category: ItemCategory = ItemCategory.FOOD
    friendship_value: int = 0  # Bonus d'amitié si offert en cadeau
    
    def __repr__(self):
        return f"{self.name} ({self.price} E)" 

# --- Catalogue d'objets (Pour faciliter la création) ---

# === NOURRITURE ===
def create_apple():
    return Item(name="Pomme Rouge", hunger_value=20.0, energy_value=5.0, price=10, category=ItemCategory.FOOD)

def create_coffee():
    return Item(name="Café Noir", hunger_value=2.0, energy_value=30.0, price=25, category=ItemCategory.DRINK)

def create_croissant():
    return Item(name="Croissant", hunger_value=25.0, energy_value=10.0, price=15, category=ItemCategory.FOOD)

def create_sandwich():
    return Item(name="Sandwich Complet", hunger_value=50.0, energy_value=15.0, price=35, category=ItemCategory.FOOD)

def create_energy_drink():
    return Item(name="Boisson Énergisante", hunger_value=0.0, energy_value=50.0, price=40, category=ItemCategory.DRINK)

def create_pizza():
    return Item(name="Pizza Margherita", hunger_value=60.0, energy_value=20.0, price=50, category=ItemCategory.FOOD)

# === CADEAUX ===
def create_flower():
    return Item(name="Bouquet de Fleurs", hunger_value=0.0, energy_value=0.0, price=30, 
                category=ItemCategory.GIFT, friendship_value=15)

def create_chocolate():
    return Item(name="Boîte de Chocolats", hunger_value=10.0, energy_value=5.0, price=45, 
                category=ItemCategory.GIFT, friendship_value=20)

def create_book():
    return Item(name="Livre Passionnant", hunger_value=0.0, energy_value=0.0, price=25, 
                category=ItemCategory.GIFT, friendship_value=10)

# === CATALOGUE COMPLET ===
ITEM_CATALOG = {
    "Pomme Rouge": create_apple,
    "Café Noir": create_coffee,
    "Croissant": create_croissant,
    "Sandwich Complet": create_sandwich,
    "Boisson Énergisante": create_energy_drink,
    "Pizza Margherita": create_pizza,
    "Bouquet de Fleurs": create_flower,
    "Boîte de Chocolats": create_chocolate,
    "Livre Passionnant": create_book,
}

def get_all_items():
    """Retourne une liste de tous les items disponibles."""
    return [factory() for factory in ITEM_CATALOG.values()]
