# src/entities/house.py
import pygame

class House:
    def __init__(self, x, y):
        # Position EXTÉRIEURE (Monde)
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 64, 64)
        self.sprite = None
        
        # Position du point de sortie (devant la porte)
        self.entry_point = (x + 32, y + 70) 

        # Éléments INTÉRIEURS
        # Le lit sera placé à une position fixe dans la maison
        self.bed_rect = pygame.Rect(300, 200, 32, 48)
        self.bed_sprite = None

    def set_sprites(self, house_img, bed_img):
        self.sprite = house_img
        self.rect = house_img.get_rect(topleft=(self.x, self.y))
        
        self.bed_sprite = bed_img
        # On garde le bed_rect défini dans le init pour l'intérieur

    def check_entry(self, player_rect):
        """Vérifie si le joueur touche la porte extérieure."""
        # On crée une petite zone invisible sur la porte
        door_zone = pygame.Rect(self.rect.centerx - 10, self.rect.bottom - 10, 20, 10)
        return door_zone.colliderect(player_rect)

    def check_sleep(self, player_rect):
        """Vérifie si le joueur touche le lit à l'intérieur."""
        return self.bed_rect.colliderect(player_rect)