# LifeSim/src/ui/components.py
"""
Composants UI réutilisables pour un design moderne.
"""

import pygame
import math
from src.ui.colors import *


class ProgressBar:
    """
    Barre de progression moderne avec gradient, animation et effets visuels.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 color_start: tuple, color_end: tuple = None,
                 bg_color: tuple = BG_PANEL, border_radius: int = 5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color_start = color_start
        self.color_end = color_end or darken(color_start, 0.3)
        self.bg_color = bg_color
        self.border_radius = border_radius
        
        # Animation
        self.displayed_value = 0.0
        self.target_value = 0.0
        self.animation_speed = 5.0  # Vitesse de l'animation
        
        # Effets
        self.show_glow = True
        self.pulse_timer = 0
    
    def set_value(self, value: float, max_value: float = 100.0):
        """Met à jour la valeur cible (0-1)."""
        self.target_value = max(0.0, min(1.0, value / max_value))
    
    def update(self, dt: float):
        """Met à jour l'animation."""
        # Animation fluide vers la valeur cible
        diff = self.target_value - self.displayed_value
        self.displayed_value += diff * self.animation_speed * dt
        
        # Mise à jour du timer de pulsation
        self.pulse_timer += dt * 3
    
    def draw(self, screen: pygame.Surface, icon: str = None, show_text: bool = True):
        """Dessine la barre de progression."""
        # Fond avec ombre
        shadow_rect = pygame.Rect(self.x + 2, self.y + 2, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=self.border_radius)
        
        # Fond de la barre
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, bg_rect, border_radius=self.border_radius)
        
        # Barre de progression avec gradient
        if self.displayed_value > 0.01:
            fill_width = int(self.width * self.displayed_value)
            if fill_width > 0:
                # Créer une surface pour le gradient
                gradient_surf = pygame.Surface((fill_width, self.height), pygame.SRCALPHA)
                
                for i in range(fill_width):
                    t = i / max(1, fill_width - 1)
                    color = lerp_color(self.color_start, self.color_end, t)
                    pygame.draw.line(gradient_surf, color, (i, 0), (i, self.height))
                
                # Appliquer le gradient
                screen.blit(gradient_surf, (self.x, self.y))
                
                # Effet de brillance en haut
                highlight_height = self.height // 3
                highlight_surf = pygame.Surface((fill_width, highlight_height), pygame.SRCALPHA)
                alpha = 60 + int(20 * math.sin(self.pulse_timer))
                highlight_surf.fill((255, 255, 255, alpha))
                screen.blit(highlight_surf, (self.x, self.y))
        
        # Bordure
        pygame.draw.rect(screen, BORDER_DEFAULT, bg_rect, 1, border_radius=self.border_radius)
        
        # Icône (si fournie)
        if icon and hasattr(self, '_font'):
            icon_surf = self._font.render(icon, True, TEXT_PRIMARY)
            screen.blit(icon_surf, (self.x - 25, self.y + (self.height - icon_surf.get_height()) // 2))
        
        # Texte de pourcentage
        if show_text:
            if not hasattr(self, '_font'):
                self._font = pygame.font.Font(None, 18)
            percent = int(self.displayed_value * 100)
            text = self._font.render(f"{percent}%", True, TEXT_PRIMARY)
            text_x = self.x + self.width + 5
            text_y = self.y + (self.height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))


class Panel:
    """
    Panneau moderne avec ombre, bordure et coins arrondis.
    Support du glassmorphism (fond semi-transparent flou).
    """
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 bg_color: tuple = BG_PANEL, border_color: tuple = BORDER_DEFAULT,
                 border_radius: int = 10, shadow: bool = True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.show_shadow = shadow
    
    def draw(self, screen: pygame.Surface):
        """Dessine le panneau."""
        # Ombre portée
        if self.show_shadow:
            shadow_offset = 4
            shadow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 80), (0, 0, self.width, self.height), 
                           border_radius=self.border_radius)
            screen.blit(shadow_surf, (self.x + shadow_offset, self.y + shadow_offset))
        
        # Fond du panneau
        if len(self.bg_color) == 4:  # Avec alpha
            panel_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, self.bg_color, (0, 0, self.width, self.height),
                           border_radius=self.border_radius)
            screen.blit(panel_surf, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height),
                           border_radius=self.border_radius)
        
        # Bordure
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height),
                        2, border_radius=self.border_radius)
        
        # Effet de lumière en haut (subtle highlight)
        highlight_height = 3
        highlight_surf = pygame.Surface((self.width - 4, highlight_height), pygame.SRCALPHA)
        highlight_surf.fill((255, 255, 255, 30))
        screen.blit(highlight_surf, (self.x + 2, self.y + 2))


class IconBadge:
    """
    Badge avec icône pour afficher des informations (argent, jour, météo).
    """
    
    def __init__(self, x: int, y: int, icon: str, color: tuple = ACCENT):
        self.x = x
        self.y = y
        self.icon = icon
        self.color = color
        self.font = None
        self.small_font = None
    
    def draw(self, screen: pygame.Surface, value: str):
        """Dessine le badge avec une valeur."""
        if self.font is None:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 20)
        
        # Icône
        icon_surf = self.font.render(self.icon, True, self.color)
        screen.blit(icon_surf, (self.x, self.y))
        
        # Valeur
        value_surf = self.small_font.render(str(value), True, TEXT_PRIMARY)
        screen.blit(value_surf, (self.x + icon_surf.get_width() + 5, self.y + 2))


class Tooltip:
    """
    Info-bulle contextuelle qui apparaît au survol.
    """
    
    def __init__(self):
        self.visible = False
        self.text = ""
        self.x = 0
        self.y = 0
        self.font = None
        self.padding = 8
    
    def show(self, x: int, y: int, text: str):
        """Affiche l'info-bulle."""
        self.visible = True
        self.x = x
        self.y = y
        self.text = text
    
    def hide(self):
        """Cache l'info-bulle."""
        self.visible = False
    
    def draw(self, screen: pygame.Surface):
        """Dessine l'info-bulle si visible."""
        if not self.visible or not self.text:
            return
        
        if self.font is None:
            self.font = pygame.font.Font(None, 18)
        
        # Calculer la taille
        text_surf = self.font.render(self.text, True, TEXT_PRIMARY)
        width = text_surf.get_width() + self.padding * 2
        height = text_surf.get_height() + self.padding * 2
        
        # Fond
        bg_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (0, 0, 0, 220), (0, 0, width, height), border_radius=5)
        screen.blit(bg_surf, (self.x, self.y - height - 5))
        
        # Bordure
        pygame.draw.rect(screen, BORDER_DEFAULT, (self.x, self.y - height - 5, width, height), 1, border_radius=5)
        
        # Texte
        screen.blit(text_surf, (self.x + self.padding, self.y - height - 5 + self.padding))


class AnimatedIcon:
    """
    Icône avec animation (rotation, pulsation, etc.)
    """
    
    def __init__(self, x: int, y: int, icon: str, color: tuple, 
                 animation_type: str = "pulse"):
        self.x = x
        self.y = y
        self.icon = icon
        self.base_color = color
        self.animation_type = animation_type
        self.timer = 0
        self.font = None
    
    def update(self, dt: float):
        """Met à jour l'animation."""
        self.timer += dt * 3
    
    def draw(self, screen: pygame.Surface):
        """Dessine l'icône animée."""
        if self.font is None:
            self.font = pygame.font.Font(None, 32)
        
        # Calculer l'effet selon le type d'animation
        if self.animation_type == "pulse":
            scale = 1.0 + 0.1 * math.sin(self.timer)
            alpha = 200 + int(55 * math.sin(self.timer))
        else:
            scale = 1.0
            alpha = 255
        
        # Dessiner l'icône
        color_with_alpha = (*self.base_color[:3], alpha)
        icon_surf = self.font.render(self.icon, True, self.base_color)
        
        # Appliquer le scale (simplifié - juste position offset)
        offset = int((1 - scale) * icon_surf.get_width() / 2)
        screen.blit(icon_surf, (self.x + offset, self.y + offset))
