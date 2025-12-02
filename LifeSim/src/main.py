# src/main.py
import sys
import os

# --- PATH HACK ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import pygame
from src.core.settings import *
from src.core.asset_manager import AssetManager
from src.entities.player import Player
from src.entities.item import create_apple
from src.entities.shop import Shop
from src.core.save_manager import SaveManager
from src.entities.workplace import Workplace
from src.entities.npc import NPC
from src.entities.house import House  # <--- IMPORT DE LA MAISON

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        # 1. ASSETS
        self.assets = AssetManager.get()
        self.assets.load_images()

        # 2. JOUEUR
        self.player = Player(name="Saïna", money=STARTING_MONEY)
        self.player.add_item(create_apple())
        self.player.set_sprite(self.assets.get_image("player"))

        # 3. MONDE EXTÉRIEUR
        self.shop = Shop(600, 100)
        self.shop.set_sprite(self.assets.get_image("shop"))
        
        self.workplace = Workplace(100, 400)
        self.workplace.set_sprite(self.assets.get_image("office"))
        
        # 4. MAISON
        self.house = House(300, 50)
        self.house.set_sprites(self.assets.get_image("house"), self.assets.get_image("bed"))

        # 5. PNJS
        self.npcs = []
        
        bob = NPC("Bob", 300, 200, [
            "Belle journée pour coder !",
            "J'ai entendu dire que le café au Shop est excellent.",
            "Il faut travailler dur au bureau pour survivre ici.",
            "Ta nouvelle maison a l'air confortable !"
        ])
        bob.set_sprite(self.assets.get_image("npc_villager"))
        self.npcs.append(bob)

        alice = NPC("Alice", 500, 500, [
            "Fais attention à ton énergie.",
            "J'adore me promener sur ce fond vert.",
            "Si tu es fatigué, rentre chez toi dormir."
        ])
        alice.set_sprite(self.assets.get_image("npc_villager"))
        self.npcs.append(alice)

        # 6. SYSTÈME ET ETAT
        self.save_manager = SaveManager()
        self.location = "world"  # "world" ou "house"
        
        self.is_running = True
        self.move_intent = (0, 0)
        self.last_message = ""
        self.message_timer = 0

    def switch_location(self, new_location):
        """Gère la transition entre l'extérieur et l'intérieur"""
        if new_location == "house":
            self.location = "house"
            # On place le joueur au centre de la pièce
            self.player.position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120]
            self.last_message = "Maison douce maison..."
            self.message_timer = 120
            
        elif new_location == "world":
            self.location = "world"
            # On replace le joueur devant la porte
            self.player.position = list(self.house.entry_point)

    def handle_events(self):
        keys = pygame.key.get_pressed()
        
        # --- LOGIQUE DE SORTIE DE MAISON (CONTINUE) ---
        if self.location == "house":
            # Si le joueur va trop bas dans la maison, il sort
            if self.player.position[1] > SCREEN_HEIGHT - 40:
                self.switch_location("world")

        # --- DÉTECTIONS PRÉLIMINAIRES ---
        in_shop_zone = False
        in_work_zone = False
        can_enter_house = False
        can_sleep = False
        nearby_npc = None

        if self.location == "world":
            in_shop_zone = self.shop.check_collision(self.player.rect)
            in_work_zone = self.workplace.check_collision(self.player.rect)
            can_enter_house = self.house.check_entry(self.player.rect)
            
            for npc in self.npcs:
                if npc.check_collision(self.player.rect):
                    nearby_npc = npc
                    break
        
        elif self.location == "house":
            can_sleep = self.house.check_sleep(self.player.rect)

        # --- BOUCLE D'ÉVÉNEMENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            if event.type == pygame.KEYDOWN:
                # Manger (Possible partout)
                if event.key == pygame.K_e:
                    self.player.eat_item(0)

                # --- ACTIONS DU MONDE ---
                if self.location == "world":
                    # Shop
                    if in_shop_zone:
                        if event.key == pygame.K_1:
                            self.last_message = self.shop.try_buy_item(self.player, 0)
                            self.message_timer = 120
                        elif event.key == pygame.K_2:
                            self.last_message = self.shop.try_buy_item(self.player, 1)
                            self.message_timer = 120

                    # Travail
                    if in_work_zone and event.key == pygame.K_SPACE:
                        self.last_message = self.workplace.work(self.player)
                        self.message_timer = 120

                    # PNJ
                    if nearby_npc and event.key == pygame.K_t:
                        self.last_message = nearby_npc.talk()
                        self.message_timer = 180
                    
                    # Entrer Maison
                    if can_enter_house and event.key == pygame.K_SPACE:
                        self.switch_location("house")

                # --- ACTIONS DE LA MAISON ---
                elif self.location == "house":
                    # Dormir
                    if can_sleep and event.key == pygame.K_SPACE:
                        self.player.stats.energy = 100
                        self.player.stats.health += 10
                        self.last_message = "Zzz... Tu te sens reposé !"
                        self.message_timer = 120

                # --- ACTIONS GLOBALES ---
                if event.key == pygame.K_F5:
                    if self.save_manager.save(self.player):
                        self.last_message = "Partie Sauvegardee !"
                        self.message_timer = 120
                if event.key == pygame.K_F9:
                    if self.save_manager.load(self.player):
                        self.last_message = "Partie Chargee !"
                        self.message_timer = 120

        # --- MOUVEMENT ---
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
        self.player.move(*self.move_intent, dt)
        self.player.update(dt, DECAY_HUNGER, DECAY_ENERGY)
        
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.last_message = ""

    def draw(self):
        # 1. RENDU DU DÉCOR (Selon le lieu)
        if self.location == "world":
            self.screen.fill((50, 160, 80)) # Vert Herbe
            
            if self.house.sprite: self.screen.blit(self.house.sprite, self.house.rect)
            if self.workplace.sprite: self.screen.blit(self.workplace.sprite, self.workplace.rect)
            if self.shop.sprite: self.screen.blit(self.shop.sprite, self.shop.rect)

            # PNJs (Uniquement dehors)
            for npc in self.npcs:
                if npc.sprite:
                    shadow_pos = (npc.rect.centerx - 10, npc.rect.bottom - 5)
                    pygame.draw.ellipse(self.screen, (30, 80, 30), (shadow_pos[0], shadow_pos[1], 20, 8))
                    self.screen.blit(npc.sprite, npc.rect)
                    
                    # Nom
                    name_surf = self.font.render(npc.name, True, (200, 255, 200))
                    text_x = npc.rect.centerx - (name_surf.get_width() // 2)
                    self.screen.blit(name_surf, (text_x, npc.rect.top - 20))

        elif self.location == "house":
            self.screen.fill((210, 180, 140)) # Beige Parquet/Bois
            
            # Tapis déco
            pygame.draw.rect(self.screen, (100, 50, 50), (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT - 100, 100, 60))
            
            # Lit
            if self.house.bed_sprite:
                self.screen.blit(self.house.bed_sprite, self.house.bed_rect)

        # 2. JOUEUR (Toujours visible)
        if self.player.sprite:
            shadow_pos = (self.player.rect.centerx - 10, self.player.rect.bottom - 5)
            pygame.draw.ellipse(self.screen, (30, 80, 30), (shadow_pos[0], shadow_pos[1], 20, 8))
            self.screen.blit(self.player.sprite, self.player.rect)
        
        # 3. UI
        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        stats = self.player.stats
        
        # Panel Stats
        panel = pygame.Surface((250, 150))
        panel.set_alpha(150)
        panel.fill((0, 0, 0))
        self.screen.blit(panel, (5, 5))

        infos = [
            f"Nom: {self.player.name}",
            f"Vie: {int(stats.health)}%  Nrj: {int(stats.energy)}%",
            f"Faim: {int(stats.hunger)}%  Argent: {stats.money} E",
            "--- Inventaire ---"
        ]
        
        if not self.player.inventory: infos.append("(Vide)")
        else:
            for item in self.player.inventory[:3]: infos.append(f"- {item.name}")

        for i, line in enumerate(infos):
            color = WHITE
            if "Faim" in line and stats.hunger < 20: color = (255, 100, 100)
            text_surf = self.font.render(line, True, color)
            self.screen.blit(text_surf, (10, 10 + i * 20))

        # Bulle Dialogue / Message
        if self.last_message:
            box_rect = pygame.Rect(100, SCREEN_HEIGHT - 100, SCREEN_WIDTH - 200, 80)
            pygame.draw.rect(self.screen, (0, 0, 0), box_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 2)
            msg_surf = self.font.render(self.last_message, True, WHITE)
            text_rect = msg_surf.get_rect(center=box_rect.center)
            self.screen.blit(msg_surf, text_rect)

        # --- MENUS CONTEXTUELS (DYNAMIQUE SELON LE LIEU) ---
        if self.location == "world":
            if self.shop.check_collision(self.player.rect):
                self.draw_context_menu(self.shop.rect, "[1] Pomme(10) [2] Café(25)")
            
            if self.workplace.check_collision(self.player.rect):
                self.draw_context_menu(self.workplace.rect, "[ESPACE] Travailler")

            if self.house.check_entry(self.player.rect):
                self.draw_context_menu(self.house.rect, "[ESPACE] Entrer")

            for npc in self.npcs:
                if npc.check_collision(self.player.rect):
                    self.draw_context_menu(npc.rect, f"[T] Parler à {npc.name}")
                    
        elif self.location == "house":
            if self.house.check_sleep(self.player.rect):
                self.draw_context_menu(self.house.bed_rect, "[ESPACE] Dormir")
            
            # Indicateur de sortie
            if self.player.position[1] > SCREEN_HEIGHT - 100:
                out_rect = pygame.Rect(SCREEN_WIDTH//2, SCREEN_HEIGHT-40, 10, 10)
                self.draw_context_menu(out_rect, "Sortir")

    def draw_context_menu(self, target_rect, text):
        surf = self.font.render(text, True, (255, 255, 0))
        bg = pygame.Rect(target_rect.centerx - surf.get_width()//2 - 5, target_rect.top - 40, surf.get_width() + 10, 25)
        pygame.draw.rect(self.screen, (0,0,0), bg)
        self.screen.blit(surf, (bg.x + 5, bg.y))

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