# src/entities/workplace.py
import pygame
from src.entities.player import Player

class Workplace:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 64, 80)
        self.sprite = None
        
        # Configuration du Job
        self.salary = 50       # Gain par session
        self.energy_cost = 20  # Coût en énergie
        self.hunger_cost = 15  # Coût en faim

    def set_sprite(self, image):
        self.sprite = image
        self.rect = image.get_rect(topleft=(self.x, self.y))

    def check_collision(self, player_rect: pygame.Rect) -> bool:
        if player_rect is None: return False
        return self.rect.colliderect(player_rect)

    def work(self, player: Player) -> str:
        """Effectue une session de travail."""
        
        # 1. Vérifier si le joueur est en état de travailler
        if player.stats.energy < self.energy_cost:
            return "Trop fatigué pour travailler ! (Mangez du café)"
        
        if player.stats.hunger < self.hunger_cost:
            return "Trop faim pour travailler ! (Mangez une pomme)"

        # 2. Appliquer les coûts
        player.stats.energy -= self.energy_cost
        player.stats.hunger -= self.hunger_cost
        
        # 3. Payer le joueur
        player.stats.money += self.salary
        
        return f"Travail terminé : +{self.salary}€ (Fatigue -{self.energy_cost})"