# src/core/save_manager.py
import json
import os

class SaveManager:
    """Gère la persistance des données dans des fichiers JSON."""
    
    def __init__(self, filename="savegame.json"):
        # On remonte à la racine du projet pour trouver data/saves
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.save_path = os.path.join(base_path, "data", "saves", filename)

    def save(self, player_obj):
        """Sauvegarde l'état complet du jeu."""
        data = {
            "player": player_obj.to_dict()
            # Plus tard, on pourra ajouter "world", "npcs", "time", etc.
        }
        
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"✅ Partie sauvegardée dans : {self.save_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur de sauvegarde : {e}")
            return False

    def load(self, player_obj):
        """Charge la sauvegarde et met à jour l'objet player existant."""
        if not os.path.exists(self.save_path):
            print("⚠️ Aucune sauvegarde trouvée.")
            return False
            
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # On injecte les données dans l'objet joueur existant
            player_obj.from_dict(data["player"])
            return True
        except Exception as e:
            print(f"❌ Erreur de chargement : {e}")
            return False