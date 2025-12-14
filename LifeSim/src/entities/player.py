# src/entities/player.py
from dataclasses import dataclass, asdict
from typing import List
from src.entities.item import Item  # <--- Nouvel import

@dataclass
class PlayerStats:
    health: float = 100.0
    hunger: float = 100.0
    energy: float = 100.0
    happiness: float = 100.0
    money: int = 0

class Player:
    def __init__(self, name: str, money: int):
        self.name = name
        self.stats = PlayerStats(money=money)
        self.is_alive = True
        self.position = [400, 300]
        self.speed = 200
        
        # --- NOUVEAU : INVENTAIRE ---
        self.inventory: List[Item] = []
        # --- NOUVEAU : GESTION GRAPHIQUE ---
        self.sprite = None
        self.rect = None # Hitbox pour les collisions

    def set_sprite(self, image):
        """Associe l'image au joueur"""
        self.sprite = image
        # On crée un rectangle de collision basé sur la taille de l'image
        self.rect = image.get_rect(topleft=(self.position[0], self.position[1]))

    def update(self, dt: float, decay_hunger: float, decay_energy: float) -> None:
        if not self.is_alive: return
        # Décroissance
        self.stats.hunger -= decay_hunger * dt
        self.stats.energy -= decay_energy * dt
        self.stats.hunger = max(0.0, min(100.0, self.stats.hunger))
        self.stats.energy = max(0.0, min(100.0, self.stats.energy))

        if self.stats.hunger <= 0 or self.stats.energy <= 0:
            self.take_damage(5 * dt)

    def take_damage(self, amount: float) -> None:
        self.stats.health -= amount
        if self.stats.health <= 0:
            self.stats.health = 0
            self.is_alive = False
            print("💀 Mort du joueur.")

    def move(self, dx: int, dy: int, dt: float) -> None:
        if self.is_alive:
            self.position[0] += dx * self.speed * dt
            self.position[1] += dy * self.speed * dt
            # --- NOUVEAU : On met à jour le RECT qui suit le joueur ---
            if self.rect:
                self.rect.topleft = (int(self.position[0]), int(self.position[1]))

    # --- NOUVELLES MÉTHODES ---
    def add_item(self, item: Item):
        """Ajoute un objet au sac à dos."""
        self.inventory.append(item)
        print(f"🎒 {self.name} a ramassé : {item.name}")

    def eat_item(self, index: int = 0):
        """Mange l'objet à l'index donné (par défaut le premier)."""
        if not self.inventory:
            print("❌ Inventaire vide !")
            return

        if index < len(self.inventory):
            item = self.inventory.pop(index) # Enlève l'objet de la liste
            
            # Applique les effets
            self.stats.hunger += item.hunger_value
            self.stats.energy += item.energy_value
            
            # On s'assure de ne pas dépasser 100
            self.stats.hunger = min(100.0, self.stats.hunger)
            self.stats.energy = min(100.0, self.stats.energy)

    def to_dict(self):
        """Transforme le joueur en dictionnaire pour la sauvegarde JSON."""
        return {
            "name": self.name,
            "position": self.position,
            "stats": asdict(self.stats), # Transforme la dataclass stats en dict
            # Pour l'inventaire, on sauvegarde aussi chaque item en dict
            "inventory": [asdict(item) for item in self.inventory]
        }

    def from_dict(self, data: dict):
        """Recharge les données du joueur depuis un dictionnaire."""
        self.name = data["name"]
        self.position = data["position"]
        
        # 1. Recharger les Stats
        # On met à jour les attributs de self.stats un par un
        stats_data = data["stats"]
        self.stats.health = stats_data["health"]
        self.stats.hunger = stats_data["hunger"]
        self.stats.energy = stats_data["energy"]
        self.stats.happiness = stats_data.get("happiness", 100.0)
        self.stats.money = stats_data["money"]

        # 2. Recharger l'Inventaire
        # On doit recréer des objets Item à partir des dicts
        self.inventory = []
        for item_data in data["inventory"]:
            # On recrée un Item proprement
            loaded_item = Item(
                name=item_data["name"],
                hunger_value=item_data["hunger_value"],
                energy_value=item_data["energy_value"],
                price=item_data.get("price", 0)
            )
            self.inventory.append(loaded_item)

        # Force la mise à jour du rectangle de collision après chargement
        if self.rect:
            self.rect.topleft = (int(self.position[0]), int(self.position[1]))
            
        print(f"💾 Données de {self.name} rechargées avec succès !")
            