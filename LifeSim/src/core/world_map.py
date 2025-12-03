# src/core/world_map.py
import pygame
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT

TILE_SIZE = 32

class WorldMap:
    def __init__(self):
        # On définit la taille de la carte en nombre de tuiles
        self.cols = SCREEN_WIDTH // TILE_SIZE + 1
        self.rows = SCREEN_HEIGHT // TILE_SIZE + 1
        
        # 1. On remplit tout d'herbe (0) par défaut
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # 2. On dessine un chemin (1) et un lac (2) "en dur" pour tester
        self._create_test_map()

    def _create_test_map(self):
        """Génère un décor simple pour le test."""
        # Un chemin vertical au milieu
        center_col = self.cols // 2
        for r in range(self.rows):
            self.grid[r][center_col] = 1 # Path
            
        # Un chemin horizontal vers le Shop
        shop_row = 5
        for c in range(center_col, self.cols):
            self.grid[shop_row][c] = 1

        # Un petit lac en bas à gauche
        for r in range(12, 16):
            for c in range(2, 8):
                self.grid[r][c] = 2 # Water

    def draw(self, screen, asset_manager):
        """Dessine toute la grille."""
        for r in range(self.rows):
            for c in range(self.cols):
                tile_id = self.grid[r][c]
                
                # On choisit l'image selon le numéro
                image_key = "grass"
                if tile_id == 1: image_key = "path"
                elif tile_id == 2: image_key = "water"
                
                img = asset_manager.get_image(image_key)
                if img:
                    # Calcul de la position x, y à l'écran
                    x = c * TILE_SIZE
                    y = r * TILE_SIZE
                    screen.blit(img, (x, y))

    def is_walkable(self, x, y):
        """(Futur) Vérifie si on peut marcher à cette position (pixel)."""
        # On convertit les pixels en coordonnées de grille
        c = int(x // TILE_SIZE)
        r = int(y // TILE_SIZE)
        
        # Sécurité : vérifier si on est hors map
        if c < 0 or c >= self.cols or r < 0 or r >= self.rows:
            return False
            
        tile_id = self.grid[r][c]
        if tile_id == 2: # 2 = EAU
            return False # On ne marche pas sur l'eau
            
        return True