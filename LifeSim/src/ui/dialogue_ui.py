# LifeSim/src/ui/dialogue_ui.py
"""
Système de dialogue moderne avec bulles stylisées et animations.
"""

import pygame
from src.ui.colors import *


class MessageBox:
    """
    Boîte de message moderne qui apparaît en bas de l'écran.
    Support des animations d'apparition/disparition.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configuration
        self.margin = 50
        self.height = 80
        self.width = screen_width - self.margin * 2
        self.x = self.margin
        self.y = screen_height - self.height - 60  # Au-dessus des hints
        
        # État
        self.message = ""
        self.visible = False
        self.alpha = 0
        self.target_alpha = 0
        
        # Animation
        self.animation_speed = 10
        
        # Police
        self.font = None
        self.small_font = None
    
    def show(self, message: str):
        """Affiche un message."""
        self.message = message
        self.visible = True
        self.target_alpha = 255
    
    def hide(self):
        """Cache le message."""
        self.target_alpha = 0
    
    def update(self, dt: float):
        """Met à jour l'animation."""
        # Animation d'alpha
        if self.alpha < self.target_alpha:
            self.alpha = min(255, self.alpha + self.animation_speed * dt * 255)
        elif self.alpha > self.target_alpha:
            self.alpha = max(0, self.alpha - self.animation_speed * dt * 255)
        
        # Cacher quand alpha = 0
        if self.alpha <= 0 and self.target_alpha == 0:
            self.visible = False
    
    def draw(self, screen: pygame.Surface):
        """Dessine la boîte de message."""
        if not self.visible and self.alpha <= 0:
            return
        
        if self.font is None:
            self.font = pygame.font.Font(None, 24)
        
        alpha = int(self.alpha)
        
        # Fond avec ombre
        shadow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, min(150, alpha // 2)), 
                        (4, 4, self.width - 4, self.height - 4), border_radius=15)
        screen.blit(shadow_surf, (self.x, self.y))
        
        # Fond principal
        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_color = (31, 41, 55, min(230, alpha))
        pygame.draw.rect(bg_surf, bg_color, (0, 0, self.width, self.height), border_radius=15)
        screen.blit(bg_surf, (self.x, self.y))
        
        # Bordure
        border_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        border_color = (99, 102, 241, alpha)  # Primary color
        pygame.draw.rect(border_surf, border_color, (0, 0, self.width, self.height), 2, border_radius=15)
        screen.blit(border_surf, (self.x, self.y))
        
        # Effet de lumière en haut
        highlight_surf = pygame.Surface((self.width - 4, 3), pygame.SRCALPHA)
        highlight_surf.fill((255, 255, 255, min(50, alpha // 5)))
        screen.blit(highlight_surf, (self.x + 2, self.y + 2))
        
        # Texte
        if self.message:
            text_alpha = min(255, alpha)
            text_color = (255, 255, 255)
            
            # Si le message est trop long, on le coupe
            if len(self.message) > 80:
                display_text = self.message[:77] + "..."
            else:
                display_text = self.message
            
            text_surf = self.font.render(display_text, True, text_color)
            text_x = self.x + (self.width - text_surf.get_width()) // 2
            text_y = self.y + (self.height - text_surf.get_height()) // 2
            
            # Appliquer l'alpha au texte
            text_with_alpha = text_surf.copy()
            text_with_alpha.set_alpha(text_alpha)
            screen.blit(text_with_alpha, (text_x, text_y))


class ContextMenu:
    """
    Menu contextuel moderne qui apparaît au-dessus des objets interactifs.
    """
    
    def __init__(self):
        self.font = None
        self.padding = 8
    
    def draw(self, screen: pygame.Surface, target_rect: pygame.Rect, text: str):
        """Dessine le menu contextuel au-dessus de la cible."""
        if self.font is None:
            self.font = pygame.font.Font(None, 20)
        
        # Calculer la taille
        text_surf = self.font.render(text, True, (255, 255, 255))
        width = text_surf.get_width() + self.padding * 2
        height = text_surf.get_height() + self.padding * 2
        
        # Position centrée au-dessus
        x = target_rect.centerx - width // 2
        y = target_rect.top - height - 10
        
        # Fond avec gradient
        bg_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (17, 24, 39, 220), (0, 0, width, height), border_radius=8)
        screen.blit(bg_surf, (x, y))
        
        # Bordure dorée
        pygame.draw.rect(screen, ACCENT, (x, y, width, height), 2, border_radius=8)
        
        # Petite flèche vers le bas
        arrow_points = [
            (target_rect.centerx - 6, y + height),
            (target_rect.centerx + 6, y + height),
            (target_rect.centerx, y + height + 6)
        ]
        pygame.draw.polygon(screen, (17, 24, 39), arrow_points)
        pygame.draw.lines(screen, ACCENT, False, [arrow_points[0], arrow_points[2], arrow_points[1]], 2)
        
        # Texte
        screen.blit(text_surf, (x + self.padding, y + self.padding))


class NPCDialogue:
    """
    Dialogue stylisé avec avatar du PNJ (pour les conversations plus longues).
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.width = 500
        self.height = 120
        self.x = (screen_width - self.width) // 2
        self.y = screen_height - self.height - 80
        
        self.visible = False
        self.npc_name = ""
        self.message = ""
        
        self.font = None
        self.name_font = None
    
    def show(self, npc_name: str, message: str):
        """Affiche un dialogue de PNJ."""
        self.visible = True
        self.npc_name = npc_name
        self.message = message
    
    def hide(self):
        """Cache le dialogue."""
        self.visible = False
    
    def draw(self, screen: pygame.Surface):
        """Dessine le dialogue du PNJ."""
        if not self.visible:
            return
        
        if self.font is None:
            self.font = pygame.font.Font(None, 22)
            self.name_font = pygame.font.Font(None, 26)
        
        # Fond principal
        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (31, 41, 55, 240), (0, 0, self.width, self.height), border_radius=12)
        screen.blit(bg_surf, (self.x, self.y))
        
        # Bordure
        pygame.draw.rect(screen, PRIMARY, (self.x, self.y, self.width, self.height), 2, border_radius=12)
        
        # Zone avatar (carré à gauche)
        avatar_size = 80
        avatar_x = self.x + 15
        avatar_y = self.y + (self.height - avatar_size) // 2
        pygame.draw.rect(screen, BG_PANEL_LIGHT, (avatar_x, avatar_y, avatar_size, avatar_size), border_radius=10)
        pygame.draw.rect(screen, BORDER_DEFAULT, (avatar_x, avatar_y, avatar_size, avatar_size), 2, border_radius=10)
        
        # Emoji placeholder pour l'avatar
        avatar_text = self.font.render("👤", True, TEXT_PRIMARY)
        screen.blit(avatar_text, (avatar_x + (avatar_size - avatar_text.get_width()) // 2,
                                   avatar_y + (avatar_size - avatar_text.get_height()) // 2))
        
        # Nom du PNJ
        name_surf = self.name_font.render(self.npc_name, True, ACCENT)
        screen.blit(name_surf, (avatar_x + avatar_size + 20, self.y + 15))
        
        # Message
        text_x = avatar_x + avatar_size + 20
        text_y = self.y + 45
        text_width = self.width - avatar_size - 50
        
        # Wrapping simple
        words = self.message.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            test_surf = self.font.render(test_line, True, TEXT_PRIMARY)
            if test_surf.get_width() <= text_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        
        # Afficher les lignes (max 2)
        for i, line in enumerate(lines[:2]):
            line_surf = self.font.render(line, True, TEXT_PRIMARY)
            screen.blit(line_surf, (text_x, text_y + i * 22))
