# LifeSim/tools/make_assets_modern.py
"""
Générateur de sprites modernes pour LifeSim.
Style inspiré de Stardew Valley avec sprites 64x64,
animations de marche et variations saisonnières.
"""

import pygame
import os
import random
import math

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")
os.makedirs(ASSETS_DIR, exist_ok=True)

# =============================================================================
# PALETTE DE COULEURS MODERNE
# =============================================================================

# Peaux
SKIN = {
    "light": (255, 224, 189),
    "medium": (241, 194, 150),
    "shadow": (214, 168, 133),
    "dark": (180, 138, 103),
}

# Cheveux
HAIR = {
    "brown": (101, 67, 33),
    "brown_highlight": (139, 90, 43),
    "black": (40, 30, 25),
    "blonde": (220, 190, 130),
    "red": (180, 80, 60),
}

# Vêtements
CLOTHES = {
    "player_red": (220, 60, 90),
    "player_red_dark": (180, 40, 70),
    "npc_green": (46, 204, 113),
    "npc_green_dark": (39, 174, 96),
    "npc_blue": (52, 152, 219),
    "npc_blue_dark": (41, 128, 185),
    "npc_purple": (155, 89, 182),
    "npc_purple_dark": (142, 68, 173),
    "npc_orange": (243, 156, 18),
    "npc_orange_dark": (230, 126, 34),
    "white": (245, 245, 245),
    "white_shadow": (220, 220, 220),
    "dark_suit": (44, 62, 80),
    "dark_suit_shadow": (30, 42, 54),
}

# Environnement - ÉTÉ
SUMMER = {
    "grass_light": (124, 205, 124),
    "grass_medium": (98, 178, 98),
    "grass_dark": (76, 153, 76),
    "grass_flower": (255, 200, 100),
    "water_light": (100, 181, 246),
    "water_medium": (66, 165, 245),
    "water_dark": (33, 150, 243),
    "dirt_light": (194, 178, 128),
    "dirt_dark": (159, 143, 103),
}

# Environnement - HIVER
WINTER = {
    "grass_light": (220, 235, 245),
    "grass_medium": (200, 220, 235),
    "grass_dark": (180, 200, 220),
    "grass_flower": (200, 200, 220),
    "water_light": (150, 200, 230),
    "water_medium": (120, 180, 220),
    "water_dark": (100, 160, 210),
    "dirt_light": (180, 175, 165),
    "dirt_dark": (150, 145, 140),
}

# Bâtiments
BUILDING = {
    "wood_light": (193, 154, 107),
    "wood_medium": (166, 124, 82),
    "wood_dark": (139, 90, 43),
    "stone_light": (189, 189, 189),
    "stone_dark": (145, 145, 145),
    "roof_red": (192, 57, 43),
    "roof_red_dark": (156, 46, 35),
    "roof_blue": (41, 128, 185),
    "roof_blue_dark": (31, 97, 141),
    "window_light": (200, 230, 255),
    "window_frame": (101, 67, 33),
    "door": (120, 80, 50),
}

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def create_surface(width, height):
    return pygame.Surface((width, height), pygame.SRCALPHA)

def save(surface, name):
    path = os.path.join(ASSETS_DIR, name)
    pygame.image.save(surface, path)
    print(f"✅ {name}")

def draw_outline(surface, color=(0, 0, 0)):
    """Ajoute un contour noir autour des pixels non-transparents."""
    w, h = surface.get_size()
    outline = create_surface(w, h)
    
    for x in range(w):
        for y in range(h):
            if surface.get_at((x, y))[3] > 128:  # Pixel visible
                # Vérifier les voisins
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if surface.get_at((nx, ny))[3] < 128:
                            outline.set_at((nx, ny), color)
                    else:
                        outline.set_at((x, y), color)
    
    # Combiner outline et surface
    result = create_surface(w, h)
    result.blit(outline, (0, 0))
    result.blit(surface, (0, 0))
    return result

def add_shading(surface, light_dir=(1, -1)):
    """Ajoute un léger ombrage."""
    w, h = surface.get_size()
    shaded = surface.copy()
    
    for x in range(w):
        for y in range(h):
            pixel = surface.get_at((x, y))
            if pixel[3] > 0:
                # Simple shading based on position
                shade_factor = 1.0 - (y / h) * 0.15
                new_color = (
                    int(pixel[0] * shade_factor),
                    int(pixel[1] * shade_factor),
                    int(pixel[2] * shade_factor),
                    pixel[3]
                )
                shaded.set_at((x, y), new_color)
    
    return shaded

# =============================================================================
# GÉNÉRATION DES PERSONNAGES (64x64)
# =============================================================================

def draw_character_64(surface, shirt_color, shirt_shadow, accessories=None, is_walking=False, walk_frame=0):
    """
    Dessine un personnage 64x64 avec plus de détails.
    
    Args:
        surface: Surface pygame
        shirt_color: Couleur principale du haut
        shirt_shadow: Couleur d'ombre du haut
        accessories: Dict d'accessoires optionnels
        is_walking: Si True, ajuste la pose
        walk_frame: 0-3 pour l'animation de marche
    """
    # Offsets pour animation de marche
    leg_offset = [0, 2, 0, -2][walk_frame] if is_walking else 0
    arm_offset = [0, -1, 0, 1][walk_frame] if is_walking else 0
    body_bob = [0, -1, 0, -1][walk_frame] if is_walking else 0
    
    # === OMBRE AU SOL ===
    pygame.draw.ellipse(surface, (0, 0, 0, 60), (18, 58, 28, 6))
    
    # === JAMBES (Jeans bleu) ===
    jeans_color = (60, 80, 140)
    jeans_shadow = (45, 60, 110)
    
    # Jambe gauche
    leg_left_x = 22 + leg_offset
    pygame.draw.rect(surface, jeans_color, (leg_left_x, 40 + body_bob, 8, 14))
    pygame.draw.rect(surface, jeans_shadow, (leg_left_x, 40 + body_bob, 3, 14))
    
    # Jambe droite
    leg_right_x = 34 - leg_offset
    pygame.draw.rect(surface, jeans_color, (leg_right_x, 40 + body_bob, 8, 14))
    pygame.draw.rect(surface, jeans_shadow, (leg_right_x, 40 + body_bob, 3, 14))
    
    # === CHAUSSURES ===
    shoe_color = (50, 40, 35)
    pygame.draw.rect(surface, shoe_color, (leg_left_x - 1, 52 + body_bob, 10, 6))
    pygame.draw.rect(surface, shoe_color, (leg_right_x - 1, 52 + body_bob, 10, 6))
    
    # === CORPS (T-Shirt) ===
    pygame.draw.rect(surface, shirt_color, (20, 26 + body_bob, 24, 16))
    pygame.draw.rect(surface, shirt_shadow, (20, 26 + body_bob, 8, 16))  # Ombre gauche
    
    # === BRAS ===
    # Bras gauche
    arm_left_y = 28 + body_bob + arm_offset
    pygame.draw.rect(surface, shirt_color, (14, arm_left_y, 6, 12))
    pygame.draw.rect(surface, SKIN["light"], (14, arm_left_y + 8, 6, 6))  # Main
    
    # Bras droit
    arm_right_y = 28 + body_bob - arm_offset
    pygame.draw.rect(surface, shirt_color, (44, arm_right_y, 6, 12))
    pygame.draw.rect(surface, SKIN["light"], (44, arm_right_y + 8, 6, 6))  # Main
    
    # === COU ===
    pygame.draw.rect(surface, SKIN["medium"], (28, 22 + body_bob, 8, 6))
    
    # === TÊTE ===
    head_y = 4 + body_bob
    # Forme arrondie
    pygame.draw.ellipse(surface, SKIN["light"], (20, head_y, 24, 22))
    pygame.draw.ellipse(surface, SKIN["shadow"], (20, head_y + 16, 24, 6))  # Ombre menton
    
    # === OREILLES ===
    pygame.draw.ellipse(surface, SKIN["light"], (17, head_y + 8, 5, 6))
    pygame.draw.ellipse(surface, SKIN["light"], (42, head_y + 8, 5, 6))
    pygame.draw.ellipse(surface, SKIN["shadow"], (18, head_y + 9, 3, 4))
    pygame.draw.ellipse(surface, SKIN["shadow"], (43, head_y + 9, 3, 4))
    
    # === CHEVEUX ===
    hair_color = HAIR["brown"]
    pygame.draw.ellipse(surface, hair_color, (20, head_y - 2, 24, 12))
    pygame.draw.rect(surface, hair_color, (18, head_y + 4, 4, 10))  # Côté gauche
    pygame.draw.rect(surface, hair_color, (42, head_y + 4, 4, 10))  # Côté droit
    
    # === YEUX ===
    eye_y = head_y + 10
    # Blanc des yeux
    pygame.draw.ellipse(surface, (255, 255, 255), (26, eye_y, 6, 4))
    pygame.draw.ellipse(surface, (255, 255, 255), (36, eye_y, 6, 4))
    # Pupilles
    pygame.draw.circle(surface, (40, 30, 20), (29, eye_y + 2), 2)
    pygame.draw.circle(surface, (40, 30, 20), (39, eye_y + 2), 2)
    # Reflets
    pygame.draw.circle(surface, (255, 255, 255), (30, eye_y + 1), 1)
    pygame.draw.circle(surface, (255, 255, 255), (40, eye_y + 1), 1)
    
    # === BOUCHE ===
    pygame.draw.line(surface, (180, 100, 100), (30, head_y + 16), (34, head_y + 16), 1)
    
    # === ACCESSOIRES ===
    if accessories:
        if accessories.get("backpack"):
            # Sac à dos
            pygame.draw.rect(surface, (139, 69, 19), (16, 28 + body_bob, 6, 12))
            pygame.draw.rect(surface, (101, 50, 14), (16, 28 + body_bob, 2, 12))
        
        if accessories.get("hat"):
            # Chapeau
            hat_color = accessories.get("hat_color", (139, 90, 43))
            pygame.draw.rect(surface, hat_color, (16, head_y - 4, 32, 6))
            pygame.draw.rect(surface, hat_color, (24, head_y - 8, 16, 6))
        
        if accessories.get("glasses"):
            # Lunettes
            pygame.draw.rect(surface, (0, 0, 0), (24, eye_y - 1, 8, 6), 1)
            pygame.draw.rect(surface, (0, 0, 0), (34, eye_y - 1, 8, 6), 1)
            pygame.draw.line(surface, (0, 0, 0), (32, eye_y + 1), (34, eye_y + 1), 1)
        
        if accessories.get("chef_hat"):
            # Toque de chef
            pygame.draw.rect(surface, (255, 255, 255), (22, head_y - 12, 20, 14))
            pygame.draw.ellipse(surface, (255, 255, 255), (18, head_y - 14, 28, 8))
        
        if accessories.get("headband"):
            # Bandeau sport
            pygame.draw.rect(surface, accessories.get("headband_color", (255, 100, 100)), 
                           (18, head_y + 2, 28, 4))
        
        if accessories.get("tie"):
            # Cravate
            tie_color = accessories.get("tie_color", (200, 50, 50))
            pygame.draw.polygon(surface, tie_color, [
                (30, 26 + body_bob), (34, 26 + body_bob),
                (36, 42 + body_bob), (32, 44 + body_bob), (28, 42 + body_bob)
            ])


def make_player_sprites():
    """Génère les sprites du joueur avec animations de marche."""
    print("\n🎮 Génération des sprites du joueur...")
    
    # Sprite statique
    s = create_surface(64, 64)
    draw_character_64(s, CLOTHES["player_red"], CLOTHES["player_red_dark"], 
                     {"backpack": True})
    s = draw_outline(s)
    save(s, "player.png")
    
    # Animations de marche (4 frames)
    for frame in range(4):
        s = create_surface(64, 64)
        draw_character_64(s, CLOTHES["player_red"], CLOTHES["player_red_dark"],
                         {"backpack": True}, is_walking=True, walk_frame=frame)
        s = draw_outline(s)
        save(s, f"player_walk_{frame}.png")


def make_npc_sprites():
    """Génère tous les sprites des PNJ."""
    print("\n👥 Génération des sprites PNJ...")
    
    npcs = {
        "bob": {
            "colors": (CLOTHES["npc_green"], CLOTHES["npc_green_dark"]),
            "accessories": {"hat": True, "hat_color": (160, 130, 90)}
        },
        "alice": {
            "colors": (CLOTHES["npc_purple"], CLOTHES["npc_purple_dark"]),
            "accessories": {"glasses": True}
        },
        "chef_marc": {
            "colors": (CLOTHES["white"], CLOTHES["white_shadow"]),
            "accessories": {"chef_hat": True}
        },
        "coach_sarah": {
            "colors": (CLOTHES["npc_orange"], CLOTHES["npc_orange_dark"]),
            "accessories": {"headband": True, "headband_color": (255, 80, 80)}
        },
        "maire_dupont": {
            "colors": (CLOTHES["dark_suit"], CLOTHES["dark_suit_shadow"]),
            "accessories": {"tie": True, "tie_color": (180, 50, 50)}
        },
    }
    
    # Sprite générique
    s = create_surface(64, 64)
    draw_character_64(s, CLOTHES["npc_green"], CLOTHES["npc_green_dark"])
    s = draw_outline(s)
    save(s, "npc.png")
    save(s, "npc_villager.png")
    
    for npc_name, npc_data in npcs.items():
        # Sprite statique
        s = create_surface(64, 64)
        draw_character_64(s, npc_data["colors"][0], npc_data["colors"][1],
                         npc_data.get("accessories"))
        s = draw_outline(s)
        save(s, f"npc_{npc_name}.png")
        
        # Animations de marche
        for frame in range(4):
            s = create_surface(64, 64)
            draw_character_64(s, npc_data["colors"][0], npc_data["colors"][1],
                             npc_data.get("accessories"), is_walking=True, walk_frame=frame)
            s = draw_outline(s)
            save(s, f"npc_{npc_name}_walk_{frame}.png")


# =============================================================================
# GÉNÉRATION DES BÂTIMENTS
# =============================================================================

def make_house():
    """Maison moderne 96x96."""
    print("\n🏠 Génération de la maison...")
    s = create_surface(96, 96)
    
    # Ombre au sol
    pygame.draw.ellipse(s, (0, 0, 0, 40), (8, 80, 80, 12))
    
    # Murs principaux
    pygame.draw.rect(s, BUILDING["wood_light"], (12, 40, 72, 48))
    pygame.draw.rect(s, BUILDING["wood_medium"], (12, 40, 24, 48))  # Ombre gauche
    
    # Texture bois horizontale
    for y in range(44, 88, 8):
        pygame.draw.line(s, BUILDING["wood_dark"], (12, y), (84, y), 1)
    
    # Toit
    pygame.draw.polygon(s, BUILDING["roof_red"], [
        (4, 42), (48, 8), (92, 42)
    ])
    pygame.draw.polygon(s, BUILDING["roof_red_dark"], [
        (4, 42), (48, 8), (48, 42)
    ])
    
    # Texture tuiles
    for y in range(15, 42, 6):
        for x in range(10, 85, 10):
            pygame.draw.arc(s, BUILDING["roof_red_dark"], (x, y, 10, 8), 0, 3.14, 1)
    
    # Porte
    pygame.draw.rect(s, BUILDING["door"], (38, 56, 20, 32))
    pygame.draw.rect(s, (90, 60, 35), (38, 56, 6, 32))  # Ombre
    pygame.draw.circle(s, (220, 180, 50), (54, 72), 3)  # Poignée
    
    # Fenêtre gauche
    pygame.draw.rect(s, BUILDING["window_frame"], (18, 52, 16, 14))
    pygame.draw.rect(s, BUILDING["window_light"], (20, 54, 12, 10))
    pygame.draw.line(s, BUILDING["window_frame"], (26, 54), (26, 64), 1)
    pygame.draw.line(s, BUILDING["window_frame"], (20, 59), (32, 59), 1)
    # Rideaux
    pygame.draw.rect(s, (200, 150, 150), (20, 54, 3, 10))
    pygame.draw.rect(s, (200, 150, 150), (29, 54, 3, 10))
    
    # Fenêtre droite
    pygame.draw.rect(s, BUILDING["window_frame"], (62, 52, 16, 14))
    pygame.draw.rect(s, BUILDING["window_light"], (64, 54, 12, 10))
    pygame.draw.line(s, BUILDING["window_frame"], (70, 54), (70, 64), 1)
    pygame.draw.line(s, BUILDING["window_frame"], (64, 59), (76, 59), 1)
    pygame.draw.rect(s, (200, 150, 150), (64, 54, 3, 10))
    pygame.draw.rect(s, (200, 150, 150), (73, 54, 3, 10))
    
    # Cheminée
    pygame.draw.rect(s, BUILDING["stone_dark"], (70, 10, 12, 20))
    pygame.draw.rect(s, BUILDING["stone_light"], (72, 10, 8, 18))
    
    save(s, "house.png")


def make_shop():
    """Magasin moderne 96x96."""
    print("\n🏪 Génération du magasin...")
    s = create_surface(96, 96)
    
    # Ombre
    pygame.draw.ellipse(s, (0, 0, 0, 40), (8, 82, 80, 10))
    
    # Structure en briques
    pygame.draw.rect(s, (180, 120, 100), (8, 30, 80, 58))
    
    # Texture briques
    for y in range(34, 88, 8):
        offset = 10 if (y // 8) % 2 == 0 else 0
        for x in range(8 + offset, 88, 20):
            pygame.draw.rect(s, (160, 100, 80), (x, y, 18, 6))
            pygame.draw.line(s, (140, 80, 60), (x, y + 6), (x + 18, y + 6), 1)
    
    # Auvent rayé
    auvent_colors = [(255, 80, 80), (255, 255, 255)]
    for i, x in enumerate(range(4, 92, 8)):
        pygame.draw.polygon(s, auvent_colors[i % 2], [
            (x, 30), (x + 8, 30), (x + 10, 38), (x - 2, 38)
        ])
    
    # Enseigne "SHOP"
    pygame.draw.rect(s, (50, 50, 60), (24, 10, 48, 18))
    pygame.draw.rect(s, (220, 180, 50), (24, 10, 48, 18), 2)  # Cadre doré
    font = pygame.font.Font(None, 20)
    # On simule le texte avec des rectangles
    pygame.draw.rect(s, (255, 255, 100), (30, 14, 8, 10))  # S
    pygame.draw.rect(s, (255, 255, 100), (42, 14, 8, 10))  # H
    pygame.draw.rect(s, (255, 255, 100), (54, 14, 8, 10))  # O
    pygame.draw.rect(s, (255, 255, 100), (66, 14, 8, 10))  # P
    
    # Grande vitrine
    pygame.draw.rect(s, BUILDING["window_frame"], (14, 44, 30, 28))
    pygame.draw.rect(s, BUILDING["window_light"], (16, 46, 26, 24))
    # Étagères dans la vitrine
    pygame.draw.line(s, (100, 70, 50), (16, 54), (42, 54), 2)
    pygame.draw.line(s, (100, 70, 50), (16, 62), (42, 62), 2)
    # Produits (petits rectangles colorés)
    for x in range(18, 40, 6):
        pygame.draw.rect(s, (random.randint(150, 255), random.randint(100, 200), random.randint(50, 150)), 
                        (x, 48, 4, 4))
        pygame.draw.rect(s, (random.randint(150, 255), random.randint(100, 200), random.randint(50, 150)),
                        (x, 56, 4, 4))
    
    # Porte vitrée
    pygame.draw.rect(s, (60, 80, 100), (52, 44, 26, 44))
    pygame.draw.rect(s, BUILDING["window_light"], (54, 46, 22, 38))
    pygame.draw.line(s, (80, 100, 120), (65, 46), (65, 84), 2)
    pygame.draw.circle(s, (220, 180, 50), (72, 66), 3)  # Poignée
    
    save(s, "shop.png")


def make_office():
    """Immeuble de bureaux 80x112."""
    print("\n🏢 Génération du bureau...")
    s = create_surface(80, 112)
    
    # Ombre
    pygame.draw.ellipse(s, (0, 0, 0, 40), (8, 100, 64, 10))
    
    # Structure moderne
    pygame.draw.rect(s, (120, 130, 140), (8, 16, 64, 92))
    pygame.draw.rect(s, (100, 110, 120), (8, 16, 20, 92))  # Ombre
    
    # Fenêtres (grille)
    for y in range(24, 96, 16):
        for x in range(14, 66, 16):
            pygame.draw.rect(s, (80, 120, 160), (x, y, 12, 12))
            pygame.draw.rect(s, (150, 200, 230), (x + 1, y + 1, 10, 10))
            # Reflet
            pygame.draw.line(s, (200, 230, 255), (x + 2, y + 2), (x + 4, y + 2), 1)
    
    # Toit
    pygame.draw.rect(s, (80, 90, 100), (6, 10, 68, 8))
    
    # Logo
    pygame.draw.rect(s, (50, 80, 150), (28, 2, 24, 8))
    pygame.draw.rect(s, (100, 150, 220), (30, 3, 6, 6))
    
    # Entrée
    pygame.draw.rect(s, (50, 60, 70), (28, 88, 24, 20))
    pygame.draw.rect(s, (80, 100, 120), (30, 90, 20, 16))
    
    save(s, "office.png")


# =============================================================================
# GÉNÉRATION DES TUILES (avec variations saisonnières)
# =============================================================================

def make_tiles(season="summer"):
    """Génère les tuiles de sol avec variations."""
    print(f"\n🌍 Génération des tuiles ({season})...")
    
    palette = SUMMER if season == "summer" else WINTER
    suffix = "" if season == "summer" else "_winter"
    
    # === HERBE ===
    for variant in range(3):
        s = create_surface(32, 32)
        
        # Base
        s.fill(palette["grass_medium"])
        
        # Variations de couleur
        for _ in range(40):
            x, y = random.randint(0, 30), random.randint(0, 30)
            color = random.choice([palette["grass_light"], palette["grass_dark"]])
            pygame.draw.rect(s, color, (x, y, 2, 2))
        
        # Brins d'herbe
        for _ in range(15):
            x = random.randint(2, 28)
            y = random.randint(2, 28)
            height = random.randint(3, 6)
            color = palette["grass_light"] if random.random() > 0.5 else palette["grass_dark"]
            pygame.draw.line(s, color, (x, y), (x + random.randint(-1, 1), y - height), 1)
        
        # Petites fleurs (rare)
        if random.random() > 0.7:
            fx, fy = random.randint(5, 25), random.randint(5, 25)
            pygame.draw.circle(s, palette["grass_flower"], (fx, fy), 2)
        
        save(s, f"grass{suffix}_{variant}.png" if variant > 0 else f"grass{suffix}.png")
    
    # === CHEMIN ===
    s = create_surface(32, 32)
    s.fill(palette["dirt_light"])
    
    # Cailloux
    for _ in range(12):
        x, y = random.randint(2, 28), random.randint(2, 28)
        size = random.randint(2, 4)
        pygame.draw.ellipse(s, palette["dirt_dark"], (x, y, size, size - 1))
    
    # Texture
    for _ in range(20):
        x, y = random.randint(0, 30), random.randint(0, 30)
        pygame.draw.rect(s, palette["dirt_dark"], (x, y, 1, 1))
    
    save(s, f"path{suffix}.png")
    
    # === EAU ===
    s = create_surface(32, 32)
    s.fill(palette["water_medium"])
    
    # Dégradé
    for y in range(32):
        alpha = y / 32
        color = (
            int(palette["water_light"][0] * (1 - alpha) + palette["water_dark"][0] * alpha),
            int(palette["water_light"][1] * (1 - alpha) + palette["water_dark"][1] * alpha),
            int(palette["water_light"][2] * (1 - alpha) + palette["water_dark"][2] * alpha),
        )
        pygame.draw.line(s, color, (0, y), (32, y))
    
    # Vagues
    for y in range(4, 28, 8):
        wave_color = (palette["water_light"][0], palette["water_light"][1], palette["water_light"][2], 150)
        for x in range(0, 32, 4):
            pygame.draw.arc(s, wave_color, (x, y, 8, 4), 0, 3.14, 1)
    
    save(s, f"water{suffix}.png")


# =============================================================================
# GÉNÉRATION DES ITEMS
# =============================================================================

def make_items():
    """Génère les sprites d'objets 32x32."""
    print("\n🍎 Génération des items...")
    
    # === POMME ===
    s = create_surface(32, 32)
    # Corps
    pygame.draw.ellipse(s, (220, 50, 50), (6, 8, 20, 20))
    pygame.draw.ellipse(s, (255, 80, 80), (8, 10, 8, 8))  # Reflet
    # Tige
    pygame.draw.line(s, (100, 70, 40), (16, 8), (16, 3), 2)
    # Feuille
    pygame.draw.ellipse(s, (80, 180, 80), (17, 2, 10, 5))
    save(s, "apple.png")
    
    # === CAFÉ ===
    s = create_surface(32, 32)
    # Tasse
    pygame.draw.ellipse(s, (255, 255, 255), (8, 12, 16, 16))
    pygame.draw.rect(s, (255, 255, 255), (8, 12, 16, 10))
    pygame.draw.ellipse(s, (100, 60, 40), (10, 14, 12, 8))  # Café
    # Anse
    pygame.draw.arc(s, (255, 255, 255), (22, 14, 8, 10), -1.57, 1.57, 2)
    # Vapeur
    for i, x in enumerate([12, 16, 20]):
        height = 4 + i % 2 * 2
        pygame.draw.line(s, (200, 200, 200, 150), (x, 10), (x + 1, 10 - height), 1)
    save(s, "coffee.png")


# =============================================================================
# GÉNÉRATION DES MEUBLES
# =============================================================================

def make_furniture():
    """Génère les meubles 64x64."""
    print("\n🛋️ Génération des meubles...")
    
    # === LIT ===
    s = create_surface(64, 64)
    # Structure
    pygame.draw.rect(s, (160, 120, 80), (4, 8, 56, 52))
    pygame.draw.rect(s, (140, 100, 60), (4, 8, 56, 52), 2)
    # Oreiller
    pygame.draw.ellipse(s, (255, 255, 255), (8, 10, 48, 14))
    pygame.draw.ellipse(s, (240, 240, 240), (10, 12, 20, 10))
    pygame.draw.ellipse(s, (240, 240, 240), (34, 12, 20, 10))
    # Couverture
    pygame.draw.rect(s, (80, 120, 180), (6, 26, 52, 32))
    pygame.draw.rect(s, (60, 100, 160), (6, 26, 52, 8))
    save(s, "bed.png")
    
    # === FRIGO ===
    s = create_surface(48, 80)
    pygame.draw.rect(s, (230, 235, 240), (4, 4, 40, 72))
    pygame.draw.line(s, (180, 185, 190), (4, 30), (44, 30), 2)
    pygame.draw.rect(s, (200, 200, 200), (8, 34, 4, 12))  # Poignée bas
    pygame.draw.rect(s, (200, 200, 200), (8, 10, 4, 8))   # Poignée haut
    save(s, "fridge.png")
    
    # === SOFA ===
    s = create_surface(96, 48)
    pygame.draw.rect(s, (100, 80, 140), (4, 16, 88, 28))  # Base
    pygame.draw.rect(s, (120, 100, 160), (8, 8, 80, 16))  # Dossier
    pygame.draw.rect(s, (80, 60, 120), (4, 16, 16, 28))   # Accoudoir G
    pygame.draw.rect(s, (80, 60, 120), (76, 16, 16, 28))  # Accoudoir D
    # Coussins
    pygame.draw.ellipse(s, (130, 110, 170), (22, 18, 24, 20))
    pygame.draw.ellipse(s, (130, 110, 170), (50, 18, 24, 20))
    save(s, "sofa.png")
    
    # === TABLE ===
    s = create_surface(80, 48)
    pygame.draw.rect(s, (160, 120, 80), (4, 4, 72, 40))
    pygame.draw.rect(s, (140, 100, 60), (8, 8, 64, 32))
    save(s, "table.png")
    
    # === CHAISE ===
    s = create_surface(32, 48)
    pygame.draw.rect(s, (160, 120, 80), (6, 24, 20, 20))  # Assise
    pygame.draw.rect(s, (140, 100, 60), (6, 6, 20, 18))   # Dossier
    pygame.draw.rect(s, (120, 80, 40), (8, 44, 4, 4))     # Pied G
    pygame.draw.rect(s, (120, 80, 40), (20, 44, 4, 4))    # Pied D
    save(s, "chair.png")
    
    # === CUISINE ===
    s = create_surface(80, 48)
    pygame.draw.rect(s, (180, 185, 190), (0, 0, 80, 48))
    # Plaques
    pygame.draw.ellipse(s, (40, 40, 50), (10, 20, 20, 16))
    pygame.draw.ellipse(s, (40, 40, 50), (50, 20, 20, 16))
    # Crédence
    pygame.draw.rect(s, (60, 60, 70), (0, 0, 80, 8))
    save(s, "kitchen.png")
    
    # === TOILETTES ===
    s = create_surface(32, 48)
    pygame.draw.rect(s, (255, 255, 255), (8, 4, 16, 12))   # Réservoir
    pygame.draw.ellipse(s, (255, 255, 255), (4, 14, 24, 30))
    pygame.draw.ellipse(s, (220, 225, 230), (8, 20, 16, 18))
    save(s, "toilet.png")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    print("=" * 50)
    print("🎨 GÉNÉRATION DES ASSETS MODERNES")
    print("=" * 50)
    
    # Personnages
    make_player_sprites()
    make_npc_sprites()
    
    # Bâtiments
    make_house()
    make_shop()
    make_office()
    
    # Tuiles (été et hiver)
    make_tiles("summer")
    make_tiles("winter")
    
    # Items
    make_items()
    
    # Meubles
    make_furniture()
    
    print("\n" + "=" * 50)
    print("✅ TOUS LES ASSETS ONT ÉTÉ GÉNÉRÉS !")
    print("=" * 50)
    
    pygame.quit()
