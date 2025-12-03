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
from src.entities.house import House
from src.core.time_manager import TimeManager
from src.core.world_map import WorldMap
from src.entities.quest import Quest
from src.systems.relationship_system import RelationshipSystem

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

        # MONDE (CARTE)
        self.world_map = WorldMap()

        # 2. JOUEUR
        self.player = Player(name="Saïna", money=STARTING_MONEY)
        self.player.add_item(create_apple())
        self.player.set_sprite(self.assets.get_image("player"))
        
        # 3. SYSTÈMES (ON LES INITIALISE ICI MAINTENANT !)
        # C'est important qu'ils soient là AVANT les PNJ
        self.save_manager = SaveManager()
        self.relationship_system = RelationshipSystem() # <--- IL EST ICI !
        self.time_manager = TimeManager()

        # 4. MONDE EXTÉRIEUR
        self.shop = Shop(600, 100)
        self.shop.set_sprite(self.assets.get_image("shop"))
        
        self.workplace = Workplace(100, 400)
        self.workplace.set_sprite(self.assets.get_image("office"))
        
        # MAISON
        self.house = House(300, 50)
        self.house.set_outdoor_sprite(self.assets.get_image("house"))
        self.house.setup_interior(self.assets)

        # 5. PNJS (MAINTENANT ÇA VA MARCHER)
        self.npcs = []
        
        # Quête de Bob
        quest_bob = Quest(
            title="Livraison Fruitée",
            description="Apporte une Pomme Rouge à Bob",
            target_item="Pomme Rouge",
            reward_amount=50
        )

        # Bob peut maintenant recevoir self.relationship_system car il existe déjà !
        bob = NPC("Bob", 300, 200, [
            "Quelle belle journée !",
            "J'ai vraiment très faim...",
        ], quest=quest_bob, relationship_manager=self.relationship_system)

        bob.set_sprite(self.assets.get_image("npc_villager"))
        self.npcs.append(bob)

        alice = NPC("Alice", 500, 500, [
            "Fais attention à ton énergie.",
            "J'adore me promener sur ce fond vert.",
            "Si tu es fatigué, rentre chez toi dormir."
        ], relationship_manager=self.relationship_system)
        
        alice.set_sprite(self.assets.get_image("npc_villager"))
        self.npcs.append(alice)

        # 6. ETAT DU JEU
        self.location = "world"
        self.is_running = True
        self.move_intent = (0, 0)
        self.last_message = ""
        self.message_timer = 0
        
        # (Le time_manager est déjà géré au point 3, tu peux nettoyer si tu as des doublons)
        self.night_filter = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.night_filter.set_alpha(0)

    def switch_location(self, new_location):
        """Gère la transition entre l'extérieur et l'intérieur"""
        if new_location == "house":
            self.location = "house"
            # On place le joueur au centre de la pièce (Entrée)
            self.player.position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120]
            self.last_message = "Maison douce maison..."
            self.message_timer = 120
            
        elif new_location == "world":
            self.location = "world"
            # On replace le joueur devant la porte extérieure
            self.player.position = list(self.house.entry_point)

    def handle_events(self):
        keys = pygame.key.get_pressed()
        
        # --- LOGIQUE DE SORTIE DE MAISON ---
        if self.location == "house":
            # Si le joueur va trop bas dans la maison, il sort
            if self.player.position[1] > SCREEN_HEIGHT - 40:
                self.switch_location("world")

        # --- DÉTECTIONS PRÉLIMINAIRES ---
        in_shop_zone = False
        in_work_zone = False
        can_enter_house = False
        nearby_npc = None
        interact_obj = None # L'objet touché dans la maison

        if self.location == "world":
            in_shop_zone = self.shop.check_collision(self.player.rect)
            in_work_zone = self.workplace.check_collision(self.player.rect)
            can_enter_house = self.house.check_entry(self.player.rect)
            for npc in self.npcs:
                if npc.check_collision(self.player.rect):
                    nearby_npc = npc
                    break
        
        elif self.location == "house":
            # On demande à la maison quel meuble on touche
            interact_obj = self.house.get_interactable_object(self.player.rect)

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
                    if in_shop_zone:
                        if event.key == pygame.K_1:
                            self.last_message = self.shop.try_buy_item(self.player, 0)
                            self.message_timer = 120
                        elif event.key == pygame.K_2:
                            self.last_message = self.shop.try_buy_item(self.player, 1)
                            self.message_timer = 120

                    if in_work_zone and event.key == pygame.K_SPACE:
                        self.last_message = self.workplace.work(self.player)
                        self.message_timer = 120

                    if nearby_npc and event.key == pygame.K_t:
                        # 1. On récupère la réponse du PNJ
                        response = nearby_npc.talk(self.player)
                        
                        # 2. On augmente l'amitié (+2 points par discussion)
                        # On ne gagne de l'amitié que si ce n'est pas une quête active bloquante
                        # (Optionnel, ici on simplifie : parler = aimer)
                        self.relationship_system.modify_friendship(nearby_npc.name, 2)
                        
                        # 3. On récupère le nouveau statut pour l'afficher
                        new_score = self.relationship_system.get_friendship(nearby_npc.name)
                        status = self.relationship_system.get_relationship_status(nearby_npc.name)
                        
                        self.last_message = f"{response} (Amitié: {new_score} - {status})"
                        self.message_timer = 180
                    
                    if can_enter_house and event.key == pygame.K_SPACE:
                        self.switch_location("house")

                # --- ACTIONS DE LA MAISON (NOUVEAU) ---
                elif self.location == "house" and interact_obj:
                    obj_type = interact_obj["type"]
                    
                    if event.key == pygame.K_SPACE:
                        if obj_type == "bed":
                            self.player.stats.energy = 100
                            self.player.stats.health += 10
                            self.last_message = "Zzz... Une bonne nuit de sommeil !"
                            self.message_timer = 120
                        elif obj_type == "kitchen" or obj_type == "fridge":
                            self.last_message = "Le frigo est vide... Il faut aller au Shop !"
                            self.message_timer = 120
                        elif obj_type == "toilet":
                            self.last_message = "Occupé..."
                            self.message_timer = 60
                        elif obj_type == "sofa":
                            self.last_message = "Petite pause Netflix."
                            self.player.stats.energy += 5 # Petit bonus repos
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
        # Mise à jour du temps
        self.time_manager.update(dt, TIME_SPEED)
        
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.last_message = ""

    def draw_house_interior(self):
        """Dessine l'intérieur détaillé de la maison"""
        # 1. Sols
        # Parquet général (Salon/Chambre)
        pygame.draw.rect(self.screen, (210, 180, 140), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        # Carrelage Cuisine (Bas Gauche) - Gris clair
        pygame.draw.rect(self.screen, (200, 200, 200), (0, SCREEN_HEIGHT//2, SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        # Carrelage Salle de bain (Haut Droite) - Bleu très clair
        pygame.draw.rect(self.screen, (220, 220, 255), (SCREEN_WIDTH//2, 0, SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

        # 2. Murs de séparation (Lignes grises)
        # Verticale milieu
        pygame.draw.line(self.screen, (100, 100, 100), (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT-100), 8)
        # Horizontale milieu
        pygame.draw.line(self.screen, (100, 100, 100), (0, SCREEN_HEIGHT//2), (SCREEN_WIDTH, SCREEN_HEIGHT//2), 8)

        # 3. Affichage des objets
        for obj in self.house.interior_objects:
            self.screen.blit(obj["sprite"], obj["rect"])

    def draw(self):
        # 1. RENDU DU DÉCOR (Selon le lieu)
        if self.location == "world":
            # self.screen.fill((50, 160, 80)) # Vert Herbe
            # AFFICHE LA CARTE EN PREMIER (C'est le sol)
            self.world_map.draw(self.screen, self.assets)

            if self.house.sprite: self.screen.blit(self.house.sprite, self.house.rect)
            if self.workplace.sprite: self.screen.blit(self.workplace.sprite, self.workplace.rect)
            if self.shop.sprite: self.screen.blit(self.shop.sprite, self.shop.rect)

            # PNJs
            for npc in self.npcs:
                if npc.sprite:
                    shadow_pos = (npc.rect.centerx - 10, npc.rect.bottom - 5)
                    pygame.draw.ellipse(self.screen, (30, 80, 30), (shadow_pos[0], shadow_pos[1], 20, 8))
                    self.screen.blit(npc.sprite, npc.rect)
                    name_surf = self.font.render(npc.name, True, (200, 255, 200))
                    text_x = npc.rect.centerx - (name_surf.get_width() // 2)
                    self.screen.blit(name_surf, (text_x, npc.rect.top - 20))

        elif self.location == "house":
            self.draw_house_interior()

        # 2. JOUEUR
        if self.player.sprite:
            shadow_pos = (self.player.rect.centerx - 10, self.player.rect.bottom - 5)
            pygame.draw.ellipse(self.screen, (30, 80, 30), (shadow_pos[0], shadow_pos[1], 20, 8))
            self.screen.blit(self.player.sprite, self.player.rect)

         # --- AJOUT : FILTRE NUIT ---
        # On demande l'intensité de la nuit
        alpha = self.time_manager.get_night_intensity()
        if alpha > 0:
            # On configure la transparence
            self.night_filter.set_alpha(alpha)
            # On remplit avec la couleur bleue nuit définie dans settings
            self.night_filter.fill(NIGHT_COLOR)
            # On colle par-dessus tout le reste
            self.screen.blit(self.night_filter, (0, 0))
        
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

        time_str = self.time_manager.get_time_string()
        day_str = f"Jour {self.time_manager.day}"

        infos = [
            f"📅 {day_str} - 🕒 {time_str}",
            f"Nom: {self.player.name}",
            f"Vie: {int(stats.health)}%  Nrj: {int(stats.energy)}%",
            f"Faim: {int(stats.hunger)}%  Argent: {stats.money} E",
            "--- Inventaire ---"
        ]

        # --- AJOUT : Affichage Quête Active ---
        # On regarde si un PNJ a une quête active
        active_quest_text = ""
        for npc in self.npcs:
            if npc.quest and npc.quest.is_active and not npc.quest.is_completed:
                active_quest_text = f"QUÊTE: {npc.quest.description}"
                break

        if active_quest_text:
            infos.append("----------------")
            infos.append(active_quest_text)
        
        if not self.player.inventory: infos.append("(Vide)")
        else:
            for item in self.player.inventory[:3]: infos.append(f"- {item.name}")

        for i, line in enumerate(infos):
            color = WHITE
            if "Faim" in line and stats.hunger < 20: color = (255, 100, 100)
            text_surf = self.font.render(line, True, color)
            self.screen.blit(text_surf, (10, 10 + i * 20))

        # Bulle Dialogue
        if self.last_message:
            box_rect = pygame.Rect(100, SCREEN_HEIGHT - 100, SCREEN_WIDTH - 200, 80)
            pygame.draw.rect(self.screen, (0, 0, 0), box_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 2)
            msg_surf = self.font.render(self.last_message, True, WHITE)
            text_rect = msg_surf.get_rect(center=box_rect.center)
            self.screen.blit(msg_surf, text_rect)

        # --- MENUS CONTEXTUELS ---
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
            # On vérifie quel objet on touche
            interact_obj = self.house.get_interactable_object(self.player.rect)
            
            if interact_obj:
                obj_type = interact_obj["type"]
                label = ""
                if obj_type == "bed": label = "[ESPACE] Dormir"
                elif obj_type == "kitchen": label = "Cuisine"
                elif obj_type == "fridge": label = "Frigo"
                elif obj_type == "toilet": label = "..."
                elif obj_type == "sofa": label = "[ESPACE] S'asseoir"
                
                if label:
                    self.draw_context_menu(interact_obj["rect"], label)
            
            # Sortie
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