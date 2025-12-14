# LifeSim/src/ui/shop_ui.py
"""
Interface graphique moderne pour le magasin.
Affiche tous les articles disponibles avec leurs prix.
"""

import pygame
from src.ui.colors import *


class ShopUI:
    """
    Interface graphique du magasin affichant les articles disponibles.
    S'affiche automatiquement quand le joueur est dans la zone du shop.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configuration du panneau
        self.width = 320
        self.height = 280
        self.x = screen_width - self.width - 15
        self.y = 220  # En dessous du HUD
        
        # Polices
        self.font = None
        self.small_font = None
        self.title_font = None
        
        # Couleurs
        self.bg_color = (25, 30, 40, 240)
        self.border_color = (220, 180, 50)  # Or
        self.item_bg = (40, 45, 55)
        self.item_hover = (60, 65, 75)
        
        # Catégories avec couleurs
        self.category_colors = {
            "FOOD": (100, 200, 100),     # Vert
            "DRINK": (100, 150, 220),    # Bleu
            "GIFT": (220, 100, 180),     # Rose
        }
    
    def init_fonts(self):
        """Initialise les polices."""
        if self.font is None:
            self.font = pygame.font.Font(None, 20)
            self.small_font = pygame.font.Font(None, 16)
            self.title_font = pygame.font.Font(None, 26)
    
    def draw(self, screen: pygame.Surface, shop, player_money: int):
        """
        Dessine l'interface du magasin.
        
        Args:
            screen: Surface pygame
            shop: Instance du Shop avec stock_catalogue
            player_money: Argent actuel du joueur
        """
        self.init_fonts()
        
        # Fond avec ombre
        shadow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (4, 4, self.width - 4, self.height - 4), border_radius=12)
        screen.blit(shadow_surf, (self.x, self.y))
        
        # Fond principal
        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, self.bg_color, (0, 0, self.width, self.height), border_radius=12)
        screen.blit(bg_surf, (self.x, self.y))
        
        # Bordure dorée
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2, border_radius=12)
        
        # Effet de lumière en haut
        highlight_surf = pygame.Surface((self.width - 4, 3), pygame.SRCALPHA)
        highlight_surf.fill((255, 255, 255, 40))
        screen.blit(highlight_surf, (self.x + 2, self.y + 2))
        
        # Titre
        title = self.title_font.render("🏪 MAGASIN", True, self.border_color)
        screen.blit(title, (self.x + 15, self.y + 10))
        
        # Argent du joueur
        money_text = self.font.render(f"💰 {player_money} E", True, (250, 200, 50))
        screen.blit(money_text, (self.x + self.width - money_text.get_width() - 15, self.y + 12))
        
        # Ligne de séparation
        pygame.draw.line(screen, (60, 65, 75), 
                        (self.x + 10, self.y + 38), 
                        (self.x + self.width - 10, self.y + 38), 1)
        
        # Liste des articles
        item_y = self.y + 48
        item_height = 24
        
        for i, item in enumerate(shop.stock_catalogue):
            if item_y + item_height > self.y + self.height - 10:
                break  # Plus de place
            
            # Fond de l'item
            item_rect = pygame.Rect(self.x + 10, item_y, self.width - 20, item_height - 2)
            pygame.draw.rect(screen, self.item_bg, item_rect, border_radius=4)
            
            # Numéro de touche
            key_text = self.small_font.render(f"[{i + 1}]", True, self.border_color)
            screen.blit(key_text, (self.x + 15, item_y + 5))
            
            # Catégorie (point de couleur)
            cat_name = item.category.name if hasattr(item.category, 'name') else str(item.category)
            cat_color = self.category_colors.get(cat_name, (150, 150, 150))
            pygame.draw.circle(screen, cat_color, (self.x + 45, item_y + 11), 4)
            
            # Nom de l'item
            name_color = (255, 255, 255) if player_money >= item.price else (150, 100, 100)
            name_text = self.font.render(item.name, True, name_color)
            screen.blit(name_text, (self.x + 55, item_y + 4))
            
            # Prix
            price_color = (100, 255, 100) if player_money >= item.price else (255, 100, 100)
            price_text = self.small_font.render(f"{item.price} E", True, price_color)
            screen.blit(price_text, (self.x + self.width - price_text.get_width() - 15, item_y + 5))
            
            item_y += item_height
        
        # Instructions
        instructions = self.small_font.render("Appuyez sur [1-9] pour acheter", True, (150, 150, 160))
        screen.blit(instructions, (self.x + 15, self.y + self.height - 22))
    
    def draw_compact(self, screen: pygame.Surface, shop):
        """
        Dessine une version compacte du menu shop (pour le menu contextuel).
        """
        self.init_fonts()
        
        # Créer le texte des articles
        items_text = []
        for i, item in enumerate(shop.stock_catalogue[:6]):  # Max 6 items affichés
            items_text.append(f"[{i+1}] {item.name}: {item.price}E")
        
        return " | ".join(items_text[:3]) + "..."  # Résumé court
