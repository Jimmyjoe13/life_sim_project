# src/entities/house.py
import pygame
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class House:
    def __init__(self, x, y):
        # --- EXTÉRIEUR ---
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 64, 64)
        self.sprite = None
        # Point de sortie (devant la porte)
        self.entry_point = (x + 32, y + 70) 

        # --- INTÉRIEUR ---
        # Liste qui contiendra tous les meubles : { "type": str, "rect": Rect, "sprite": Surface }
        self.interior_objects = []

    def set_outdoor_sprite(self, image):
        """Définit l'image vue du monde extérieur."""
        self.sprite = image
        self.rect = image.get_rect(topleft=(self.x, self.y))

    def setup_interior(self, asset_manager):
        """
        Configure l'agencement de l'intérieur et charge les sprites des meubles.
        C'est ici qu'on fait le 'level design' de la maison.
        """
        self.interior_objects = []

        # --- ZONE CHAMBRE (Haut Gauche) ---
        self.add_object("bed", 50, 50, asset_manager)
        
        # --- ZONE SALLE DE BAIN (Haut Droite) ---
        self.add_object("toilet", SCREEN_WIDTH - 80, 50, asset_manager)

        # --- ZONE CUISINE (Bas Gauche) ---
        self.add_object("fridge", 50, SCREEN_HEIGHT - 200, asset_manager)
        self.add_object("kitchen", 90, SCREEN_HEIGHT - 200, asset_manager)
        # Table à manger
        self.add_object("table", 200, SCREEN_HEIGHT - 180, asset_manager)
        self.add_object("chair", 216, SCREEN_HEIGHT - 220, asset_manager) # Chaise haut
        self.add_object("chair", 216, SCREEN_HEIGHT - 130, asset_manager) # Chaise bas

        # --- ZONE SALON (Bas Droite) ---
        self.add_object("sofa", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 180, asset_manager)

    def add_object(self, name, x, y, asset_mgr):
        """Helper pour ajouter un meuble à la liste."""
        img = asset_mgr.get_image(name)
        if img:
            rect = img.get_rect(topleft=(x, y))
            self.interior_objects.append({
                "type": name,
                "rect": rect,
                "sprite": img
            })

    def check_entry(self, player_rect):
        """Vérifie si le joueur touche la porte extérieure."""
        door_zone = pygame.Rect(self.rect.centerx - 10, self.rect.bottom - 5, 20, 10)
        return door_zone.colliderect(player_rect)

    def get_interactable_object(self, player_rect):
        """
        Retourne l'objet avec lequel le joueur entre en collision à l'intérieur,
        ou None s'il ne touche rien d'interactif.
        """
        for obj in self.interior_objects:
            # On ajoute une petite marge (inflate) pour faciliter l'interaction
            interaction_zone = obj["rect"].inflate(10, 10)
            if interaction_zone.colliderect(player_rect):
                return obj # Retourne le dictionnaire complet de l'objet
        return None