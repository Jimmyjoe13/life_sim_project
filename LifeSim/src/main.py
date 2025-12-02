import sys
import os

# --- PATH HACK ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import pygame
from src.core.settings import *
from src.core.asset_manager import AssetManager  # <--- NOUVEAU
from src.entities.player import Player
from src.entities.item import create_apple
from src.entities.shop import Shop
from src.core.save_manager import SaveManager # <--- Nouveau
from src.entities.workplace import Workplace

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        # 1. CHARGEMENT DES ASSETS
        self.assets = AssetManager.get()
        self.assets.load_images()

        # 2. SETUP JOUEUR
        self.player = Player(name="Saïna", money=STARTING_MONEY)
        self.player.add_item(create_apple())
        # On injecte l'image
        self.player.set_sprite(self.assets.get_image("player"))

        # 3. SETUP SHOP
        self.shop = Shop(600, 100)
        self.shop.set_sprite(self.assets.get_image("shop"))
        
        self.is_running = True
        self.move_intent = (0, 0)
        self.last_message = ""
        self.message_timer = 0
        self.shop.set_sprite(self.assets.get_image("shop"))

        # 4. SETUP WORKPLACE (A gauche, en bas)
        self.workplace = Workplace(100, 400)
        self.workplace.set_sprite(self.assets.get_image("office"))
        
        # --- SYSTEME DE SAUVEGARDE ---
        self.save_manager = SaveManager()
        
        self.is_running = True

    def handle_events(self):
        # On utilise self.player.rect pour la collision
        in_shop_zone = self.shop.check_collision(self.player.rect)
        in_work_zone = self.workplace.check_collision(self.player.rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.player.eat_item(0)

                if in_shop_zone:
                    if event.key == pygame.K_1:
                        print(f"💰 Avant achat : {self.player.stats.money}") # DEBUG
                        self.last_message = self.shop.try_buy_item(self.player, 0)
                        print(f"💸 Après achat : {self.player.stats.money}") # DEBUG
                        self.message_timer = 120
                    elif event.key == pygame.K_2:
                        self.last_message = self.shop.try_buy_item(self.player, 1)
                        self.message_timer = 120

                        # --- TRAVAIL ---
                if in_work_zone:
                    if event.key == pygame.K_SPACE:
                        self.last_message = self.workplace.work(self.player)
                        self.message_timer = 120

                # --- SAUVEGARDE / CHARGEMENT ---
                if event.key == pygame.K_F5:
                    if self.save_manager.save(self.player):
                        self.last_message = "Partie Sauvegardee !"
                        self.message_timer = 120

                if event.key == pygame.K_F9:
                    if self.save_manager.load(self.player):
                        self.last_message = "Partie Chargee !"
                        self.message_timer = 120

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_q]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_z]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
        
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        self.move_intent = (dx, dy)

    def update(self, dt):
        dx, dy = self.move_intent
        self.player.move(dx, dy, dt)
        self.player.update(dt, DECAY_HUNGER, DECAY_ENERGY)
        
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.last_message = ""

    def draw(self):
        # Fond vert (Herbe) au lieu de noir
        self.screen.fill((50, 160, 80))

        # Dessiner le Bureau
        if self.workplace.sprite:
            self.screen.blit(self.workplace.sprite, self.workplace.rect)
        
        # 1. Dessiner le Shop (Image)
        if self.shop.sprite:
            self.screen.blit(self.shop.sprite, self.shop.rect)
        else:
            pygame.draw.rect(self.screen, (255, 215, 0), self.shop.rect)

        # 2. Dessiner le Joueur (Image)
        if self.player.sprite:
            # Petite ombre sous le joueur pour le style
            shadow_pos = (self.player.rect.centerx - 10, self.player.rect.bottom - 5)
            pygame.draw.ellipse(self.screen, (30, 80, 30), (shadow_pos[0], shadow_pos[1], 20, 8))
            
            self.screen.blit(self.player.sprite, self.player.rect)
        else:
            pygame.draw.rect(self.screen, (0, 0, 255), (self.player.position[0], self.player.position[1], 32, 32))
        
        # 3. UI
        self.draw_ui()
        
        pygame.display.flip()

    def draw_ui(self):
        stats = self.player.stats
        
        # Panneau semi-transparent pour les stats
        panel = pygame.Surface((250, 150))
        panel.set_alpha(150)
        panel.fill((0, 0, 0))
        self.screen.blit(panel, (5, 5))

        infos = [
            f"Nom: {self.player.name}",
            f"Santé: {int(stats.health)}%",
            f"Faim: {int(stats.hunger)}%",
            f"Énergie: {int(stats.energy)}%",
            f"Argent: {stats.money} E",
            "--- Inventaire ---"
        ]
        
        if not self.player.inventory:
            infos.append("(Vide)")
        else:
            for item in self.player.inventory[:3]:
                infos.append(f"- {item.name}")

        for i, line in enumerate(infos):
            color = WHITE
            if "Faim" in line and stats.hunger < 20: color = (255, 100, 100)
            text_surf = self.font.render(line, True, color)
            self.screen.blit(text_surf, (10, 10 + i * 20))

        if self.last_message:
            msg_surf = self.font.render(self.last_message, True, (255, 255, 0))
            self.screen.blit(msg_surf, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80))

        if self.shop.check_collision(self.player.rect):
            shop_text = self.font.render("[1] Pomme(10)  [2] Café(25)", True, (255, 255, 255))
            pygame.draw.rect(self.screen, (0,0,0), (self.shop.rect.x, self.shop.rect.y - 30, 200, 25))
            self.screen.blit(shop_text, (self.shop.rect.x + 5, self.shop.rect.y - 30))

        # Affichage Menu Travail
        if self.workplace.check_collision(self.player.rect):
            work_text = self.font.render("[ESPACE] Travailler (+50€ / -20 Énergie)", True, (200, 200, 255))
            # Fond noir pour lisibilité
            bg_rect = pygame.Rect(self.workplace.rect.x - 20, self.workplace.rect.y - 30, 300, 25)
            pygame.draw.rect(self.screen, (0,0,0), bg_rect)
            self.screen.blit(work_text, (self.workplace.rect.x, self.workplace.rect.y - 30))

    def run(self):
        while self.is_running:
            dt = self.clock.tick(FPS) / 1000.0 
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
