# src/entities/npc.py
import pygame
import random

class NPC:
    def __init__(self, name, x, y, dialogues, quest=None, relationship_manager=None):
        self.name = name
        self.x = x
        self.y = y
        
        # On garde les dialogues de base, mais on pourra les étendre par la suite
        self.default_dialogues = dialogues
        
        # --- GESTION DE QUÊTE ---
        self.quest = quest
        
        # --- NOUVEAU : RELATION SOCIALE ---
        self.relationship_manager = relationship_manager
        
        # Gestion graphique
        self.sprite = None
        self.rect = pygame.Rect(x, y, 32, 48)

    def set_sprite(self, image):
        self.sprite = image
        self.rect = image.get_rect(topleft=(self.x, self.y))

    def check_collision(self, player_rect):
        interaction_zone = self.rect.inflate(20, 20)
        return interaction_zone.colliderect(player_rect)

    def get_dialogue_based_on_friendship(self):
        """Sélectionne une phrase selon le niveau d'amitié."""
        # Sécurité : Si pas de gestionnaire, on retourne un dialogue aléatoire de base
        if self.relationship_manager is None:
            return random.choice(self.default_dialogues)

        # On récupère le score d'amitié actuel via le système
        score = self.relationship_manager.get_friendship(self.name)
        
        # Logique des paliers
        if score <= 25:
            # Niveau 1 : Inconnu / Distant
            options = [
                "Je ne te connais pas très bien...",
                "Bonjour.",
                "Il fait beau, n'est-ce pas ?"
            ]
        elif score <= 50:
            # Niveau 2 : Connaissance
            options = [
                "Content de te revoir !",
                "Tu as l'air en forme aujourd'hui.",
                "J'aime bien discuter avec toi."
            ]
        elif score <= 75:
            # Niveau 3 : Ami
            options = [
                "Hé ! Mon ami préféré !",
                "Si tu as besoin d'aide, je suis là.",
                "C'est toujours un plaisir de te voir."
            ]
        else:
            # Niveau 4 : Meilleur Ami
            options = [
                "Tu es comme ma famille !",
                "Je te ferais confiance pour garder ma maison.",
                "On forme une super équipe toi et moi !"
            ]
            
        return random.choice(options)

    def talk(self, player):
        """
        Gère le dialogue ET la logique de quête.
        Priorité : Quête > Amitié
        """
        
        # 1. Gestion des quêtes (Prioritaire)
        if self.quest:
            # Si la quête est active mais pas finie
            if self.quest.is_active and not self.quest.is_completed:
                # Vérification de l'inventaire
                found_index = -1
                for i, item in enumerate(player.inventory):
                    if item.name == self.quest.target_item:
                        found_index = i
                        break
                
                if found_index != -1:
                    # SUCCÈS
                    player.inventory.pop(found_index)
                    player.stats.money += self.quest.reward_amount
                    self.quest.is_completed = True
                    return f"Merci ! Voici {self.quest.reward_amount} E pour ton aide."
                else:
                    # EN ATTENTE
                    return f"{self.name}: Je t'attends... ({self.quest.target_item})"

            # Si la quête n'est pas encore active, on la donne
            if not self.quest.is_active and not self.quest.is_completed:
                self.quest.is_active = True
                return f"QUÊTE REÇUE : {self.quest.description} !"

        # 2. Dialogue Social (Si pas de quête ou quête finie)
        message = self.get_dialogue_based_on_friendship()
        return f"{self.name}: {message}"