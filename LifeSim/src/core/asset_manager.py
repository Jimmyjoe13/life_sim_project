# LifeSim/src/core/asset_manager.py
import pygame
import os

class AssetManager:
    _instance = None
    images = {}

    @classmethod
    def get(cls):
        """Récupère l'instance unique (Singleton)"""
        if cls._instance is None:
            cls._instance = AssetManager()
        return cls._instance

    def load_images(self):
        """Charge toutes les images du dossier assets/images"""
        # On remonte de src/core/ vers la racine pour trouver assets
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        img_dir = os.path.join(base_path, "assets", "images")
        
        filenames = {
            # === JOUEUR ===
            "player": "player.png",
            "player_walk_0": "player_walk_0.png",
            "player_walk_1": "player_walk_1.png",
            "player_walk_2": "player_walk_2.png",
            "player_walk_3": "player_walk_3.png",
            
            # === PNJ GÉNÉRIQUE ===
            "npc": "npc.png",
            "npc_villager": "npc_villager.png",
            
            # === PNJ INDIVIDUELS ===
            "npc_bob": "npc_bob.png",
            "npc_bob_walk_0": "npc_bob_walk_0.png",
            "npc_bob_walk_1": "npc_bob_walk_1.png",
            "npc_bob_walk_2": "npc_bob_walk_2.png",
            "npc_bob_walk_3": "npc_bob_walk_3.png",
            
            "npc_alice": "npc_alice.png",
            "npc_alice_walk_0": "npc_alice_walk_0.png",
            "npc_alice_walk_1": "npc_alice_walk_1.png",
            "npc_alice_walk_2": "npc_alice_walk_2.png",
            "npc_alice_walk_3": "npc_alice_walk_3.png",
            
            "npc_chef_marc": "npc_chef_marc.png",
            "npc_chef_marc_walk_0": "npc_chef_marc_walk_0.png",
            "npc_chef_marc_walk_1": "npc_chef_marc_walk_1.png",
            "npc_chef_marc_walk_2": "npc_chef_marc_walk_2.png",
            "npc_chef_marc_walk_3": "npc_chef_marc_walk_3.png",
            
            "npc_coach_sarah": "npc_coach_sarah.png",
            "npc_coach_sarah_walk_0": "npc_coach_sarah_walk_0.png",
            "npc_coach_sarah_walk_1": "npc_coach_sarah_walk_1.png",
            "npc_coach_sarah_walk_2": "npc_coach_sarah_walk_2.png",
            "npc_coach_sarah_walk_3": "npc_coach_sarah_walk_3.png",
            
            "npc_maire_dupont": "npc_maire_dupont.png",
            "npc_maire_dupont_walk_0": "npc_maire_dupont_walk_0.png",
            "npc_maire_dupont_walk_1": "npc_maire_dupont_walk_1.png",
            "npc_maire_dupont_walk_2": "npc_maire_dupont_walk_2.png",
            "npc_maire_dupont_walk_3": "npc_maire_dupont_walk_3.png",
            
            # === BÂTIMENTS ===
            "house": "house.png",
            "shop": "shop.png",
            "office": "office.png",
            
            # === ITEMS ===
            "apple": "apple.png",
            "coffee": "coffee.png",
            
            # === MEUBLES ===
            "bed": "bed.png",
            "table": "table.png",
            "chair": "chair.png",
            "kitchen": "kitchen.png",
            "fridge": "fridge.png",
            "toilet": "toilet.png",
            "sofa": "sofa.png",
            
            # === TUILES ÉTÉ ===
            "grass": "grass.png",
            "grass_1": "grass_1.png",
            "grass_2": "grass_2.png",
            "grass_3": "grass_3.png",
            "grass_4": "grass_4.png",
            "path": "path.png",
            "path_1": "path_1.png",
            "path_2": "path_2.png",
            "water": "water.png",
            "water_1": "water_1.png",
            "water_2": "water_2.png",
            "sand": "sand.png",
            "sand_1": "sand_1.png",
            
            # === TUILES HIVER ===
            "grass_winter": "grass_winter.png",
            "grass_winter_1": "grass_winter_1.png",
            "grass_winter_2": "grass_winter_2.png",
            "grass_winter_3": "grass_winter_3.png",
            "grass_winter_4": "grass_winter_4.png",
            "path_winter": "path_winter.png",
            "path_winter_1": "path_winter_1.png",
            "path_winter_2": "path_winter_2.png",
            "water_winter": "water_winter.png",
            "water_winter_1": "water_winter_1.png",
            "water_winter_2": "water_winter_2.png",
            "sand_winter": "sand_winter.png",
            "sand_winter_1": "sand_winter_1.png",
        }

        print(f"📂 Chargement des images depuis : {img_dir}")

        for key, fname in filenames.items():
            path = os.path.join(img_dir, fname)
            try:
                # .convert_alpha() est CRITIQUE pour la transparence (détourage)
                img = pygame.image.load(path).convert_alpha()
                self.images[key] = img
                print(f"  ✅ Chargé : {key}")
            except Exception as e:
                # En cas d'erreur, on crée un carré rose de secours
                fallback = pygame.Surface((64, 64))
                fallback.fill((255, 0, 255))
                self.images[key] = fallback
                # Ne pas afficher d'erreur pour les fichiers optionnels
                if "_walk_" not in fname and "_winter" not in fname:
                    print(f"  ⚠️ Non trouvé : {fname}")

    def get_image(self, key):
        return self.images.get(key)
    
    def get_walk_frames(self, base_key: str) -> list:
        """Retourne les 4 frames d'animation de marche pour une entité."""
        frames = []
        for i in range(4):
            key = f"{base_key}_walk_{i}"
            frame = self.images.get(key)
            if frame:
                frames.append(frame)
        
        # Si pas de frames de marche, retourner le sprite statique 4 fois
        if not frames:
            static = self.images.get(base_key)
            if static:
                frames = [static] * 4
        
        return frames
