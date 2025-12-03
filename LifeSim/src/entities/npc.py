# src/entities/npc.py
import pygame
import random
# On importe la classe Quest pour le typage (optionnel mais propre)
# Si tu as une erreur d'import circulaire, tu peux retirer cet import
# et juste utiliser quest=None sans typage strict.

class NPC:
    def __init__(self, name, x, y, dialogues, quest=None):
        self.name = name
        self.x = x
        self.y = y
        self.dialogues = dialogues
        
        # --- NOUVEAU : GESTION DE QUÊTE ---
        self.quest = quest  # On stocke la quête (ou None s'il n'en a pas)
        
        # Gestion graphique
        self.sprite = None
        self.rect = pygame.Rect(x, y, 32, 48) # Taille par défaut

    def set_sprite(self, image):
        self.sprite = image
        self.rect = image.get_rect(topleft=(self.x, self.y))

    def check_collision(self, player_rect):
        # On agrandit un peu la zone de détection pour parler
        interaction_zone = self.rect.inflate(20, 20)
        return interaction_zone.colliderect(player_rect)

    def talk(self, player):
        """
        Gère le dialogue ET la logique de quête.
        Accepte l'objet 'player' en argument pour vérifier son inventaire.
        """
        
        # 1. Si le PNJ n'a pas de quête ou quête déjà finie
        if not self.quest or self.quest.is_completed:
            return f"{self.name}: {random.choice(self.dialogues)}"

        # 2. Si la quête n'est pas encore active, on la donne au joueur
        if not self.quest.is_active:
            self.quest.is_active = True
            return f"QUÊTE REÇUE : {self.quest.description} !"

        # 3. Si la quête est active, on vérifie si le joueur a l'objet
        if self.quest.is_active:
            # On cherche l'objet cible dans l'inventaire du joueur
            found_index = -1
            for i, item in enumerate(player.inventory):
                if item.name == self.quest.target_item:
                    found_index = i
                    break
            
            if found_index != -1:
                # BRAVO ! Le joueur a l'objet
                player.inventory.pop(found_index) # On retire l'objet du sac
                player.stats.money += self.quest.reward_amount # On donne l'argent
                self.quest.is_completed = True
                return f"Merci ! Voici {self.quest.reward_amount} E pour ton aide."
            else:
                # Le joueur n'a pas encore l'objet
                return f"{self.name}: Je t'attends... ({self.quest.target_item})"