# LifeSim/src/ui/colors.py
"""
Palette de couleurs centralisée pour un design moderne et cohérent.
Inspiré par les jeux modernes comme Stardew Valley et Animal Crossing.
"""

# === COULEURS PRIMAIRES ===
PRIMARY = (99, 102, 241)       # Indigo moderne
SECONDARY = (34, 211, 238)     # Cyan vif
ACCENT = (251, 191, 36)        # Or/Ambre (pour les éléments importants)

# === COULEURS DE STATUT ===
HEALTH = (239, 68, 68)         # Rouge - Santé
HEALTH_GRADIENT = [(239, 68, 68), (185, 28, 28)]  # Gradient santé

ENERGY = (34, 197, 94)         # Vert - Énergie
ENERGY_GRADIENT = [(34, 197, 94), (22, 163, 74)]

HUNGER = (249, 115, 22)        # Orange - Faim
HUNGER_GRADIENT = [(249, 115, 22), (234, 88, 12)]

HAPPINESS = (236, 72, 153)     # Rose - Bonheur
HAPPINESS_GRADIENT = [(236, 72, 153), (219, 39, 119)]

MONEY = (250, 204, 21)         # Or - Argent
XP = (139, 92, 246)            # Violet - Expérience

# === COULEURS DE FOND ===
BG_DARK = (17, 24, 39)         # Fond principal très sombre
BG_PANEL = (31, 41, 55)        # Panneaux/cartes
BG_PANEL_LIGHT = (55, 65, 81)  # Panneaux hover
BG_OVERLAY = (0, 0, 0, 200)    # Overlay semi-transparent

# === COULEURS DE TEXTE ===
TEXT_PRIMARY = (255, 255, 255)     # Blanc
TEXT_SECONDARY = (156, 163, 175)   # Gris clair
TEXT_ACCENT = (251, 191, 36)       # Or
TEXT_SUCCESS = (74, 222, 128)      # Vert succès
TEXT_ERROR = (248, 113, 113)       # Rouge erreur

# === COULEURS D'INTERFACE ===
BORDER_DEFAULT = (75, 85, 99)      # Bordures normales
BORDER_HOVER = (107, 114, 128)     # Bordures hover
BORDER_ACTIVE = (99, 102, 241)     # Bordures actives (primaire)

# === COULEURS PAR CATÉGORIE D'ITEM ===
ITEM_FOOD = (74, 222, 128)         # Vert nourriture
ITEM_DRINK = (96, 165, 250)        # Bleu boisson
ITEM_GIFT = (244, 114, 182)        # Rose cadeau
ITEM_TOOL = (251, 191, 36)         # Or outil

# === COULEURS DE MÉTÉO ===
WEATHER_SUNNY = (250, 204, 21)     # Jaune soleil
WEATHER_CLOUDY = (148, 163, 184)   # Gris nuage
WEATHER_RAINY = (96, 165, 250)     # Bleu pluie
WEATHER_STORMY = (71, 85, 105)     # Gris orage

# === EFFETS VISUELS ===
GLOW_HEALTH = (239, 68, 68, 100)   # Lueur santé faible
GLOW_LEVEL_UP = (250, 204, 21, 150)  # Lueur level up
SHADOW = (0, 0, 0, 100)            # Ombre portée


def lerp_color(color1: tuple, color2: tuple, t: float) -> tuple:
    """Interpole entre deux couleurs. t=0 -> color1, t=1 -> color2"""
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    return (r, g, b)


def with_alpha(color: tuple, alpha: int) -> tuple:
    """Ajoute ou modifie le canal alpha d'une couleur."""
    if len(color) == 4:
        return (color[0], color[1], color[2], alpha)
    return (color[0], color[1], color[2], alpha)


def darken(color: tuple, factor: float = 0.2) -> tuple:
    """Assombrit une couleur."""
    return (
        int(color[0] * (1 - factor)),
        int(color[1] * (1 - factor)),
        int(color[2] * (1 - factor))
    )


def lighten(color: tuple, factor: float = 0.2) -> tuple:
    """Éclaircit une couleur."""
    return (
        min(255, int(color[0] + (255 - color[0]) * factor)),
        min(255, int(color[1] + (255 - color[1]) * factor)),
        min(255, int(color[2] + (255 - color[2]) * factor))
    )
