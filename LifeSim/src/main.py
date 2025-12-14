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
from src.entities.item import create_apple, ItemCategory
from src.entities.shop import Shop
from src.core.save_manager import SaveManager
from src.entities.workplace import Workplace
from src.entities.npc import NPC
from src.entities.house import House
from src.core.time_manager import TimeManager
from src.core.world_map import WorldMap
from src.entities.quest import Quest
from src.systems.relationship_system import RelationshipSystem
from src.systems.skill_system import SkillSystem, SkillType
from src.systems.event_system import EventSystem
from src.entities.npc_manager import NPCManager
from src.ui.inventory_ui import InventoryUI, SkillsUI
from src.ui.hud import ModernHUD, ControlsHint, QuestIndicator
from src.ui.dialogue_ui import MessageBox, ContextMenu
from src.ui.minimap import MiniMap
from src.ui.house_interior import ModernHouseInterior
from src.ui.shop_ui import ShopUI

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
        self.relationship_system = RelationshipSystem()
        self.time_manager = TimeManager()
        
        # NOUVEAUX SYSTÈMES
        self.skill_system = SkillSystem()
        self.event_system = EventSystem()
        
        # GESTIONNAIRE DE PNJ
        self.npc_manager = NPCManager(relationship_manager=self.relationship_system)
        
        # INTERFACES UTILISATEUR
        self.inventory_ui = InventoryUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.skills_ui = SkillsUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # HUD MODERNE
        self.modern_hud = ModernHUD(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.controls_hint = ControlsHint(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.quest_indicator = QuestIndicator(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.message_box = MessageBox(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.context_menu = ContextMenu()
        self.minimap = MiniMap(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.shop_ui = ShopUI(SCREEN_WIDTH, SCREEN_HEIGHT)

        # 4. MONDE EXTÉRIEUR
        self.shop = Shop(600, 100)
        self.shop.set_sprite(self.assets.get_image("shop"))
        
        self.workplace = Workplace(100, 400)
        self.workplace.set_sprite(self.assets.get_image("office"))
        
        # MAISON
        self.house = House(300, 50)
        self.house.set_outdoor_sprite(self.assets.get_image("house"))
        self.house.setup_interior(self.assets)
        
        # INTÉRIEUR MODERNE DE LA MAISON
        self.house_interior = ModernHouseInterior(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.house_interior.setup(self.assets)

        # 5. PNJS - Chargement depuis JSON
        data_path = os.path.join(parent_dir, "data", "npcs.json")
        if self.npc_manager.load_from_json(data_path):
            self.npcs = self.npc_manager.get_all_npcs()
            self.npc_manager.set_sprites(self.assets)
        else:
            # Fallback : créer des PNJ manuellement si le fichier n'existe pas
            self.npcs = []
            quest_bob = Quest(
                title="Livraison Fruitée",
                description="Apporte une Pomme Rouge à Bob",
                target_item="Pomme Rouge",
                reward_amount=50
            )
            bob = NPC("Bob", 300, 200, [
                "Quelle belle journée !",
                "J'ai vraiment très faim...",
            ], quest=quest_bob, relationship_manager=self.relationship_system)
            bob.set_sprite(self.assets.get_image("npc_villager"))
            self.npcs.append(bob)

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
            # On demande à l'intérieur moderne quel meuble on touche
            interact_obj = self.house_interior.get_interactable_object(self.player.rect)

        # --- BOUCLE D'ÉVÉNEMENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            if event.type == pygame.KEYDOWN:
                # Ouvrir/Fermer Inventaire
                if event.key == pygame.K_i:
                    self.inventory_ui.toggle()
                    self.skills_ui.close()  # Ferme l'autre menu
                
                # Ouvrir/Fermer Compétences
                if event.key == pygame.K_k:
                    self.skills_ui.toggle()
                    self.inventory_ui.close()
                
                # Toggle Mini-carte
                if event.key == pygame.K_m:
                    self.minimap.toggle()
                
                # Manger (Possible partout)
                if event.key == pygame.K_e:
                    if self.inventory_ui.is_open and self.inventory_ui.selected_index >= 0:
                        # Manger l'objet sélectionné
                        if self.inventory_ui.selected_index < len(self.player.inventory):
                            item = self.player.inventory[self.inventory_ui.selected_index]
                            if item.category in [ItemCategory.FOOD, ItemCategory.DRINK]:
                                self.player.eat_item(self.inventory_ui.selected_index)
                                self.skill_system.gain_xp(SkillType.COOKING, 5)
                                self.show_message(f"Miam ! {item.name} consommé.", 90)
                    else:
                        self.player.eat_item(0)

                # --- ACTIONS DU MONDE ---
                if self.location == "world":
                    if in_shop_zone:
                        # Achat d'items avec touches 1-9
                        shop_keys = {
                            pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
                            pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5,
                            pygame.K_7: 6, pygame.K_8: 7, pygame.K_9: 8,
                        }
                        if event.key in shop_keys:
                            item_index = shop_keys[event.key]
                            result = self.shop.try_buy_item(self.player, item_index)
                            self.show_message(result, 120)

                    if in_work_zone and event.key == pygame.K_SPACE:
                        result = self.workplace.work(self.player)
                        # Gagner de l'XP en travaillant
                        self.skill_system.gain_xp(SkillType.WORK, 15)
                        self.show_message(result, 120)

                    if nearby_npc and event.key == pygame.K_t:
                        # 1. On récupère la réponse du PNJ
                        response = nearby_npc.talk(self.player)
                        
                        # 2. On augmente l'amitié (+2 points par discussion)
                        self.relationship_system.modify_friendship(nearby_npc.name, 2)
                        # Gagner de l'XP social
                        self.skill_system.gain_xp(SkillType.SOCIAL, 5)
                        
                        # 3. On récupère le nouveau statut pour l'afficher
                        new_score = self.relationship_system.get_friendship(nearby_npc.name)
                        status = self.relationship_system.get_relationship_status(nearby_npc.name)
                        
                        self.show_message(f"{response} (Amitié: {new_score} - {status})", 180)
                    
                    # OFFRIR UN CADEAU (nouvelle touche G)
                    if nearby_npc and event.key == pygame.K_g:
                        # Chercher un cadeau dans l'inventaire
                        gift_found = False
                        for i, item in enumerate(self.player.inventory):
                            if item.category == ItemCategory.GIFT:
                                # Offrir le cadeau
                                bonus, reaction = self.npc_manager.check_gift_reaction(nearby_npc, item.name)
                                self.relationship_system.modify_friendship(nearby_npc.name, bonus + item.friendship_value)
                                self.skill_system.gain_xp(SkillType.SOCIAL, 10)
                                self.player.inventory.pop(i)
                                self.show_message(reaction, 150)
                                gift_found = True
                                break
                        
                        if not gift_found:
                            self.show_message("Pas de cadeau dans l'inventaire !", 90)
                    
                    if can_enter_house and event.key == pygame.K_SPACE:
                        self.switch_location("house")

                # --- ACTIONS DE LA MAISON (NOUVEAU) ---
                elif self.location == "house" and interact_obj:
                    obj_type = interact_obj["type"]
                    
                    if event.key == pygame.K_SPACE:
                        if obj_type == "bed":
                            self.player.stats.energy = 100
                            self.player.stats.health += 10
                            self.skill_system.gain_xp(SkillType.FITNESS, 10)
                            self.show_message("Zzz... Une bonne nuit de sommeil !", 120)
                        elif obj_type == "kitchen" or obj_type == "fridge":
                            self.show_message("Le frigo est vide... Il faut aller au Shop !", 120)
                        elif obj_type == "toilet":
                            self.show_message("Occupé...", 60)
                        elif obj_type == "sofa":
                            self.show_message("Petite pause Netflix.", 120)
                            self.player.stats.energy += 5
                            self.skill_system.gain_xp(SkillType.FITNESS, 3)

                if event.key == pygame.K_F5:
                    if self.save_manager.save(
                        self.player, 
                        self.time_manager, 
                        self.relationship_system,
                        self.skill_system,
                        self.event_system
                    ):
                        self.show_message("Partie Sauvegardée !", 120)
                if event.key == pygame.K_F9:
                    if self.save_manager.load(
                        self.player,
                        self.time_manager,
                        self.relationship_system,
                        self.skill_system,
                        self.event_system
                    ):
                        self.show_message("Partie Chargée !", 120)

        # --- MOUVEMENT ---
        # Ne pas bouger si un menu est ouvert
        if self.inventory_ui.is_open or self.skills_ui.is_open:
            self.move_intent = (0, 0)
            return
        
        dx, dy = 0, 0
        # Support AZERTY (ZQSD) et flèches directionnelles
        if keys[pygame.K_LEFT] or keys[pygame.K_q] or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_z] or keys[pygame.K_w]: dy = -1
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
        
        # Mise à jour des positions des PNJ selon l'heure
        current_hour = int(self.time_manager.minutes // 60)
        self.npc_manager.update_positions_by_time(current_hour)
        
        # Vérifier les événements aléatoires
        game_minutes = int(self.time_manager.day * 1440 + self.time_manager.minutes)
        event = self.event_system.update(game_minutes)
        if event:
            self.event_system.apply_event_effects(self.player, event)
            self.show_message(event.message)
        
        # Mise à jour météo toutes les heures de jeu
        if int(self.time_manager.minutes) % 60 == 0:
            self.event_system.update_weather()
        
        # Gestion du timer de message
        if self.message_timer > 0:
            self.message_timer -= 1
        elif self.message_timer == 0 and self.last_message:
            self.message_box.hide()
            self.last_message = ""
    
    def show_message(self, message: str, duration: int = 180):
        """Affiche un message avec le nouveau système de message box."""
        self.last_message = message
        self.message_timer = duration
        self.message_box.show(message)

    def draw_house_interior(self):
        """Dessine l'intérieur moderne de la maison."""
        self.house_interior.draw(self.screen)

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
        
        # 3. UI MODERNE
        self.draw_ui()
        
        # 4. Mini-carte (seulement en extérieur)
        if self.location == "world":
            buildings = {
                "shop": self.shop.rect,
                "house": self.house.rect,
                "workplace": self.workplace.rect
            }
            self.minimap.draw(self.screen, self.player, self.npcs, buildings)
            
            # Afficher le Shop UI si le joueur est près du magasin
            if self.shop.check_collision(self.player.rect):
                self.shop_ui.draw(self.screen, self.shop, self.player.stats.money)
        
        # 5. INTERFACES INVENTAIRE / COMPÉTENCES
        self.inventory_ui.draw(self.screen, self.player)
        self.skills_ui.draw(self.screen, self.skill_system)
        
        # 6. Hints de contrôles (en bas de l'écran)
        self.controls_hint.draw(self.screen)
        
        # 7. Message box (dialogues/infos)
        self.message_box.update(self.clock.get_time() / 1000.0)
        self.message_box.draw(self.screen)
        
        pygame.display.flip()

    def draw_ui(self):
        # Mise à jour et dessin du HUD moderne
        dt = self.clock.get_time() / 1000.0  # Delta time pour animations
        self.modern_hud.update(dt, self.player.stats)
        self.modern_hud.draw(self.screen, self.player, self.time_manager, self.event_system)

        # --- AJOUT : Affichage Quête Active ---
        active_quest_text = ""
        for npc in self.npcs:
            if npc.quest and npc.quest.is_active and not npc.quest.is_completed:
                active_quest_text = npc.quest.description
                break
        
        if active_quest_text:
            self.quest_indicator.draw(self.screen, active_quest_text)

        # --- MENUS CONTEXTUELS ---
        if self.location == "world":
            if self.shop.check_collision(self.player.rect):
                # Afficher le menu du shop avec plus d'options
                menu_text = "[1-9] Acheter | Shop ouvert !"
                self.draw_context_menu(self.shop.rect, menu_text)
            
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
        self.context_menu.draw(self.screen, target_rect, text)

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