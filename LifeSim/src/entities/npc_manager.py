# LifeSim/src/entities/npc_manager.py
"""
Gestionnaire de PNJ - Charge et gère tous les PNJ du jeu.
"""

import json
import os
from typing import List, Dict, Optional
from src.entities.npc import NPC
from src.entities.quest import Quest


class NPCManager:
    """
    Charge les PNJ depuis un fichier JSON et les gère.
    Permet d'ajouter facilement de nouveaux PNJ sans modifier le code.
    """
    
    def __init__(self, relationship_manager=None):
        self.npcs: List[NPC] = []
        self.npcs_by_id: Dict[str, NPC] = {}
        self.relationship_manager = relationship_manager
    
    def load_from_json(self, json_path: str) -> bool:
        """
        Charge tous les PNJ depuis un fichier JSON.
        Retourne True si le chargement a réussi.
        """
        if not os.path.exists(json_path):
            print(f"❌ Fichier NPC non trouvé : {json_path}")
            return False
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.npcs = []
            self.npcs_by_id = {}
            
            for npc_data in data.get("npcs", []):
                npc = self._create_npc_from_data(npc_data)
                if npc:
                    self.npcs.append(npc)
                    self.npcs_by_id[npc_data.get("id", npc.name)] = npc
            
            print(f"✅ {len(self.npcs)} PNJ chargés avec succès !")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur de parsing JSON : {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors du chargement des PNJ : {e}")
            return False
    
    def _create_npc_from_data(self, data: dict) -> Optional[NPC]:
        """Crée un NPC à partir des données JSON."""
        try:
            # Créer la quête si elle existe
            quest = None
            quest_data = data.get("quest")
            if quest_data:
                quest = Quest(
                    title=quest_data.get("title", "Quête"),
                    description=quest_data.get("description", ""),
                    target_item=quest_data.get("target_item", ""),
                    reward_amount=quest_data.get("reward_amount", 50)
                )
            
            # Créer le NPC
            npc = NPC(
                name=data.get("name", "Inconnu"),
                x=data.get("x", 0),
                y=data.get("y", 0),
                dialogues=data.get("dialogues", ["..."]),
                quest=quest,
                relationship_manager=self.relationship_manager
            )
            
            # Ajouter les attributs étendus
            npc.personality = data.get("personality", "neutral")
            npc.favorite_gifts = data.get("favorite_gifts", [])
            npc.disliked_gifts = data.get("disliked_gifts", [])
            npc.schedule = data.get("schedule", {})
            npc.npc_id = data.get("id", npc.name.lower())
            
            return npc
            
        except Exception as e:
            print(f"❌ Erreur création NPC : {e}")
            return None
    
    def get_npc_by_id(self, npc_id: str) -> Optional[NPC]:
        """Retourne un PNJ par son ID."""
        return self.npcs_by_id.get(npc_id)
    
    def get_npc_by_name(self, name: str) -> Optional[NPC]:
        """Retourne un PNJ par son nom."""
        for npc in self.npcs:
            if npc.name == name:
                return npc
        return None
    
    def get_all_npcs(self) -> List[NPC]:
        """Retourne tous les PNJ."""
        return self.npcs
    
    def update_positions_by_time(self, current_hour: int):
        """
        Met à jour les positions des PNJ selon l'heure.
        morning: 6h-12h
        afternoon: 12h-18h
        evening: 18h-6h
        """
        if 6 <= current_hour < 12:
            period = "morning"
        elif 12 <= current_hour < 18:
            period = "afternoon"
        else:
            period = "evening"
        
        for npc in self.npcs:
            if hasattr(npc, 'schedule') and npc.schedule:
                schedule = npc.schedule.get(period)
                if schedule:
                    npc.x = schedule.get("x", npc.x)
                    npc.y = schedule.get("y", npc.y)
                    # Mettre à jour le rect aussi
                    if npc.rect:
                        npc.rect.x = npc.x
                        npc.rect.y = npc.y
    
    def check_gift_reaction(self, npc: NPC, item_name: str) -> tuple:
        """
        Vérifie la réaction du PNJ à un cadeau.
        Retourne (bonus_amitié, message)
        """
        base_bonus = 5
        
        if hasattr(npc, 'favorite_gifts') and item_name in npc.favorite_gifts:
            return (base_bonus * 3, f"😍 {npc.name} adore ce cadeau !")
        elif hasattr(npc, 'disliked_gifts') and item_name in npc.disliked_gifts:
            return (-base_bonus, f"😒 {npc.name} n'aime pas vraiment ça...")
        else:
            return (base_bonus, f"😊 {npc.name} apprécie le geste.")
    
    def set_sprites(self, asset_manager):
        """Associe les sprites à tous les PNJ."""
        for npc in self.npcs:
            # Essayer de charger un sprite spécifique, sinon utiliser le générique
            npc_id = getattr(npc, 'npc_id', 'npc')
            sprite = asset_manager.get_image(f"npc_{npc_id}")
            if sprite is None:
                sprite = asset_manager.get_image("npc")
            if sprite:
                npc.set_sprite(sprite)
