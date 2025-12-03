# LifeSim/tools/make_assets.py
import pygame
import os
import random

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

# --- PALETTE DE COULEURS (Pour la cohérence) ---
C_SKIN = (255, 220, 177)
C_SHIRT_P1 = (220, 50, 50)   # Rouge héroïque
C_SHIRT_NPC = (50, 180, 80)  # Vert villageois
C_JEANS = (40, 60, 140)
C_SHOES = (30, 30, 30)
C_HAIR = (70, 40, 20)
C_GRASS = (100, 180, 80)
C_WATER = (60, 160, 230)
C_DIRT = (160, 140, 100)

def draw_character(surface, color_shirt):
    """Fonction générique pour dessiner un humanoïde"""
    # 1. Corps (T-Shirt)
    pygame.draw.rect(surface, color_shirt, (8, 20, 16, 14))
    # 2. Bras
    pygame.draw.rect(surface, C_SKIN, (4, 20, 4, 12))
    pygame.draw.rect(surface, C_SKIN, (24, 20, 4, 12))
    # 3. Jambes (Jeans)
    pygame.draw.rect(surface, C_JEANS, (8, 34, 6, 10))
    pygame.draw.rect(surface, C_JEANS, (18, 34, 6, 10))
    # 4. Chaussures
    pygame.draw.rect(surface, C_SHOES, (8, 44, 6, 4))
    pygame.draw.rect(surface, C_SHOES, (18, 44, 6, 4))
    # 5. Tête
    pygame.draw.rect(surface, C_SKIN, (8, 4, 16, 16))
    # 6. Cheveux
    pygame.draw.rect(surface, C_HAIR, (8, 0, 16, 6))
    pygame.draw.rect(surface, C_HAIR, (6, 2, 2, 10))
    pygame.draw.rect(surface, C_HAIR, (24, 2, 2, 10))
    # 7. Yeux
    pygame.draw.rect(surface, (0,0,0), (12, 10, 2, 2))
    pygame.draw.rect(surface, (0,0,0), (18, 10, 2, 2))

def make_player():
    # Taille standard 32x48 pour les personnages
    s = create_surface(32, 48)
    draw_character(s, C_SHIRT_P1)
    # Détail : Un petit sac à dos pour l'inventaire
    pygame.draw.rect(s, (100, 50, 0), (10, 22, 12, 10)) 
    save(s, "player.png")

def make_npc():
    s = create_surface(32, 48)
    draw_character(s, C_SHIRT_NPC)
    save(s, "npc_villager.png")

def make_house():
    # 64x64 (2x2 tuiles)
    s = create_surface(64, 64)
    # Murs
    pygame.draw.rect(s, (240, 230, 200), (8, 24, 48, 40))
    # Toit (Triangle)
    pygame.draw.polygon(s, (180, 60, 60), [(0, 24), (32, 0), (64, 24)])
    # Ombre sous le toit
    pygame.draw.line(s, (140, 40, 40), (2, 24), (62, 24), 2)
    # Porte
    pygame.draw.rect(s, (120, 70, 30), (26, 40, 12, 24))
    pygame.draw.circle(s, (255, 215, 0), (36, 52), 2) # Poignée dorée
    # Fenêtre
    pygame.draw.rect(s, (150, 200, 255), (12, 35, 10, 10))
    pygame.draw.rect(s, (120, 70, 30), (12, 35, 10, 10), 2) # Cadre
    save(s, "house.png")

def make_shop():
    # 64x64
    s = create_surface(64, 64)
    # Bâtiment brique
    pygame.draw.rect(s, (180, 100, 80), (4, 20, 56, 44))
    # Toit plat
    pygame.draw.rect(s, (80, 80, 90), (2, 15, 60, 10))
    # Grande Vitrine
    pygame.draw.rect(s, (200, 240, 255), (8, 35, 20, 15))
    # Porte vitrée
    pygame.draw.rect(s, (150, 200, 255), (36, 35, 16, 29))
    pygame.draw.rect(s, (50, 50, 100), (36, 35, 16, 29), 2) # Cadre porte
    # Enseigne "SHOP" (Simulation de texte avec des lignes)
    pygame.draw.rect(s, (255, 255, 200), (15, 5, 34, 10))
    pygame.draw.rect(s, (200, 50, 50), (17, 7, 30, 6))
    save(s, "shop.png")

def make_office():
    # 64x80 (Plus haut)
    s = create_surface(64, 80)
    # Béton moderne
    pygame.draw.rect(s, (140, 140, 150), (4, 10, 56, 70))
    # Entrée sombre
    pygame.draw.rect(s, (60, 60, 70), (22, 60, 20, 20))
    # Vitres (Grilles)
    for y in range(15, 55, 12):
        for x in range(10, 50, 14):
            pygame.draw.rect(s, (200, 230, 255), (x, y, 10, 8))
    # Logo "W" sur le toit
    pygame.draw.rect(s, (50, 50, 150), (20, 0, 24, 10))
    save(s, "office.png")

# --- ITEMS ---
def make_items():
    # Pomme (32x32)
    s = create_surface(32, 32)
    pygame.draw.circle(s, (220, 20, 20), (16, 18), 10) # Rouge
    pygame.draw.circle(s, (255, 100, 100), (12, 14), 3) # Reflet
    pygame.draw.line(s, (100, 50, 0), (16, 8), (16, 2), 2) # Tige
    pygame.draw.ellipse(s, (50, 200, 50), (16, 4, 8, 4)) # Feuille
    save(s, "apple.png")

    # Café (32x32)
    s = create_surface(32, 32)
    # Tasse
    pygame.draw.rect(s, (255, 255, 255), (8, 12, 16, 16))
    pygame.draw.line(s, (255, 255, 255), (24, 14), (28, 14), 2) # Anse haut
    pygame.draw.line(s, (255, 255, 255), (28, 14), (28, 22), 2) # Anse coté
    pygame.draw.line(s, (255, 255, 255), (28, 22), (24, 22), 2) # Anse bas
    # Liquide noir
    pygame.draw.rect(s, (60, 30, 0), (10, 14, 12, 12))
    # Vapeur
    pygame.draw.line(s, (200, 200, 200), (12, 8), (12, 4), 1)
    pygame.draw.line(s, (200, 200, 200), (16, 6), (16, 2), 1)
    pygame.draw.line(s, (200, 200, 200), (20, 8), (20, 4), 1)
    save(s, "coffee.png")

# --- MEUBLES ---
def make_furniture():
    # Lit (32x48)
    s = create_surface(32, 48)
    pygame.draw.rect(s, (200, 200, 200), (2, 2, 28, 44)) # Structure
    pygame.draw.rect(s, (255, 255, 255), (4, 4, 24, 12)) # Oreiller
    pygame.draw.rect(s, (80, 100, 200), (4, 18, 24, 28)) # Couverture bleue
    save(s, "bed.png")

    # Table (64x48)
    s = create_surface(64, 48)
    pygame.draw.rect(s, (120, 80, 40), (4, 4, 56, 40)) # Plateau bois
    pygame.draw.rect(s, (100, 60, 30), (8, 8, 48, 32)) # Centre table
    save(s, "table.png")

    # Chaise (32x32)
    s = create_surface(32, 32)
    pygame.draw.rect(s, (120, 80, 40), (8, 8, 16, 16)) # Assise
    pygame.draw.rect(s, (100, 60, 30), (8, 2, 16, 6))  # Dossier
    save(s, "chair.png")

    # Frigo (32x64)
    s = create_surface(32, 64)
    pygame.draw.rect(s, (230, 240, 255), (0, 0, 32, 64))
    pygame.draw.line(s, (180, 180, 180), (0, 24), (32, 24), 1) # Séparation
    pygame.draw.rect(s, (180, 180, 180), (4, 28, 2, 10)) # Poignée bas
    pygame.draw.rect(s, (180, 180, 180), (4, 10, 2, 8))  # Poignée haut
    save(s, "fridge.png")

    # Cuisine (64x48)
    s = create_surface(64, 48)
    pygame.draw.rect(s, (180, 180, 190), (0, 0, 64, 48)) # Meuble gris
    pygame.draw.circle(s, (30, 30, 30), (16, 24), 10) # Plaque cuisson 1
    pygame.draw.circle(s, (30, 30, 30), (48, 24), 10) # Plaque cuisson 2
    pygame.draw.rect(s, (50, 50, 50), (0, 0, 64, 6)) # Crédence
    save(s, "kitchen.png")

    # Toilette (32x32)
    s = create_surface(32, 32)
    pygame.draw.rect(s, (255, 255, 255), (8, 0, 16, 10)) # Réservoir
    pygame.draw.ellipse(s, (255, 255, 255), (6, 8, 20, 22)) # Cuvette
    pygame.draw.ellipse(s, (200, 200, 200), (10, 12, 12, 14)) # Intérieur
    save(s, "toilet.png")

    # Sofa (80x40)
    s = create_surface(80, 40)
    pygame.draw.rect(s, (60, 40, 100), (0, 10, 80, 30)) # Base violette
    pygame.draw.rect(s, (80, 60, 120), (5, 5, 70, 15))  # Dossier
    pygame.draw.rect(s, (50, 30, 80), (0, 10, 15, 30))  # Accoudoir G
    pygame.draw.rect(s, (50, 30, 80), (65, 10, 15, 30)) # Accoudoir D
    save(s, "sofa.png")

# --- TUILES (SOL) ---
def make_tiles():
    # 1. Herbe (Texture naturelle)
    s = create_surface(32, 32)
    pygame.draw.rect(s, C_GRASS, (0, 0, 32, 32))
    # Ajout de bruit pour la texture
    for _ in range(20):
        x, y = random.randint(0, 30), random.randint(0, 30)
        color = (C_GRASS[0]+20, C_GRASS[1]+20, C_GRASS[2]) # Brin clair
        pygame.draw.line(s, color, (x, y), (x, y-2), 1)
    save(s, "grass.png")

    # 2. Chemin (Terre avec cailloux)
    s = create_surface(32, 32)
    pygame.draw.rect(s, C_DIRT, (0, 0, 32, 32))
    for _ in range(10):
        x, y = random.randint(2, 28), random.randint(2, 28)
        pygame.draw.rect(s, (120, 100, 70), (x, y, 3, 3)) # Caillou
    save(s, "path.png")

    # 3. Eau (Ondulations)
    s = create_surface(32, 32)
    pygame.draw.rect(s, C_WATER, (0, 0, 32, 32))
    for i in range(0, 32, 8):
        pygame.draw.line(s, (200, 230, 255), (0, i), (32, i), 1) # Vagues simples
    save(s, "water.png")

if __name__ == "__main__":
    pygame.init()
    # Mode invisible pour générer
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    print("🎨 Génération des assets ENRICHIS via Code...")
    
    make_player()
    make_npc()
    make_house()
    make_shop()
    make_office()
    make_tiles()
    make_items()
    make_furniture()
    
    print("\n🎉 Assets générés avec succès ! Relance le jeu maintenant.")
    pygame.quit()