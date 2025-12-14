# LifeSim/src/ui/inventory_ui.py
"""
Interface graphique pour l'inventaire du joueur.
Affiche les objets dans une grille avec possibilité de sélection.
"""

import pygame
from typing import Optional, List
from src.entities.player import Player
from src.entities.item import Item, ItemCategory


class InventoryUI:
    """
    Interface graphique pour afficher et gérer l'inventaire.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configuration de la fenêtre d'inventaire
        self.width = 400
        self.height = 350
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        # Grille d'inventaire
        self.cols = 5
        self.rows = 4
        self.cell_size = 60
        self.cell_margin = 8
        self.grid_start_x = self.x + 30
        self.grid_start_y = self.y + 60
        
        # État
        self.is_open = False
        self.selected_index = -1
        self.hovered_index = -1
        
        # Couleurs
        self.bg_color = (30, 30, 40, 230)
        self.border_color = (100, 100, 120)
        self.cell_color = (50, 50, 60)
        self.cell_hover_color = (70, 70, 90)
        self.cell_selected_color = (80, 120, 180)
        self.text_color = (255, 255, 255)
        self.title_color = (255, 215, 0)
        
        # Catégories
        self.category_colors = {
            ItemCategory.FOOD: (100, 200, 100),     # Vert
            ItemCategory.DRINK: (100, 150, 220),    # Bleu
            ItemCategory.GIFT: (220, 100, 180),     # Rose
            ItemCategory.TOOL: (180, 150, 100),     # Marron
        }
        
        # Police
        self.font = None
        self.small_font = None
    
    def init_fonts(self):
        """Initialise les polices (appelé après pygame.init)."""
        if self.font is None:
            self.font = pygame.font.Font(None, 28)
            self.small_font = pygame.font.Font(None, 20)
    
    def toggle(self):
        """Ouvre/ferme l'inventaire."""
        self.is_open = not self.is_open
        if not self.is_open:
            self.selected_index = -1
    
    def close(self):
        """Ferme l'inventaire."""
        self.is_open = False
        self.selected_index = -1
    
    def handle_event(self, event: pygame.event.Event, player: Player) -> Optional[str]:
        """
        Gère les événements de l'inventaire.
        Retourne une action si nécessaire.
        """
        if not self.is_open:
            return None
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered_index = self._get_cell_at_position(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                cell_index = self._get_cell_at_position(event.pos)
                if cell_index is not None and cell_index < len(player.inventory):
                    self.selected_index = cell_index
                    return "select"
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and self.selected_index >= 0:
                # Manger l'objet sélectionné
                if self.selected_index < len(player.inventory):
                    return "eat"
            elif event.key == pygame.K_ESCAPE:
                self.close()
                return "close"
        
        return None
    
    def _get_cell_at_position(self, pos: tuple) -> Optional[int]:
        """Retourne l'index de la cellule sous le curseur."""
        mx, my = pos
        
        for i in range(self.cols * self.rows):
            row = i // self.cols
            col = i % self.cols
            
            cell_x = self.grid_start_x + col * (self.cell_size + self.cell_margin)
            cell_y = self.grid_start_y + row * (self.cell_size + self.cell_margin)
            
            if cell_x <= mx <= cell_x + self.cell_size and cell_y <= my <= cell_y + self.cell_size:
                return i
        
        return None
    
    def draw(self, screen: pygame.Surface, player: Player):
        """Dessine l'interface d'inventaire."""
        if not self.is_open:
            return
        
        self.init_fonts()
        
        # Fond semi-transparent
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        screen.blit(overlay, (self.x, self.y))
        
        # Bordure
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 3, border_radius=10)
        
        # Titre
        title = self.font.render("🎒 INVENTAIRE", True, self.title_color)
        screen.blit(title, (self.x + 20, self.y + 15))
        
        # Argent
        money_text = self.small_font.render(f"💰 {player.stats.money} E", True, (255, 215, 0))
        screen.blit(money_text, (self.x + self.width - 80, self.y + 20))
        
        # Grille d'inventaire
        for i in range(self.cols * self.rows):
            row = i // self.cols
            col = i % self.cols
            
            cell_x = self.grid_start_x + col * (self.cell_size + self.cell_margin)
            cell_y = self.grid_start_y + row * (self.cell_size + self.cell_margin)
            
            # Couleur de la cellule
            if i == self.selected_index:
                color = self.cell_selected_color
            elif i == self.hovered_index:
                color = self.cell_hover_color
            else:
                color = self.cell_color
            
            # Dessiner la cellule
            pygame.draw.rect(screen, color, (cell_x, cell_y, self.cell_size, self.cell_size), border_radius=5)
            pygame.draw.rect(screen, self.border_color, (cell_x, cell_y, self.cell_size, self.cell_size), 1, border_radius=5)
            
            # Si un objet est présent
            if i < len(player.inventory):
                item = player.inventory[i]
                
                # Indicateur de catégorie
                cat_color = self.category_colors.get(item.category, (128, 128, 128))
                pygame.draw.rect(screen, cat_color, (cell_x, cell_y, self.cell_size, 4), border_radius=2)
                
                # Nom de l'objet (raccourci)
                short_name = item.name[:6] + "..." if len(item.name) > 8 else item.name
                item_text = self.small_font.render(short_name, True, self.text_color)
                text_x = cell_x + (self.cell_size - item_text.get_width()) // 2
                screen.blit(item_text, (text_x, cell_y + 25))
        
        # Info de l'objet sélectionné
        if 0 <= self.selected_index < len(player.inventory):
            self._draw_item_details(screen, player.inventory[self.selected_index])
        
        # Instructions
        instructions = self.small_font.render("[E] Manger | [Échap] Fermer", True, (180, 180, 180))
        screen.blit(instructions, (self.x + 20, self.y + self.height - 30))
    
    def _draw_item_details(self, screen: pygame.Surface, item: Item):
        """Affiche les détails de l'objet sélectionné."""
        detail_y = self.y + self.height - 80
        
        # Nom
        name_text = self.font.render(item.name, True, self.text_color)
        screen.blit(name_text, (self.x + 20, detail_y))
        
        # Effets
        effects = []
        if item.hunger_value > 0:
            effects.append(f"🍎 +{int(item.hunger_value)}")
        if item.energy_value > 0:
            effects.append(f"⚡ +{int(item.energy_value)}")
        if item.friendship_value > 0:
            effects.append(f"❤️ +{item.friendship_value}")
        
        effects_text = self.small_font.render("  ".join(effects), True, (180, 220, 180))
        screen.blit(effects_text, (self.x + 20, detail_y + 25))


class SkillsUI:
    """
    Interface pour afficher les compétences du joueur.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.width = 300
        self.height = 250
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        self.is_open = False
        
        # Couleurs
        self.bg_color = (30, 35, 50, 230)
        self.border_color = (80, 100, 140)
        self.bar_bg = (40, 40, 50)
        self.text_color = (255, 255, 255)
        
        self.skill_colors = {
            "Cuisine": (255, 150, 100),
            "Social": (255, 100, 150),
            "Travail": (100, 200, 255),
            "Forme": (100, 255, 150),
        }
        
        self.font = None
        self.small_font = None
    
    def init_fonts(self):
        if self.font is None:
            self.font = pygame.font.Font(None, 28)
            self.small_font = pygame.font.Font(None, 22)
    
    def toggle(self):
        self.is_open = not self.is_open
    
    def close(self):
        self.is_open = False
    
    def draw(self, screen: pygame.Surface, skill_system):
        """Dessine l'interface des compétences."""
        if not self.is_open or skill_system is None:
            return
        
        self.init_fonts()
        
        # Fond
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        screen.blit(overlay, (self.x, self.y))
        
        # Bordure
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 3, border_radius=10)
        
        # Titre
        title = self.font.render("📊 COMPÉTENCES", True, (255, 215, 0))
        screen.blit(title, (self.x + 20, self.y + 15))
        
        # Barre de compétences
        bar_y = self.y + 55
        for skill in skill_system.skills.values():
            color = self.skill_colors.get(skill.name, (150, 150, 150))
            
            # Nom et niveau
            name_text = self.small_font.render(f"{skill.name} Nv.{skill.level}", True, self.text_color)
            screen.blit(name_text, (self.x + 20, bar_y))
            
            # Barre de progression
            bar_width = 180
            bar_height = 15
            bar_x = self.x + 20
            progress_bar_y = bar_y + 22
            
            # Fond de la barre
            pygame.draw.rect(screen, self.bar_bg, (bar_x, progress_bar_y, bar_width, bar_height), border_radius=5)
            
            # Progression
            if skill.xp_to_next_level > 0:
                progress = skill.xp / skill.xp_to_next_level
                fill_width = int(bar_width * progress)
                if fill_width > 0:
                    pygame.draw.rect(screen, color, (bar_x, progress_bar_y, fill_width, bar_height), border_radius=5)
            
            # Bordure
            pygame.draw.rect(screen, self.border_color, (bar_x, progress_bar_y, bar_width, bar_height), 1, border_radius=5)
            
            # XP text
            xp_text = self.small_font.render(f"{skill.xp}/{skill.xp_to_next_level} XP", True, (180, 180, 180))
            screen.blit(xp_text, (bar_x + bar_width + 10, progress_bar_y))
            
            bar_y += 45
        
        # Instructions
        instructions = self.small_font.render("[Échap] Fermer", True, (150, 150, 150))
        screen.blit(instructions, (self.x + 20, self.y + self.height - 30))
