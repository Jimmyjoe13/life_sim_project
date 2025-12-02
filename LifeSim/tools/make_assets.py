# LifeSim/tools/make_assets.py
import pygame
import os

# On se base sur l'emplacement de ce script pour trouver le dossier assets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")

# Création du dossier s'il n'existe pas
os.makedirs(ASSETS_DIR, exist_ok=True)

def create_surface(width, height):
    return pygame.Surface((width, height), pygame.SRCALPHA)

def save(surface, name):
    path = os.path.join(ASSETS_DIR, name)
    pygame.image.save(surface, path)
    print(f"✅ Image générée : {path}")

def make_player():
    # Un petit bonhomme (32x48)
    s = create_surface(32, 48)
    # Corps (Bleu)
    pygame.draw.rect(s, (50, 100, 200), (4, 20, 24, 20))
    # Tête (Peau)
    pygame.draw.rect(s, (255, 200, 180), (6, 4, 20, 16))
    # Yeux
    pygame.draw.rect(s, (0, 0, 0), (10, 10, 4, 4))
    pygame.draw.rect(s, (0, 0, 0), (18, 10, 4, 4))
    # Jambes
    pygame.draw.rect(s, (30, 30, 100), (8, 40, 6, 8))
    pygame.draw.rect(s, (30, 30, 100), (18, 40, 6, 8))
    save(s, "player.png")

def make_shop():
    # Une boutique (64x64)
    s = create_surface(64, 64)
    # Murs
    pygame.draw.rect(s, (200, 180, 140), (4, 20, 56, 44))
    # Toit Rouge
    pygame.draw.polygon(s, (200, 50, 50), [(0, 20), (32, 0), (64, 20)])
    # Porte
    pygame.draw.rect(s, (100, 50, 0), (24, 40, 16, 24))
    # Enseigne "SHOP" (Barre noire)
    pygame.draw.rect(s, (50, 50, 50), (12, 24, 40, 10))
    save(s, "shop.png")

def make_items():
    # Pomme
    s = create_surface(32, 32)
    pygame.draw.circle(s, (220, 20, 20), (16, 18), 10)
    pygame.draw.line(s, (0, 150, 0), (16, 10), (16, 4), 2)
    save(s, "apple.png")

    # Café
    s = create_surface(32, 32)
    pygame.draw.rect(s, (255, 255, 255), (8, 10, 16, 18))
    pygame.draw.rect(s, (100, 50, 0), (10, 12, 12, 14))
    save(s, "coffee.png")

def make_office():
    # Un immeuble de bureaux (64x80)
    s = create_surface(64, 80)
    # Structure Béton
    pygame.draw.rect(s, (150, 150, 160), (4, 10, 56, 70))
    # Vitres (Bleu ciel)
    for y in range(20, 70, 15):
        pygame.draw.rect(s, (200, 230, 255), (10, y, 10, 10))
        pygame.draw.rect(s, (200, 230, 255), (28, y, 10, 10))
        pygame.draw.rect(s, (200, 230, 255), (46, y, 10, 10))
    # Porte
    pygame.draw.rect(s, (80, 80, 90), (24, 65, 16, 15))
    # Enseigne "WORK"
    pygame.draw.rect(s, (0, 0, 100), (12, 0, 40, 10))
    save(s, "office.png")

def make_npc():
    # Un Villageois (32x48) - Même base que le joueur mais couleurs différentes
    s = create_surface(32, 48)
    # Corps (Vert)
    pygame.draw.rect(s, (50, 200, 50), (4, 20, 24, 20))
    # Tête (Peau)
    pygame.draw.rect(s, (255, 200, 180), (6, 4, 20, 16))
    # Yeux
    pygame.draw.rect(s, (0, 0, 0), (10, 10, 4, 4))
    pygame.draw.rect(s, (0, 0, 0), (18, 10, 4, 4))
    # Jambes (Brun)
    pygame.draw.rect(s, (100, 50, 0), (8, 40, 6, 8))
    pygame.draw.rect(s, (100, 50, 0), (18, 40, 6, 8))
    save(s, "npc_villager.png")

def make_house():
    # Une petite maison confortable (64x64)
    s = create_surface(64, 64)
    # Murs (Blanc cassé)
    pygame.draw.rect(s, (240, 240, 230), (8, 20, 48, 44))
    # Toit (Bleu foncé)
    pygame.draw.polygon(s, (40, 40, 100), [(4, 20), (32, 0), (60, 20)])
    # Porte (Marron)
    pygame.draw.rect(s, (100, 50, 0), (26, 40, 12, 24))
    save(s, "house.png")

def make_bed():
    # Un lit (32x48)
    s = create_surface(32, 48)
    # Drap (Blanc)
    pygame.draw.rect(s, (255, 255, 255), (0, 0, 32, 48))
    # Couverture (Rouge)
    pygame.draw.rect(s, (200, 50, 50), (0, 16, 32, 32))
    # Oreiller (Blanc)
    pygame.draw.rect(s, (230, 230, 230), (4, 4, 24, 10))
    save(s, "bed.png")

if __name__ == "__main__":
    pygame.init()
    # Ecran virtuel pour permettre les opérations graphiques
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    print("🎨 Génération des assets en cours...")
    make_player()
    make_shop()
    make_items()
    make_office()
    make_npc()
    make_house() # <--- NOUVEAU
    make_bed()   # <--- NOUVEAU
    
    print("\n🎉 Assets Maison générés !")
    pygame.quit()