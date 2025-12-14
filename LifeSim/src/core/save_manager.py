# src/core/save_manager.py
import json
import os

class SaveManager:
    """Gère la persistance des données dans des fichiers JSON."""
    
    def __init__(self, filename="savegame.json"):
        # On remonte à la racine du projet pour trouver data/saves
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.save_path = os.path.join(base_path, "data", "saves", filename)

    def save(self, player_obj, time_manager=None, relationship_system=None, 
             skill_system=None, event_system=None):
        """Sauvegarde l'état complet du jeu."""
        data = {
            "player": player_obj.to_dict()
        }
        
        # Sauvegarder le temps
        if time_manager:
            data["time"] = {
                "day": time_manager.day,
                "minutes": time_manager.minutes
            }
        
        # Sauvegarder les relations
        if relationship_system:
            data["relationships"] = relationship_system.to_dict()
        
        # Sauvegarder les compétences
        if skill_system:
            data["skills"] = skill_system.to_dict()
        
        # Sauvegarder les événements/météo
        if event_system:
            data["events"] = event_system.to_dict()
        
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"✅ Partie sauvegardée dans : {self.save_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur de sauvegarde : {e}")
            return False

    def load(self, player_obj, time_manager=None, relationship_system=None,
             skill_system=None, event_system=None):
        """Charge la sauvegarde et met à jour tous les objets."""
        if not os.path.exists(self.save_path):
            print("⚠️ Aucune sauvegarde trouvée.")
            return False
            
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Charger le joueur
            player_obj.from_dict(data["player"])
            
            # Charger le temps
            if time_manager and "time" in data:
                time_data = data["time"]
                time_manager.day = time_data.get("day", 1)
                time_manager.minutes = time_data.get("minutes", 480)
                print(f"⏰ Temps chargé : Jour {time_manager.day}")
            
            # Charger les relations
            if relationship_system and "relationships" in data:
                relationship_system.from_dict(data["relationships"])
            
            # Charger les compétences
            if skill_system and "skills" in data:
                skill_system.from_dict(data["skills"])
            
            # Charger les événements/météo
            if event_system and "events" in data:
                event_system.from_dict(data["events"])
            
            return True
        except Exception as e:
            print(f"❌ Erreur de chargement : {e}")
            return False
