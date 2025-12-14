# LifeSim/src/ui/house_interior.py
"""
Système de rendu moderne pour l'intérieur de la maison.
Gère les pièces, les sols texturés, les murs et les décorations.
"""

import pygame
import random
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui.colors import *


class Room:
    """Représente une pièce dans la maison."""
    
    def __init__(self, name: str, x: int, y: int, width: int, height: int, 
                 floor_color: tuple, wall_color: tuple = None):
        self.name = name
        self.rect = pygame.Rect(x, y, width, height)
        self.floor_color = floor_color
        self.wall_color = wall_color or (80, 80, 90)
        self.objects = []
        self.decorations = []
    
    def add_object(self, obj_type: str, x: int, y: int, sprite, interactive: bool = True):
        """Ajoute un objet à la pièce."""
        if sprite:
            rect = sprite.get_rect(topleft=(x, y))
            self.objects.append({
                "type": obj_type,
                "rect": rect,
                "sprite": sprite,
                "interactive": interactive
            })
    
    def add_decoration(self, x: int, y: int, width: int, height: int, color: tuple):
        """Ajoute une décoration simple."""
        self.decorations.append({
            "rect": pygame.Rect(x, y, width, height),
            "color": color
        })


class ModernHouseInterior:
    """
    Système de rendu moderne pour l'intérieur de la maison.
    Affiche des pièces distinctes avec sols texturés et murs.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configuration des couleurs
        self.colors = {
            # Sols
            "parquet_light": (185, 140, 95),
            "parquet_medium": (160, 115, 70),
            "parquet_dark": (130, 90, 55),
            "tile_white": (240, 245, 250),
            "tile_gray": (220, 225, 230),
            "tile_blue": (200, 220, 240),
            "carpet_red": (140, 60, 70),
            "carpet_pattern": (120, 50, 60),
            
            # Murs
            "wall_cream": (245, 235, 220),
            "wall_blue": (200, 220, 240),
            "wall_green": (210, 235, 210),
            "wall_line": (190, 180, 170),
            "baseboard": (100, 80, 60),
            
            # Décorations
            "window_frame": (120, 90, 60),
            "window_glass": (180, 210, 240),
            "rug": (100, 60, 80),
        }
        
        # Pièces
        self.rooms = []
        self.all_objects = []
        
        # Dimensions des pièces
        self.wall_thickness = 12
        self.baseboard_height = 8
        
        # Cache pour les textures de sol
        self.floor_surfaces = {}
    
    def setup(self, asset_manager):
        """Configure les pièces et charge les objets."""
        self.rooms = []
        self.all_objects = []
        
        half_w = self.screen_width // 2
        half_h = self.screen_height // 2
        
        # === CHAMBRE (Haut Gauche) ===
        bedroom = Room("bedroom", 0, 0, half_w, half_h,
                      floor_color=self.colors["parquet_medium"],
                      wall_color=self.colors["wall_cream"])
        bedroom.add_object("bed", 40, 40, asset_manager.get_image("bed"))
        self.rooms.append(bedroom)
        
        # === SALLE DE BAIN (Haut Droite) ===
        bathroom = Room("bathroom", half_w, 0, half_w, half_h,
                       floor_color=self.colors["tile_blue"],
                       wall_color=self.colors["wall_blue"])
        bathroom.add_object("toilet", self.screen_width - 80, 60, asset_manager.get_image("toilet"))
        self.rooms.append(bathroom)
        
        # === CUISINE (Bas Gauche) ===
        kitchen = Room("kitchen", 0, half_h, half_w, half_h - 60,
                      floor_color=self.colors["tile_white"],
                      wall_color=self.colors["wall_green"])
        kitchen.add_object("fridge", 40, half_h + 40, asset_manager.get_image("fridge"))
        kitchen.add_object("kitchen", 100, half_h + 60, asset_manager.get_image("kitchen"))
        kitchen.add_object("table", 200, half_h + 80, asset_manager.get_image("table"))
        kitchen.add_object("chair", 220, half_h + 40, asset_manager.get_image("chair"))
        kitchen.add_object("chair", 220, half_h + 140, asset_manager.get_image("chair"))
        self.rooms.append(kitchen)
        
        # === SALON (Bas Droite) ===
        living = Room("living", half_w, half_h, half_w, half_h - 60,
                     floor_color=self.colors["parquet_light"],
                     wall_color=self.colors["wall_cream"])
        living.add_object("sofa", self.screen_width - 140, half_h + 60, asset_manager.get_image("sofa"))
        self.rooms.append(living)
        
        # Compiler tous les objets
        for room in self.rooms:
            self.all_objects.extend(room.objects)
        
        # Générer les textures de sol
        self._generate_floor_textures()
    
    def _generate_floor_textures(self):
        """Génère les textures de sol pour chaque pièce."""
        for room in self.rooms:
            surf = pygame.Surface((room.rect.width, room.rect.height))
            
            if "parquet" in str(room.floor_color):
                self._draw_parquet(surf, room.floor_color, room.rect.width, room.rect.height)
            elif "tile" in room.name or room.name in ["bathroom", "kitchen"]:
                self._draw_tiles(surf, room.floor_color, room.rect.width, room.rect.height)
            else:
                self._draw_parquet(surf, room.floor_color, room.rect.width, room.rect.height)
            
            self.floor_surfaces[room.name] = surf
    
    def _draw_parquet(self, surface: pygame.Surface, base_color: tuple, width: int, height: int):
        """Dessine un sol en parquet."""
        plank_width = 40
        plank_height = 12
        
        light = tuple(min(255, c + 15) for c in base_color)
        dark = tuple(max(0, c - 20) for c in base_color)
        
        for y in range(0, height, plank_height):
            offset = (y // plank_height % 2) * (plank_width // 2)
            for x in range(-plank_width, width + plank_width, plank_width):
                px = x + offset
                # Couleur avec variation
                if random.random() > 0.7:
                    color = light
                elif random.random() > 0.5:
                    color = dark
                else:
                    color = base_color
                
                pygame.draw.rect(surface, color, (px, y, plank_width - 1, plank_height - 1))
                # Ligne de séparation
                pygame.draw.line(surface, dark, (px, y + plank_height - 1), 
                               (px + plank_width, y + plank_height - 1), 1)
    
    def _draw_tiles(self, surface: pygame.Surface, base_color: tuple, width: int, height: int):
        """Dessine un sol carrelé."""
        tile_size = 32
        
        grout = tuple(max(0, c - 30) for c in base_color)
        
        for y in range(0, height, tile_size):
            for x in range(0, width, tile_size):
                # Variation légère de couleur
                var = random.randint(-5, 5)
                color = tuple(max(0, min(255, c + var)) for c in base_color)
                
                pygame.draw.rect(surface, color, (x + 1, y + 1, tile_size - 2, tile_size - 2))
                
                # Joints
                pygame.draw.line(surface, grout, (x, y), (x + tile_size, y), 1)
                pygame.draw.line(surface, grout, (x, y), (x, y + tile_size), 1)
    
    def draw(self, screen: pygame.Surface):
        """Dessine l'intérieur complet de la maison."""
        # 1. Dessiner les sols de chaque pièce
        for room in self.rooms:
            floor_surf = self.floor_surfaces.get(room.name)
            if floor_surf:
                screen.blit(floor_surf, room.rect.topleft)
        
        # 2. Dessiner les murs et séparations
        self._draw_walls(screen)
        
        # 3. Dessiner les décorations de fond
        self._draw_decorations(screen)
        
        # 4. Dessiner les objets
        for obj in self.all_objects:
            if obj["sprite"]:
                # Ombre sous l'objet
                shadow_rect = pygame.Rect(
                    obj["rect"].x + 4, obj["rect"].bottom - 4,
                    obj["rect"].width - 8, 6
                )
                pygame.draw.ellipse(screen, (0, 0, 0, 40), shadow_rect)
                
                # Objet
                screen.blit(obj["sprite"], obj["rect"])
        
        # 5. Zone de sortie
        self._draw_exit_zone(screen)
    
    def _draw_walls(self, screen: pygame.Surface):
        """Dessine les murs de séparation et plinthes."""
        half_w = self.screen_width // 2
        half_h = self.screen_height // 2
        
        # Murs verticaux avec texture
        wall_vertical = pygame.Surface((self.wall_thickness, self.screen_height - 80), pygame.SRCALPHA)
        wall_vertical.fill((100, 90, 85))
        # Texture
        for y in range(0, wall_vertical.get_height(), 20):
            pygame.draw.line(wall_vertical, (80, 70, 65), (0, y), (self.wall_thickness, y), 1)
        # Bordures
        pygame.draw.line(wall_vertical, (60, 50, 45), (0, 0), (0, wall_vertical.get_height()), 2)
        pygame.draw.line(wall_vertical, (120, 110, 100), (self.wall_thickness - 1, 0), 
                        (self.wall_thickness - 1, wall_vertical.get_height()), 1)
        
        screen.blit(wall_vertical, (half_w - self.wall_thickness // 2, 0))
        
        # Mur horizontal
        wall_horizontal = pygame.Surface((self.screen_width, self.wall_thickness), pygame.SRCALPHA)
        wall_horizontal.fill((100, 90, 85))
        for x in range(0, self.screen_width, 20):
            pygame.draw.line(wall_horizontal, (80, 70, 65), (x, 0), (x, self.wall_thickness), 1)
        pygame.draw.line(wall_horizontal, (60, 50, 45), (0, 0), (self.screen_width, 0), 2)
        pygame.draw.line(wall_horizontal, (120, 110, 100), (0, self.wall_thickness - 1), 
                        (self.screen_width, self.wall_thickness - 1), 1)
        
        screen.blit(wall_horizontal, (0, half_h - self.wall_thickness // 2))
        
        # Plinthes extérieures
        baseboard_color = self.colors["baseboard"]
        pygame.draw.rect(screen, baseboard_color, (0, 0, self.screen_width, self.baseboard_height))
        pygame.draw.rect(screen, baseboard_color, (0, 0, self.baseboard_height, self.screen_height))
        pygame.draw.rect(screen, baseboard_color, 
                        (self.screen_width - self.baseboard_height, 0, self.baseboard_height, self.screen_height))
    
    def _draw_decorations(self, screen: pygame.Surface):
        """Dessine les décorations (fenêtres, tapis, tableaux)."""
        half_h = self.screen_height // 2
        
        # Fenêtres sur le mur du haut
        for x in [80, 200, self.screen_width - 180, self.screen_width - 100]:
            self._draw_window(screen, x, 10, 60, 50)
        
        # Tapis dans le salon
        rug_x = self.screen_width // 2 + 60
        rug_y = half_h + 100
        pygame.draw.ellipse(screen, self.colors["rug"], (rug_x, rug_y, 120, 80))
        pygame.draw.ellipse(screen, (120, 80, 100), (rug_x + 10, rug_y + 10, 100, 60))
        
        # Tapis dans la chambre
        pygame.draw.rect(screen, (100, 120, 140), (120, 70, 100, 60), border_radius=5)
        pygame.draw.rect(screen, (120, 140, 160), (125, 75, 90, 50), border_radius=3)
    
    def _draw_window(self, screen: pygame.Surface, x: int, y: int, width: int, height: int):
        """Dessine une fenêtre."""
        # Cadre
        pygame.draw.rect(screen, self.colors["window_frame"], (x, y, width, height))
        # Vitre
        pygame.draw.rect(screen, self.colors["window_glass"], (x + 4, y + 4, width - 8, height - 8))
        # Montants
        mid_x = x + width // 2
        mid_y = y + height // 2
        pygame.draw.line(screen, self.colors["window_frame"], (mid_x, y + 4), (mid_x, y + height - 4), 3)
        pygame.draw.line(screen, self.colors["window_frame"], (x + 4, mid_y), (x + width - 4, mid_y), 3)
        # Reflet
        pygame.draw.line(screen, (255, 255, 255, 100), (x + 8, y + 8), (x + 20, y + 20), 2)
    
    def _draw_exit_zone(self, screen: pygame.Surface):
        """Dessine la zone de sortie en bas."""
        exit_height = 60
        exit_y = self.screen_height - exit_height
        
        # Fond de la zone de sortie (plus sombre)
        pygame.draw.rect(screen, (60, 50, 45), (0, exit_y, self.screen_width, exit_height))
        
        # Paillasson
        mat_x = self.screen_width // 2 - 40
        mat_y = exit_y + 10
        pygame.draw.rect(screen, (100, 80, 60), (mat_x, mat_y, 80, 40), border_radius=5)
        pygame.draw.rect(screen, (80, 60, 40), (mat_x + 5, mat_y + 5, 70, 30), border_radius=3)
        
        # Texte "SORTIE"
        font = pygame.font.Font(None, 24)
        text = font.render("↓ SORTIE", True, (200, 200, 200))
        text_x = self.screen_width // 2 - text.get_width() // 2
        screen.blit(text, (text_x, exit_y + 35))
        
        # Porte (fond)
        door_width = 100
        door_x = self.screen_width // 2 - door_width // 2
        pygame.draw.rect(screen, (80, 60, 45), (door_x, exit_y - 10, door_width, exit_height + 10))
        pygame.draw.rect(screen, (100, 80, 60), (door_x + 5, exit_y - 5, door_width - 10, exit_height), border_radius=3)
    
    def get_interactable_object(self, player_rect: pygame.Rect):
        """Retourne l'objet avec lequel le joueur peut interagir."""
        for obj in self.all_objects:
            if obj.get("interactive", True):
                interaction_zone = obj["rect"].inflate(15, 15)
                if interaction_zone.colliderect(player_rect):
                    return obj
        return None
    
    def get_all_objects(self):
        """Retourne tous les objets pour la collision."""
        return self.all_objects
