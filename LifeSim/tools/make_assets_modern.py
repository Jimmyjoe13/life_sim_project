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
import sys

# Ajouter le dossier tools au path pour importer graphics_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graphics_utils import (
    PerlinNoise, 
    DitherPattern,
    apply_dither_gradient,
    create_radial_gradient,
    apply_vertical_gradient,
    apply_noise_texture,
    smooth_edges,
    add_soft_outline,
    create_tile_variation,
    add_detail_pixels
)

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
    """
    Maison moderne 96x96 avec textures avancées.
    
    Améliorations :
    - Texture bois avec Perlin Noise
    - Dégradé sur le toit pour effet 3D
    - Fenêtres avec reflets réalistes
    - Ombre douce au sol
    """
    print("\n🏠 Génération de la maison AMÉLIORÉE...")
    s = create_surface(96, 96)
    
    # Générateur de bruit pour les textures
    wood_noise = PerlinNoise(seed=1234)
    
    # === OMBRE AU SOL (plus douce et réaliste) ===
    # Dégradé radial pour l'ombre
    for y in range(80, 94):
        for x in range(6, 90):
            # Distance au centre de l'ombre
            cx, cy = 48, 87
            dist = math.sqrt((x - cx) ** 2 + ((y - cy) * 2) ** 2)
            max_dist = 45
            
            if dist < max_dist:
                alpha = int(40 * (1 - dist / max_dist))
                current = s.get_at((x, y))
                if current[3] == 0:  # Pixel transparent
                    s.set_at((x, y), (0, 0, 0, alpha))
    
    # === MURS AVEC TEXTURE BOIS ===
    wall_left, wall_top = 12, 40
    wall_width, wall_height = 72, 48
    
    for y in range(wall_top, wall_top + wall_height):
        for x in range(wall_left, wall_left + wall_width):
            # Bruit de Perlin pour variation de couleur
            n = wood_noise.octave(x * 0.1, y * 0.08, octaves=2, persistence=0.6)
            
            # Ombre progressive de gauche à droite
            t = (x - wall_left) / wall_width
            shadow_factor = 0.75 + t * 0.25  # Gauche plus sombre
            
            # Couleur de base interpolée
            base = BUILDING["wood_light"]
            color = (
                max(0, min(255, int(base[0] * shadow_factor + n * 15))),
                max(0, min(255, int(base[1] * shadow_factor + n * 12))),
                max(0, min(255, int(base[2] * shadow_factor + n * 8))),
                255
            )
            s.set_at((x, y), color)
    
    # Lignes horizontales du bardage bois
    for y in range(wall_top + 4, wall_top + wall_height, 6):
        for x in range(wall_left, wall_left + wall_width):
            pixel = s.get_at((x, y))
            darker = (
                max(0, pixel[0] - 25),
                max(0, pixel[1] - 20),
                max(0, pixel[2] - 15),
                255
            )
            s.set_at((x, y), darker)
            # Ligne de highlight juste au-dessus
            if y > wall_top + 4:
                s.set_at((x, y - 1), (
                    min(255, pixel[0] + 10),
                    min(255, pixel[1] + 8),
                    min(255, pixel[2] + 5),
                    255
                ))
    
    # === TOIT AVEC DÉGRADÉ 3D ===
    roof_points = [(4, 42), (48, 8), (92, 42)]
    
    # Dessiner le toit pixel par pixel avec gradient
    for y in range(8, 43):
        for x in range(4, 93):
            # Vérifier si le point est dans le triangle du toit
            # Côté gauche : y = 42 - (42-8)/(48-4) * (x-4) = 42 - 0.77*(x-4)
            # Côté droit : y = 42 - (42-8)/(92-48) * (92-x) = 42 - 0.77*(92-x)
            
            left_edge = 42 - 0.77 * (x - 4)
            right_edge = 42 - 0.77 * (92 - x)
            
            if y >= max(8, min(left_edge, right_edge)) and y <= 42:
                # Position relative dans le toit
                rel_y = (y - 8) / 34  # 0 en haut, 1 en bas
                
                # Côté gauche ou droit ?
                is_left = x < 48
                
                # Gradient de luminosité
                if is_left:
                    # Côté ombré
                    brightness = 0.7 + rel_y * 0.15
                    base = BUILDING["roof_red_dark"]
                else:
                    # Côté éclairé
                    brightness = 0.9 + rel_y * 0.1
                    base = BUILDING["roof_red"]
                
                # Ajouter du bruit subtil
                n = wood_noise.get(x * 0.15, y * 0.15)
                
                color = (
                    max(0, min(255, int(base[0] * brightness + n * 8))),
                    max(0, min(255, int(base[1] * brightness + n * 5))),
                    max(0, min(255, int(base[2] * brightness + n * 3))),
                    255
                )
                s.set_at((x, y), color)
    
    # Texture tuiles améliorée
    for row, y in enumerate(range(14, 42, 5)):
        offset = (row % 2) * 5  # Décalage alterné
        for x in range(8 + offset, 88, 10):
            if s.get_at((x, y))[3] > 0:  # Si on est sur le toit
                # Arc de tuile
                for dx in range(8):
                    dy = int(2 * math.sin(dx * math.pi / 8))
                    px, py = x + dx, y + dy
                    if 0 <= px < 96 and 0 <= py < 96:
                        pixel = s.get_at((px, py))
                        if pixel[3] > 0:
                            # Ombre sous la tuile
                            s.set_at((px, py), (
                                max(0, pixel[0] - 15),
                                max(0, pixel[1] - 10),
                                max(0, pixel[2] - 5),
                                255
                            ))
    
    # === PORTE AVEC VOLUME ===
    door_x, door_y = 38, 56
    door_w, door_h = 20, 32
    
    for y in range(door_y, door_y + door_h):
        for x in range(door_x, door_x + door_w):
            # Gradient horizontal sur la porte
            t = (x - door_x) / door_w
            brightness = 0.7 + t * 0.35
            
            base = BUILDING["door"]
            color = (
                int(base[0] * brightness),
                int(base[1] * brightness),
                int(base[2] * brightness),
                255
            )
            s.set_at((x, y), color)
    
    # Cadre de porte
    pygame.draw.rect(s, (80, 50, 30), (door_x, door_y, door_w, door_h), 1)
    
    # Poignée avec reflet
    pygame.draw.circle(s, (200, 160, 40), (54, 72), 3)
    pygame.draw.circle(s, (255, 220, 100), (53, 71), 1)  # Reflet
    
    # === FENÊTRES AVEC REFLETS ===
    def draw_window(wx, wy, ww, wh):
        # Cadre
        pygame.draw.rect(s, BUILDING["window_frame"], (wx, wy, ww, wh))
        
        # Vitre avec dégradé (reflet du ciel)
        for y in range(wy + 2, wy + wh - 2):
            for x in range(wx + 2, wx + ww - 2):
                t = (y - wy) / wh
                # Dégradé de lumière (plus clair en haut)
                r = int(220 * (1 - t * 0.3) + 180 * t * 0.3)
                g = int(240 * (1 - t * 0.2) + 200 * t * 0.2)
                b = int(255 * (1 - t * 0.1) + 230 * t * 0.1)
                s.set_at((x, y), (r, g, b, 255))
        
        # Croix de fenêtre
        pygame.draw.line(s, BUILDING["window_frame"], 
                        (wx + ww // 2, wy + 2), (wx + ww // 2, wy + wh - 2), 1)
        pygame.draw.line(s, BUILDING["window_frame"],
                        (wx + 2, wy + wh // 2), (wx + ww - 2, wy + wh // 2), 1)
        
        # Rideaux
        curtain_color = (180, 140, 140)
        pygame.draw.rect(s, curtain_color, (wx + 2, wy + 2, 3, wh - 4))
        pygame.draw.rect(s, curtain_color, (wx + ww - 5, wy + 2, 3, wh - 4))
        
        # Reflet diagonal
        pygame.draw.line(s, (255, 255, 255, 100), 
                        (wx + 3, wy + 3), (wx + 6, wy + 6), 1)
    
    # Fenêtre gauche
    draw_window(18, 52, 16, 14)
    # Fenêtre droite  
    draw_window(62, 52, 16, 14)
    
    # === CHEMINÉE AVEC TEXTURE ===
    pygame.draw.rect(s, BUILDING["stone_dark"], (70, 10, 12, 22))
    
    # Briques de cheminée
    for y in range(10, 32, 4):
        offset = 2 if (y // 4) % 2 else 0
        for x in range(70 + offset, 82, 6):
            pygame.draw.rect(s, BUILDING["stone_light"], (x, y, 5, 3))
    
    # Faîte du toit
    pygame.draw.line(s, (60, 30, 20), (48, 8), (48, 8), 2)
    
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
    """
    Génère les tuiles de sol avec techniques avancées.
    
    Nouvelles techniques :
    - Perlin Noise pour variations organiques de couleur
    - Dithering style GBA/Stardew Valley pour transitions
    - Détails procéduraux (brins d'herbe, cailloux, bulles d'eau)
    - Dégradés de profondeur pour l'eau
    """
    print(f"\n🌍 Génération des tuiles AMÉLIORÉES ({season})...")
    
    palette = SUMMER if season == "summer" else WINTER
    suffix = "" if season == "summer" else "_winter"
    
    # Générateur de bruit unique par saison
    base_seed = 42 if season == "summer" else 123
    noise = PerlinNoise(seed=base_seed)
    
    # === HERBE AMÉLIORÉE ===
    # On génère 5 variantes au lieu de 3 pour plus de diversité
    print("  🌿 Génération de l'herbe avec Perlin Noise...")
    
    for variant in range(5):
        s = create_surface(32, 32)
        
        # 1. Base avec gradient de Perlin Noise
        for y in range(32):
            for x in range(32):
                # Valeur de bruit multi-octaves (-1 à 1)
                n = noise.octave(
                    (x + variant * 100) * 0.12,  # Décalage par variante
                    (y + variant * 100) * 0.12,
                    octaves=3,
                    persistence=0.5
                )
                
                # Mapper le bruit sur les 3 teintes d'herbe
                if n < -0.2:
                    base_color = palette["grass_dark"]
                elif n > 0.2:
                    base_color = palette["grass_light"]
                else:
                    base_color = palette["grass_medium"]
                
                # Légère variation de luminosité additionnelle
                brightness = 1.0 + n * 0.15
                color = (
                    max(0, min(255, int(base_color[0] * brightness))),
                    max(0, min(255, int(base_color[1] * brightness))),
                    max(0, min(255, int(base_color[2] * brightness))),
                    255
                )
                s.set_at((x, y), color)
        
        # 2. Brins d'herbe procéduraux (plus réalistes)
        random.seed(base_seed + variant * 50)
        num_blades = random.randint(12, 20)
        
        for _ in range(num_blades):
            bx = random.randint(2, 29)
            by = random.randint(8, 30)  # Commencent plus bas
            height = random.randint(4, 8)
            
            # Courbure du brin
            curve = random.choice([-1, 0, 0, 1])  # Tendance à rester droit
            
            # Couleur du brin (légèrement différente du fond)
            blade_color = random.choice([
                palette["grass_light"],
                (min(255, palette["grass_light"][0] + 20),
                 min(255, palette["grass_light"][1] + 15),
                 palette["grass_light"][2])
            ])
            
            # Dessiner le brin pixel par pixel
            for h in range(height):
                px = bx + (curve * h // 3)
                py = by - h
                if 0 <= px < 32 and 0 <= py < 32:
                    # Fade vers le haut
                    alpha = 255 - (h * 20)
                    s.set_at((px, py), (*blade_color, max(150, alpha)))
        
        # 3. Détails supplémentaires
        # Petits points sombres (terre visible)
        for _ in range(random.randint(3, 8)):
            dx, dy = random.randint(0, 31), random.randint(0, 31)
            dark = (palette["grass_dark"][0] - 20, 
                    palette["grass_dark"][1] - 15,
                    palette["grass_dark"][2] - 10)
            s.set_at((dx, dy), (*[max(0, c) for c in dark], 255))
        
        # Petites fleurs (rare, seulement sur certaines variantes)
        if variant in [1, 3] and season == "summer":
            flower_colors = [
                (255, 220, 100),  # Jaune
                (255, 180, 200),  # Rose
                (200, 180, 255),  # Lavande
            ]
            num_flowers = random.randint(1, 2)
            for _ in range(num_flowers):
                fx, fy = random.randint(4, 27), random.randint(4, 27)
                fc = random.choice(flower_colors)
                # Centre
                pygame.draw.circle(s, fc, (fx, fy), 2)
                # Pétales (4 pixels autour)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    s.set_at((fx + dx * 2, fy + dy * 2), (*fc, 200))
        
        # Sauvegarder
        filename = f"grass{suffix}.png" if variant == 0 else f"grass{suffix}_{variant}.png"
        save(s, filename)
    
    # === CHEMIN / TERRE AMÉLIORÉ ===
    print("  🪨 Génération du chemin avec textures...")
    
    for variant in range(3):
        s = create_surface(32, 32)
        
        # Base avec bruit
        path_noise = PerlinNoise(seed=base_seed + 500 + variant)
        
        for y in range(32):
            for x in range(32):
                n = path_noise.octave(x * 0.15, y * 0.15, octaves=2)
                
                # Interpoler entre les deux couleurs de terre
                t = (n + 1) / 2  # Normaliser 0-1
                color = (
                    int(palette["dirt_light"][0] * (1 - t) + palette["dirt_dark"][0] * t),
                    int(palette["dirt_light"][1] * (1 - t) + palette["dirt_dark"][1] * t),
                    int(palette["dirt_light"][2] * (1 - t) + palette["dirt_dark"][2] * t),
                    255
                )
                s.set_at((x, y), color)
        
        # Cailloux (plus détaillés)
        random.seed(base_seed + 600 + variant)
        num_pebbles = random.randint(8, 15)
        
        for _ in range(num_pebbles):
            px, py = random.randint(2, 28), random.randint(2, 28)
            size = random.randint(2, 4)
            
            # Couleur du caillou (gris variable)
            gray = random.randint(100, 160)
            pebble_color = (gray, gray - 5, gray - 10)
            highlight = (min(255, gray + 30), min(255, gray + 25), min(255, gray + 20))
            
            # Corps du caillou
            pygame.draw.ellipse(s, pebble_color, (px, py, size, size - 1))
            # Reflet
            if size >= 3:
                s.set_at((px + 1, py), highlight)
        
        # Fissures dans le sol
        if variant == 2:
            crack_color = (palette["dirt_dark"][0] - 30,
                          palette["dirt_dark"][1] - 25,
                          palette["dirt_dark"][2] - 20)
            pygame.draw.line(s, crack_color, (5, 10), (12, 18), 1)
            pygame.draw.line(s, crack_color, (20, 5), (25, 15), 1)
        
        filename = f"path{suffix}.png" if variant == 0 else f"path{suffix}_{variant}.png"
        save(s, filename)
    
    # === EAU AMÉLIORÉE (avec dithering et profondeur) ===
    print("  💧 Génération de l'eau avec dithering et vagues...")
    
    for variant in range(3):
        s = create_surface(32, 32)
        
        # 1. Dégradé de base avec dithering (style rétro)
        # Simuler la profondeur : haut = clair (surface), bas = sombre (fond)
        for y in range(32):
            for x in range(32):
                # Position dans le gradient
                t = y / 31
                
                # Seuil de dithering Bayer 4x4
                threshold = DitherPattern.get_threshold(x, y)
                
                # Appliquer le dithering pour transition douce
                if t < threshold * 0.5:
                    color = palette["water_light"]
                elif t < 0.3 + threshold * 0.3:
                    color = palette["water_medium"]
                else:
                    color = palette["water_dark"]
                
                s.set_at((x, y), (*color, 255))
        
        # 2. Ajouter du bruit subtil pour effet de mouvement gelé
        water_noise = PerlinNoise(seed=base_seed + 1000 + variant)
        for y in range(32):
            for x in range(32):
                n = water_noise.get(x * 0.2, y * 0.2)
                pixel = s.get_at((x, y))
                
                # Très légère variation
                variation = int(n * 8)
                new_color = (
                    max(0, min(255, pixel[0] + variation)),
                    max(0, min(255, pixel[1] + variation)),
                    max(0, min(255, pixel[2] + variation)),
                    255
                )
                s.set_at((x, y), new_color)
        
        # 3. Vagues (lignes de reflet)
        wave_positions = [4, 12, 20, 28] if variant == 0 else [6, 14, 22]
        wave_color = (
            min(255, palette["water_light"][0] + 40),
            min(255, palette["water_light"][1] + 30),
            min(255, palette["water_light"][2] + 20),
        )
        
        for wy in wave_positions:
            # Décalage horizontal par variante
            offset = (variant * 3) % 8
            for wx in range(offset, 32, 8):
                # Petite ligne de reflet
                pygame.draw.line(s, wave_color, (wx, wy), (wx + 3, wy), 1)
                # Pixel plus clair au début
                s.set_at((wx, wy), (255, 255, 255, 180))
        
        # 4. Bulles occasionnelles
        if variant == 1:
            bubble_positions = [(8, 20), (22, 12)]
            for bx, by in bubble_positions:
                pygame.draw.circle(s, (200, 230, 255), (bx, by), 2)
                s.set_at((bx, by - 1), (255, 255, 255))  # Reflet
        
        filename = f"water{suffix}.png" if variant == 0 else f"water{suffix}_{variant}.png"
        save(s, filename)
    
    # === TUILE DE SABLE (NOUVEAU) ===
    print("  🏖️ Génération du sable...")
    
    sand_colors = {
        "light": (245, 222, 179),
        "medium": (230, 200, 160),
        "dark": (210, 180, 140)
    }
    
    for variant in range(2):
        s = create_surface(32, 32)
        sand_noise = PerlinNoise(seed=base_seed + 2000 + variant)
        
        for y in range(32):
            for x in range(32):
                n = sand_noise.octave(x * 0.18, y * 0.18, octaves=2)
                
                if n < -0.15:
                    color = sand_colors["dark"]
                elif n > 0.15:
                    color = sand_colors["light"]
                else:
                    color = sand_colors["medium"]
                
                s.set_at((x, y), (*color, 255))
        
        # Grains de sable brillants
        random.seed(base_seed + 2100 + variant)
        for _ in range(random.randint(5, 10)):
            gx, gy = random.randint(0, 31), random.randint(0, 31)
            s.set_at((gx, gy), (255, 250, 230, 255))
        
        filename = f"sand{suffix}.png" if variant == 0 else f"sand{suffix}_{variant}.png"
        save(s, filename)
    
    print(f"  ✨ Tuiles {season} générées avec succès !")


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
