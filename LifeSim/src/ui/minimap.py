# LifeSim/src/ui/minimap.py
"""
Mini-carte affichant une vue réduite du monde.
"""

import pygame
from src.ui.colors import *
from src.core.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MiniMap:
    """
    Affiche une mini-carte dans le coin supérieur droit.
    Montre la position du joueur, des PNJ et des bâtiments.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configuration
        self.size = 120
        self.margin = 10
        self.x = screen_width - self.size - self.margin
        self.y = self.margin
        
        # Échelle de la mini-carte par rapport au monde
        self.scale_x = self.size / screen_width
        self.scale_y = self.size / screen_height
        
        # Couleurs des éléments
        self.colors = {
            "player": (96, 165, 250),      # Bleu joueur
            "npc": (74, 222, 128),          # Vert PNJ
            "shop": (250, 204, 21),         # Or magasin
            "house": (239, 68, 68),         # Rouge maison
            "workplace": (139, 92, 246),    # Violet bureau
            "grass": (34, 197, 94),         # Vert herbe (fond)
            "path": (156, 163, 175),        # Gris chemin
        }
        
        # État
        self.visible = True
    
    def toggle(self):
        """Active/désactive la mini-carte."""
        self.visible = not self.visible
    
    def world_to_minimap(self, world_x: int, world_y: int) -> tuple:
        """Convertit des coordonnées monde en coordonnées mini-carte."""
        mini_x = self.x + int(world_x * self.scale_x)
        mini_y = self.y + int(world_y * self.scale_y)
        return (mini_x, mini_y)
    
    def draw(self, screen: pygame.Surface, player, npcs, buildings: dict):
        """
        Dessine la mini-carte.
        
        Args:
            screen: Surface Pygame
            player: Objet joueur
            npcs: Liste des PNJ
            buildings: Dict avec les bâtiments {"shop": rect, "house": rect, "workplace": rect}
        """
        if not self.visible:
            return
        
        # Fond de la mini-carte avec ombre
        shadow_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), (4, 4, self.size - 4, self.size - 4), border_radius=8)
        screen.blit(shadow_surf, (self.x, self.y))
        
        # Fond principal (herbe)
        bg_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (*self.colors["grass"], 200), (0, 0, self.size, self.size), border_radius=8)
        screen.blit(bg_surf, (self.x, self.y))
        
        # Dessiner les bâtiments
        for building_type, rect in buildings.items():
            if rect and building_type in self.colors:
                bx, by = self.world_to_minimap(rect.x, rect.y)
                bw = max(6, int(rect.width * self.scale_x))
                bh = max(6, int(rect.height * self.scale_y))
                
                # Garder dans les limites de la mini-carte
                bx = max(self.x, min(self.x + self.size - bw, bx))
                by = max(self.y, min(self.y + self.size - bh, by))
                
                color = self.colors.get(building_type, (100, 100, 100))
                pygame.draw.rect(screen, color, (bx, by, bw, bh), border_radius=2)
        
        # Dessiner les PNJ
        for npc in npcs:
            if hasattr(npc, 'rect') and npc.rect:
                nx, ny = self.world_to_minimap(npc.rect.centerx, npc.rect.centery)
                # Garder dans les limites
                nx = max(self.x + 3, min(self.x + self.size - 3, nx))
                ny = max(self.y + 3, min(self.y + self.size - 3, ny))
                pygame.draw.circle(screen, self.colors["npc"], (nx, ny), 3)
        
        # Dessiner le joueur (plus visible)
        if hasattr(player, 'rect') and player.rect:
            px, py = self.world_to_minimap(player.rect.centerx, player.rect.centery)
            # Garder dans les limites
            px = max(self.x + 4, min(self.x + self.size - 4, px))
            py = max(self.y + 4, min(self.y + self.size - 4, py))
            
            # Effet de pulsation pour le joueur
            pygame.draw.circle(screen, (255, 255, 255), (px, py), 6)
            pygame.draw.circle(screen, self.colors["player"], (px, py), 4)
        
        # Bordure
        pygame.draw.rect(screen, BORDER_DEFAULT, (self.x, self.y, self.size, self.size), 2, border_radius=8)
        
        # Label "MAP"
        font = pygame.font.Font(None, 14)
        label = font.render("MAP", True, TEXT_SECONDARY)
        screen.blit(label, (self.x + 5, self.y + 5))
        
        # Légende (petite)
        self._draw_legend(screen)
    
    def _draw_legend(self, screen: pygame.Surface):
        """Dessine une petite légende sous la mini-carte."""
        legend_y = self.y + self.size + 5
        font = pygame.font.Font(None, 12)
        
        legends = [
            (self.colors["player"], "Vous"),
            (self.colors["shop"], "Shop"),
            (self.colors["house"], "Maison"),
        ]
        
        x = self.x
        for color, name in legends:
            # Point de couleur
            pygame.draw.circle(screen, color, (x + 4, legend_y + 6), 3)
            # Texte
            text = font.render(name, True, TEXT_SECONDARY)
            screen.blit(text, (x + 10, legend_y + 2))
            x += text.get_width() + 18
