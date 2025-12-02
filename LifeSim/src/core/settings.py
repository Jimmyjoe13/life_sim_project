# src/core/settings.py

# Affichage
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Python Life Sim MVP"

# Couleurs (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
UI_BG_COLOR = (50, 50, 50)
BAR_COLOR_HEALTH = (200, 50, 50)
BAR_COLOR_ENERGY = (50, 200, 50)

# Gameplay
TIME_SPEED = 1.0       # Multiplicateur de vitesse
DECAY_HUNGER = 0.5     # Perte de faim par seconde
DECAY_ENERGY = 0.2     # Perte d'énergie par seconde
STARTING_MONEY = 100