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
            "player": "player.png",
            "shop": "shop.png",
            "apple": "apple.png",
            "office": "office.png",
            "coffee": "coffee.png",
            "npc_villager": "npc_villager.png",
            "house": "house.png", # <--- AJOUT
            "bed": "bed.png",
            "table": "table.png",
            "chair": "chair.png",
            "kitchen": "kitchen.png",
            "fridge": "fridge.png",
            "toilet": "toilet.png",
            "sofa": "sofa.png",
            # --- AJOUTS TUILES ---
            "grass": "grass.png",
            "path": "path.png",
            "water": "water.png"
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
                print(f"  ❌ Erreur sur {fname} : {e}")
                # En cas d'erreur, on crée un carré rose de secours
                fallback = pygame.Surface((32, 32))
                fallback.fill((255, 0, 255))
                self.images[key] = fallback

    def get_image(self, key):
        return self.images.get(key)