# src/entities/shop.py
from typing import List
import pygame
from src.entities.item import (
    Item, create_apple, create_coffee, create_croissant, 
    create_sandwich, create_energy_drink, create_pizza,
    create_flower, create_chocolate, create_book
)
from src.entities.player import Player

class Shop:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        # Position physique (Carré jaune/or)
        self.rect = pygame.Rect(x, y, 50, 50)
        self.sprite = None  # Pour une future amélioration graphique
        
        # Stock complet avec tous les items disponibles
        self.stock_catalogue: List[Item] = [
            create_apple(),
            create_croissant(),
            create_coffee(),
            create_sandwich(),
            create_energy_drink(),
            create_pizza(),
            create_flower(),
            create_chocolate(),
            create_book()
        ]

    def set_sprite(self, image):
        """Associe l'image au magasin"""
        self.sprite = image
        self.rect = image.get_rect(topleft=(self.x, self.y))

    def check_collision(self, player_rect: pygame.Rect) -> bool:
        # Si le joueur n'a pas encore d'image (rect est None), pas de collision
        if player_rect is None: return False
        return self.rect.colliderect(player_rect)

    def try_buy_item(self, player: Player, item_index: int) -> str:
        """Tente d'acheter un objet. Retourne un message de succès ou d'échec."""
        if item_index >= len(self.stock_catalogue):
            return "Cet article n'existe pas."

        item_to_buy = self.stock_catalogue[item_index]

        # 1. Vérification des fonds
        if player.stats.money >= item_to_buy.price:
            # 2. Transaction
            player.stats.money -= item_to_buy.price
            
            # On crée une NOUVELLE instance de l'objet pour l'inventaire
            # (Sinon on modifierait l'objet du magasin)
            import copy
            new_item = copy.copy(item_to_buy)
            player.add_item(new_item)
            
            return f"Achat réussi : {item_to_buy.name} (-{item_to_buy.price} E)"
        else:
            return "Pas assez d'argent !"