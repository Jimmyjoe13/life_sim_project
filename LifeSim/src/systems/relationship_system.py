# LifeSim/src/systems/relationship_system.py

class RelationshipSystem:
    """
    Gère les niveaux d'amitié entre le joueur et les PNJ.
    Les valeurs vont de 0 (Inconnu/Hostile) à 100 (Meilleur ami).
    """
    def __init__(self):
        # Dictionnaire : { "NomDuPNJ": niveau_amitié (int) }
        self.relationships = {}

    def ensure_npc_exists(self, npc_name: str):
        """Initialise le PNJ dans la base de données s'il n'existe pas encore."""
        if npc_name not in self.relationships:
            self.relationships[npc_name] = 0

    def modify_friendship(self, npc_name: str, amount: int):
        """
        Ajoute ou retire des points d'amitié.
        La valeur reste bornée entre 0 et 100.
        """
        self.ensure_npc_exists(npc_name)
        
        current = self.relationships[npc_name]
        new_value = current + amount
        
        # On s'assure que ça ne dépasse pas les limites (Clamping)
        self.relationships[npc_name] = max(0, min(100, new_value))
        
        # Petit print pour le debug (tu le verras dans la console)
        print(f"❤️ Relation avec {npc_name}: {self.relationships[npc_name]} ({amount:+})")

    def get_friendship(self, npc_name: str) -> int:
        """Retourne le score actuel d'amitié."""
        return self.relationships.get(npc_name, 0)

    def get_relationship_status(self, npc_name: str) -> str:
        """Retourne un texte décrivant la relation selon le score."""
        score = self.get_friendship(npc_name)
        
        if score <= 25:
            return "Inconnu"
        elif score <= 50:
            return "Connaissance"
        elif score <= 75:
            return "Ami"
        else:
            return "Meilleur Ami"

    # --- Pour la Sauvegarde (JSON) ---
    
    def to_dict(self):
        """Exporte les données pour la sauvegarde."""
        return self.relationships

    def from_dict(self, data: dict):
        """Charge les données depuis la sauvegarde."""
        if data:
            self.relationships = data
            print("❤️ Relations sociales chargées.")