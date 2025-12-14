# LifeSim/src/ui/hud.py
"""
HUD (Heads-Up Display) moderne avec barres de statut animées,
informations du jeu et indicateurs visuels.
"""

import pygame
import math
from src.ui.colors import *
from src.ui.components import ProgressBar, Panel, IconBadge


class ModernHUD:
    """
    Interface principale affichant les statistiques du joueur.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configuration du panneau principal
        self.panel_x = 10
        self.panel_y = 10
        self.panel_width = 260
        self.panel_height = 140
        
        # Panneau de fond
        self.main_panel = Panel(
            self.panel_x, self.panel_y, 
            self.panel_width, self.panel_height,
            bg_color=(17, 24, 39, 220),
            border_color=BORDER_DEFAULT,
            border_radius=12
        )
        
        # Barres de progression
        bar_x = self.panel_x + 35
        bar_width = 150
        bar_height = 12
        bar_spacing = 22
        
        self.health_bar = ProgressBar(
            bar_x, self.panel_y + 35, bar_width, bar_height,
            color_start=HEALTH, color_end=darken(HEALTH, 0.3)
        )
        
        self.energy_bar = ProgressBar(
            bar_x, self.panel_y + 35 + bar_spacing, bar_width, bar_height,
            color_start=ENERGY, color_end=darken(ENERGY, 0.3)
        )
        
        self.hunger_bar = ProgressBar(
            bar_x, self.panel_y + 35 + bar_spacing * 2, bar_width, bar_height,
            color_start=HUNGER, color_end=darken(HUNGER, 0.3)
        )
        
        self.happiness_bar = ProgressBar(
            bar_x, self.panel_y + 35 + bar_spacing * 3, bar_width, bar_height,
            color_start=HAPPINESS, color_end=darken(HAPPINESS, 0.3)
        )
        
        # Polices
        self.font = None
        self.small_font = None
        self.icon_font = None
        
        # Timer pour animations
        self.timer = 0
        
        # Icônes avec leurs positions
        self.icons = {
            "health": ("❤️", HEALTH, self.panel_x + 12, self.panel_y + 33),
            "energy": ("⚡", ENERGY, self.panel_x + 12, self.panel_y + 33 + bar_spacing),
            "hunger": ("🍎", HUNGER, self.panel_x + 12, self.panel_y + 33 + bar_spacing * 2),
            "happiness": ("😊", HAPPINESS, self.panel_x + 12, self.panel_y + 33 + bar_spacing * 3),
        }
    
    def init_fonts(self):
        """Initialise les polices."""
        if self.font is None:
            self.font = pygame.font.Font(None, 22)
            self.small_font = pygame.font.Font(None, 18)
            self.icon_font = pygame.font.Font(None, 24)
    
    def update(self, dt: float, player_stats):
        """Met à jour les valeurs et animations."""
        self.timer += dt
        
        # Mettre à jour les barres
        self.health_bar.set_value(player_stats.health)
        self.energy_bar.set_value(player_stats.energy)
        self.hunger_bar.set_value(player_stats.hunger)
        self.happiness_bar.set_value(player_stats.happiness)
        
        # Animation des barres
        self.health_bar.update(dt)
        self.energy_bar.update(dt)
        self.hunger_bar.update(dt)
        self.happiness_bar.update(dt)
    
    def draw(self, screen: pygame.Surface, player, time_manager, event_system):
        """Dessine le HUD complet."""
        self.init_fonts()
        
        # Panneau principal
        self.main_panel.draw(screen)
        
        # Nom du joueur
        name_surf = self.font.render(f"🎮 {player.name}", True, ACCENT)
        screen.blit(name_surf, (self.panel_x + 12, self.panel_y + 12))
        
        # Argent (à droite du nom)
        money_surf = self.small_font.render(f"💰 {player.stats.money} E", True, MONEY)
        screen.blit(money_surf, (self.panel_x + self.panel_width - money_surf.get_width() - 12, 
                                  self.panel_y + 14))
        
        # Dessiner les icônes
        for icon_name, (icon, color, ix, iy) in self.icons.items():
            icon_surf = self.small_font.render(icon, True, color)
            screen.blit(icon_surf, (ix, iy))
        
        # Dessiner les barres de progression
        self.health_bar.draw(screen, show_text=True)
        self.energy_bar.draw(screen, show_text=True)
        self.hunger_bar.draw(screen, show_text=True)
        self.happiness_bar.draw(screen, show_text=True)
        
        # Panneau d'informations (bas du HUD)
        self._draw_info_bar(screen, time_manager, event_system)
    
    def _draw_info_bar(self, screen: pygame.Surface, time_manager, event_system):
        """Dessine la barre d'informations (temps, météo, contrôles)."""
        info_y = self.panel_y + self.panel_height + 8
        
        # Petit panneau pour les infos
        info_panel = Panel(
            self.panel_x, info_y,
            self.panel_width, 50,
            bg_color=(17, 24, 39, 200),
            border_radius=8
        )
        info_panel.draw(screen)
        
        # Jour et heure
        day_str = f"📅 Jour {time_manager.day}"
        time_str = f"🕒 {time_manager.get_time_string()}"
        weather_str = f"🌤️ {event_system.get_weather_string()}"
        
        day_surf = self.small_font.render(day_str, True, TEXT_PRIMARY)
        time_surf = self.small_font.render(time_str, True, TEXT_SECONDARY)
        weather_surf = self.small_font.render(weather_str, True, self._get_weather_color(event_system))
        
        screen.blit(day_surf, (self.panel_x + 10, info_y + 8))
        screen.blit(time_surf, (self.panel_x + 10 + day_surf.get_width() + 15, info_y + 8))
        screen.blit(weather_surf, (self.panel_x + 10, info_y + 28))
    
    def _get_weather_color(self, event_system) -> tuple:
        """Retourne la couleur selon la météo."""
        weather_colors = {
            "Ensoleillé": WEATHER_SUNNY,
            "Nuageux": WEATHER_CLOUDY,
            "Pluvieux": WEATHER_RAINY,
            "Orageux": WEATHER_STORMY,
        }
        return weather_colors.get(event_system.get_weather_string(), TEXT_SECONDARY)


class ControlsHint:
    """
    Affiche les raccourcis clavier disponibles en bas de l'écran.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = None
        
        # Contrôles principaux
        self.controls = [
            ("[I]", "Inventaire"),
            ("[K]", "Skills"),
            ("[M]", "Map"),
            ("[T]", "Parler"),
            ("[G]", "Cadeau"),
            ("[E]", "Manger"),
        ]
    
    def draw(self, screen: pygame.Surface):
        """Dessine les hints de contrôles."""
        if self.font is None:
            self.font = pygame.font.Font(None, 18)
        
        # Position en bas de l'écran
        y = self.screen_height - 30
        
        # Fond semi-transparent
        bg_height = 25
        bg_surf = pygame.Surface((self.screen_width, bg_height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 150))
        screen.blit(bg_surf, (0, y - 5))
        
        # Dessiner les contrôles
        x = 20
        for key, action in self.controls:
            # Touche
            key_surf = self.font.render(key, True, ACCENT)
            screen.blit(key_surf, (x, y))
            x += key_surf.get_width() + 3
            
            # Action
            action_surf = self.font.render(action, True, TEXT_SECONDARY)
            screen.blit(action_surf, (x, y))
            x += action_surf.get_width() + 20


class QuestIndicator:
    """
    Affiche la quête active de manière stylisée.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = None
    
    def draw(self, screen: pygame.Surface, quest_text: str):
        """Dessine l'indicateur de quête."""
        if not quest_text:
            return
        
        if self.font is None:
            self.font = pygame.font.Font(None, 20)
        
        # Position en haut à droite
        margin = 10
        padding = 10
        
        # Calculer la taille
        text_surf = self.font.render(f"📜 {quest_text}", True, TEXT_PRIMARY)
        width = text_surf.get_width() + padding * 2
        height = text_surf.get_height() + padding * 2
        
        x = self.screen_width - width - margin
        y = margin
        
        # Fond avec style "parchemin"
        panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (45, 35, 25, 230), (0, 0, width, height), border_radius=8)
        screen.blit(panel_surf, (x, y))
        
        # Bordure dorée
        pygame.draw.rect(screen, ACCENT, (x, y, width, height), 2, border_radius=8)
        
        # Texte
        screen.blit(text_surf, (x + padding, y + padding))
