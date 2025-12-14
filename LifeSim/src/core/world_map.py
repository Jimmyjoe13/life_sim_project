# src/core/world_map.py
"""
Gestionnaire de carte du monde avec rendu amélioré.

Améliorations :
- Utilisation des variantes de tuiles pour briser la répétition
- Pré-calcul des variantes pour performances
- Support de nouveaux types de terrain (sable)
"""
import pygame
import random
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT

TILE_SIZE = 32

# Types de terrain
TERRAIN_GRASS = 0
TERRAIN_PATH = 1
TERRAIN_WATER = 2
TERRAIN_SAND = 3

# Nombre de variantes par type de terrain
TILE_VARIANTS = {
    TERRAIN_GRASS: 5,  # grass.png, grass_1.png, ..., grass_4.png
    TERRAIN_PATH: 3,   # path.png, path_1.png, path_2.png
    TERRAIN_WATER: 3,  # water.png, water_1.png, water_2.png
    TERRAIN_SAND: 2,   # sand.png, sand_1.png
}

class WorldMap:
    def __init__(self, seed: int = 42):
        """
        Initialise la carte du monde.
        
        Args:
            seed: Graine pour la génération aléatoire des variantes
        """
        random.seed(seed)
        
        # Taille de la carte en nombre de tuiles
        self.cols = SCREEN_WIDTH // TILE_SIZE + 1
        self.rows = SCREEN_HEIGHT // TILE_SIZE + 1
        
        # Grille principale (type de terrain)
        self.grid = [[TERRAIN_GRASS for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Grille des variantes (quelle variante de la tuile utiliser)
        # Pré-calculée pour éviter de recalculer à chaque frame
        self.variant_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Générer les variantes pour chaque tuile
        self._generate_variants()
        
        # Créer le décor de test
        self._create_test_map()
    
    def _generate_variants(self):
        """Pré-calcule une variante aléatoire pour chaque tuile."""
        for r in range(self.rows):
            for c in range(self.cols):
                terrain_type = self.grid[r][c]
                max_variants = TILE_VARIANTS.get(terrain_type, 1)
                self.variant_grid[r][c] = random.randint(0, max_variants - 1)

    def _create_test_map(self):
        """Génère un décor simple pour le test."""
        # Un chemin vertical au milieu
        center_col = self.cols // 2
        for r in range(self.rows):
            self.grid[r][center_col] = TERRAIN_PATH
            # Régénérer la variante pour ce type
            self.variant_grid[r][center_col] = random.randint(0, TILE_VARIANTS[TERRAIN_PATH] - 1)
            
        # Un chemin horizontal vers le Shop
        shop_row = 5
        for c in range(center_col, self.cols):
            self.grid[shop_row][c] = TERRAIN_PATH
            self.variant_grid[shop_row][c] = random.randint(0, TILE_VARIANTS[TERRAIN_PATH] - 1)

        # Un petit lac en bas à gauche
        for r in range(12, 16):
            for c in range(2, 8):
                self.grid[r][c] = TERRAIN_WATER
                self.variant_grid[r][c] = random.randint(0, TILE_VARIANTS[TERRAIN_WATER] - 1)
        
        # Une petite plage autour du lac
        beach_positions = [
            (11, 2), (11, 3), (11, 4), (11, 5), (11, 6), (11, 7), (11, 8),  # Haut
            (16, 2), (16, 3), (16, 4), (16, 5), (16, 6), (16, 7), (16, 8),  # Bas
            (12, 1), (13, 1), (14, 1), (15, 1),  # Gauche
            (12, 8), (13, 8), (14, 8), (15, 8),  # Droite
        ]
        for r, c in beach_positions:
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = TERRAIN_SAND
                self.variant_grid[r][c] = random.randint(0, TILE_VARIANTS[TERRAIN_SAND] - 1)
    
    def _get_tile_key(self, terrain_type: int, variant: int) -> str:
        """
        Retourne la clé de l'image pour un type de terrain et sa variante.
        
        Args:
            terrain_type: Type de terrain (TERRAIN_GRASS, etc.)
            variant: Numéro de la variante (0, 1, 2, ...)
        
        Returns:
            Clé pour l'asset manager (ex: "grass", "grass_1", "water_2")
        """
        base_names = {
            TERRAIN_GRASS: "grass",
            TERRAIN_PATH: "path",
            TERRAIN_WATER: "water",
            TERRAIN_SAND: "sand",
        }
        
        base = base_names.get(terrain_type, "grass")
        
        # Variante 0 = nom de base, sinon ajouter le suffixe
        if variant == 0:
            return base
        else:
            return f"{base}_{variant}"

    def draw(self, screen, asset_manager):
        """
        Dessine toute la grille avec les variantes de tuiles.
        
        Args:
            screen: Surface pygame de destination
            asset_manager: Gestionnaire d'assets pour récupérer les images
        """
        for r in range(self.rows):
            for c in range(self.cols):
                terrain_type = self.grid[r][c]
                variant = self.variant_grid[r][c]
                
                # Construire la clé de l'image
                image_key = self._get_tile_key(terrain_type, variant)
                
                img = asset_manager.get_image(image_key)
                
                # Fallback si la variante n'existe pas
                if img is None:
                    # Essayer sans variante
                    fallback_key = self._get_tile_key(terrain_type, 0)
                    img = asset_manager.get_image(fallback_key)
                
                if img:
                    x = c * TILE_SIZE
                    y = r * TILE_SIZE
                    screen.blit(img, (x, y))

    def is_walkable(self, x: float, y: float) -> bool:
        """
        Vérifie si on peut marcher à cette position (pixel).
        
        Args:
            x: Position X en pixels
            y: Position Y en pixels
        
        Returns:
            True si le terrain est praticable
        """
        # Conversion pixels -> coordonnées de grille
        c = int(x // TILE_SIZE)
        r = int(y // TILE_SIZE)
        
        # Vérifier les limites
        if c < 0 or c >= self.cols or r < 0 or r >= self.rows:
            return False
        
        terrain_type = self.grid[r][c]
        
        # L'eau n'est pas praticable
        if terrain_type == TERRAIN_WATER:
            return False
            
        return True
    
    def get_terrain_at(self, x: float, y: float) -> int:
        """
        Retourne le type de terrain à une position donnée.
        
        Args:
            x: Position X en pixels
            y: Position Y en pixels
        
        Returns:
            Type de terrain (TERRAIN_GRASS, TERRAIN_PATH, etc.)
        """
        c = int(x // TILE_SIZE)
        r = int(y // TILE_SIZE)
        
        if c < 0 or c >= self.cols or r < 0 or r >= self.rows:
            return TERRAIN_GRASS  # Défaut hors limites
        
        return self.grid[r][c]