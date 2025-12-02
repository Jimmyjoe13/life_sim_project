# src/entities/npc.py
import pygame
import random

class NPC:
    def __init__(self, name, x, y, dialogues):
        self.name = name
        self.x = x
        self.y = y
        self.dialogues = dialogues
        
        # Gestion graphique
        self.sprite = None
        self.rect = pygame.Rect(x, y, 32, 48) # Taille par défaut

    def set_sprite(self, image):
        self.sprite = image
        self.rect = image.get_rect(topleft=(self.x, self.y))

    def check_collision(self, player_rect):
        # On agrandit un peu la zone de détection pour parler sans être COLLÉ au PNJ
        interaction_zone = self.rect.inflate(20, 20)
        return interaction_zone.colliderect(player_rect)

    def talk(self):
        """Retourne une phrase aléatoire."""
        return f"{self.name}: {random.choice(self.dialogues)}"