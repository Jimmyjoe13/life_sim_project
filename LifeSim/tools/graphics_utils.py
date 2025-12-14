# LifeSim/tools/graphics_utils.py
"""
Utilitaires graphiques avancés pour la génération de sprites.
Techniques : Perlin Noise, Dithering, Gradients, Anti-aliasing.

Ces fonctions transforment des sprites "plats" en textures organiques
dignes d'un jeu indé commercial (style Stardew Valley).
"""

import pygame
import math
import random
from typing import Tuple, List, Optional

# =============================================================================
# PERLIN NOISE - Génère des variations naturelles et continues
# =============================================================================
# Le Perlin Noise utilise des vecteurs de gradient interpolés pour créer
# un bruit "cohérent" où les valeurs voisines sont proches les unes des autres.
# Contrairement au random pur qui donne un effet "neige de TV", le Perlin
# crée des ondulations naturelles parfaites pour l'herbe, l'eau, les nuages.

class PerlinNoise:
    """
    Générateur de bruit de Perlin 2D simplifié.
    
    Usage:
        noise = PerlinNoise(seed=42)
        value = noise.get(x * 0.1, y * 0.1)  # Valeur entre -1 et 1
    """
    
    def __init__(self, seed: int = 0):
        random.seed(seed)
        # Table de permutation (shuffle des indices 0-255)
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm += self.perm  # Double pour éviter overflow
        
        # Vecteurs de gradient pré-calculés
        self.gradients = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (-1, 1), (1, -1), (-1, -1)
        ]
    
    def _fade(self, t: float) -> float:
        """Courbe de lissage 6t^5 - 15t^4 + 10t^3 (Perlin amélioré)."""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Interpolation linéaire."""
        return a + t * (b - a)
    
    def _dot_grid_gradient(self, ix: int, iy: int, x: float, y: float) -> float:
        """Produit scalaire entre vecteur de distance et gradient."""
        # Sélection du gradient basée sur les coordonnées
        idx = self.perm[self.perm[ix & 255] + (iy & 255)] % len(self.gradients)
        gx, gy = self.gradients[idx]
        
        # Vecteur de distance
        dx, dy = x - ix, y - iy
        
        return dx * gx + dy * gy
    
    def get(self, x: float, y: float) -> float:
        """
        Retourne la valeur de bruit à la position (x, y).
        Résultat normalisé entre -1 et 1.
        """
        # Coordonnées de la cellule
        x0, y0 = int(math.floor(x)), int(math.floor(y))
        x1, y1 = x0 + 1, y0 + 1
        
        # Position relative dans la cellule
        sx = self._fade(x - x0)
        sy = self._fade(y - y0)
        
        # Interpolation des 4 coins
        n0 = self._dot_grid_gradient(x0, y0, x, y)
        n1 = self._dot_grid_gradient(x1, y0, x, y)
        ix0 = self._lerp(n0, n1, sx)
        
        n0 = self._dot_grid_gradient(x0, y1, x, y)
        n1 = self._dot_grid_gradient(x1, y1, x, y)
        ix1 = self._lerp(n0, n1, sx)
        
        return self._lerp(ix0, ix1, sy)
    
    def octave(self, x: float, y: float, octaves: int = 4, persistence: float = 0.5) -> float:
        """
        Bruit multi-octaves (fBm - Fractional Brownian Motion).
        Superpose plusieurs couches de bruit à différentes fréquences.
        
        - octaves: nombre de couches (plus = plus de détail)
        - persistence: perte d'amplitude par octave (0.5 = moitié)
        """
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        for _ in range(octaves):
            total += self.get(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2
        
        return total / max_value  # Normalisation


# =============================================================================
# DITHERING - Motifs de tramage style pixel art / GBA
# =============================================================================
# Le dithering crée des transitions de couleur en alternant des pixels
# de différentes couleurs selon un motif. C'est LA technique signature
# des jeux 16-bit et des jeux indie modernes qui s'en inspirent.

class DitherPattern:
    """Motifs de dithering classiques."""
    
    # Matrice de Bayer 4x4 (valeurs 0-15, normalisées ensuite)
    BAYER_4X4 = [
        [0,  8,  2,  10],
        [12, 4,  14, 6],
        [3,  11, 1,  9],
        [15, 7,  13, 5]
    ]
    
    # Motif en damier simple
    CHECKER = [
        [0, 1],
        [1, 0]
    ]
    
    @staticmethod
    def get_threshold(x: int, y: int, pattern: List[List[int]] = None) -> float:
        """
        Retourne le seuil de dithering pour une position (x, y).
        Valeur entre 0 et 1.
        """
        if pattern is None:
            pattern = DitherPattern.BAYER_4X4
        
        size = len(pattern)
        px, py = x % size, y % size
        max_val = size * size - 1
        
        return pattern[py][px] / max_val


def apply_dither_gradient(surface: pygame.Surface, 
                          color1: Tuple[int, int, int], 
                          color2: Tuple[int, int, int],
                          direction: str = "vertical",
                          pattern: List[List[int]] = None) -> pygame.Surface:
    """
    Applique un dégradé avec dithering sur une surface.
    
    Args:
        surface: Surface source (doit avoir de l'alpha)
        color1: Couleur de départ (RGB)
        color2: Couleur d'arrivée (RGB)
        direction: "vertical", "horizontal", ou "radial"
        pattern: Matrice de dithering (défaut: Bayer 4x4)
    
    Returns:
        Nouvelle surface avec dégradé dithered
    """
    if pattern is None:
        pattern = DitherPattern.BAYER_4X4
    
    w, h = surface.get_size()
    result = surface.copy()
    
    for y in range(h):
        for x in range(w):
            # Récupérer le pixel original
            pixel = surface.get_at((x, y))
            if pixel[3] == 0:  # Ignorer les pixels transparents
                continue
            
            # Calculer la position dans le gradient (0 à 1)
            if direction == "vertical":
                t = y / max(1, h - 1)
            elif direction == "horizontal":
                t = x / max(1, w - 1)
            else:  # radial
                cx, cy = w / 2, h / 2
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                max_dist = math.sqrt(cx ** 2 + cy ** 2)
                t = min(1.0, dist / max_dist)
            
            # Seuil de dithering
            threshold = DitherPattern.get_threshold(x, y, pattern)
            
            # Choisir la couleur selon le seuil
            if t < threshold:
                new_color = color1
            else:
                new_color = color2
            
            # Appliquer en préservant l'alpha original
            result.set_at((x, y), (*new_color, pixel[3]))
    
    return result


# =============================================================================
# GRADIENTS LISSES - Pour effets de volume et lumière
# =============================================================================

def create_radial_gradient(size: int, 
                           center_color: Tuple[int, int, int, int],
                           edge_color: Tuple[int, int, int, int],
                           center: Tuple[float, float] = (0.5, 0.5)) -> pygame.Surface:
    """
    Crée une surface avec un dégradé radial (cercle de lumière).
    
    Args:
        size: Taille de la surface carrée
        center_color: Couleur RGBA au centre
        edge_color: Couleur RGBA sur les bords
        center: Position relative du centre (0-1, 0-1)
    
    Returns:
        Surface avec dégradé radial
    """
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = int(size * center[0]), int(size * center[1])
    max_radius = math.sqrt((size/2) ** 2 + (size/2) ** 2)
    
    for y in range(size):
        for x in range(size):
            # Distance au centre normalisée
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            t = min(1.0, dist / max_radius)
            
            # Courbe de falloff douce (ease-out)
            t = 1 - (1 - t) ** 2
            
            # Interpolation des couleurs
            r = int(center_color[0] * (1 - t) + edge_color[0] * t)
            g = int(center_color[1] * (1 - t) + edge_color[1] * t)
            b = int(center_color[2] * (1 - t) + edge_color[2] * t)
            a = int(center_color[3] * (1 - t) + edge_color[3] * t)
            
            surface.set_at((x, y), (r, g, b, a))
    
    return surface


def apply_vertical_gradient(surface: pygame.Surface,
                            top_factor: float = 1.2,
                            bottom_factor: float = 0.7) -> pygame.Surface:
    """
    Applique un gradient vertical de luminosité (lumière du haut).
    Simule une source de lumière au-dessus de l'objet.
    
    Args:
        surface: Surface source
        top_factor: Multiplicateur de luminosité en haut (>1 = plus clair)
        bottom_factor: Multiplicateur en bas (<1 = plus sombre)
    
    Returns:
        Surface avec gradient appliqué
    """
    w, h = surface.get_size()
    result = surface.copy()
    
    for y in range(h):
        # Facteur de luminosité pour cette ligne
        t = y / max(1, h - 1)
        factor = top_factor * (1 - t) + bottom_factor * t
        
        for x in range(w):
            pixel = surface.get_at((x, y))
            if pixel[3] == 0:
                continue
            
            new_color = (
                min(255, int(pixel[0] * factor)),
                min(255, int(pixel[1] * factor)),
                min(255, int(pixel[2] * factor)),
                pixel[3]
            )
            result.set_at((x, y), new_color)
    
    return result


# =============================================================================
# APPLICATION DE BRUIT SUR TEXTURE
# =============================================================================

def apply_noise_texture(surface: pygame.Surface,
                        noise: PerlinNoise,
                        scale: float = 0.15,
                        intensity: float = 0.3,
                        color_variation: bool = True) -> pygame.Surface:
    """
    Applique du bruit de Perlin sur une surface existante.
    Casse l'effet "plastique" des couleurs unies.
    
    Args:
        surface: Surface source
        noise: Instance de PerlinNoise
        scale: Échelle du bruit (plus petit = plus de détail)
        intensity: Force de l'effet (0-1)
        color_variation: Si True, varie aussi légèrement la teinte
    
    Returns:
        Surface avec texture de bruit
    """
    w, h = surface.get_size()
    result = surface.copy()
    
    for y in range(h):
        for x in range(w):
            pixel = surface.get_at((x, y))
            if pixel[3] == 0:
                continue
            
            # Valeur de bruit à cette position
            n = noise.octave(x * scale, y * scale, octaves=3, persistence=0.5)
            
            # Variation de luminosité
            brightness_mod = 1.0 + (n * intensity)
            
            # Variation de teinte optionnelle (très subtile)
            hue_shift = n * 0.05 if color_variation else 0
            
            new_color = (
                max(0, min(255, int(pixel[0] * brightness_mod + hue_shift * 20))),
                max(0, min(255, int(pixel[1] * brightness_mod))),
                max(0, min(255, int(pixel[2] * brightness_mod - hue_shift * 10))),
                pixel[3]
            )
            result.set_at((x, y), new_color)
    
    return result


# =============================================================================
# ANTI-ALIASING MANUEL
# =============================================================================

def smooth_edges(surface: pygame.Surface, iterations: int = 1) -> pygame.Surface:
    """
    Lisse les bords des sprites en ajoutant des pixels semi-transparents.
    
    Args:
        surface: Surface avec transparence
        iterations: Nombre de passes de lissage
    
    Returns:
        Surface avec bords adoucis
    """
    w, h = surface.get_size()
    result = surface.copy()
    
    for _ in range(iterations):
        temp = result.copy()
        
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                pixel = temp.get_at((x, y))
                
                # Ignorer les pixels opaques ou transparents
                if pixel[3] == 255 or pixel[3] == 0:
                    continue
                
                # Moyenner avec les voisins
                neighbors = [
                    temp.get_at((x-1, y)),
                    temp.get_at((x+1, y)),
                    temp.get_at((x, y-1)),
                    temp.get_at((x, y+1))
                ]
                
                total_a = sum(n[3] for n in neighbors)
                if total_a > 0:
                    avg_r = sum(n[0] * n[3] for n in neighbors) // total_a
                    avg_g = sum(n[1] * n[3] for n in neighbors) // total_a
                    avg_b = sum(n[2] * n[3] for n in neighbors) // total_a
                    avg_a = total_a // 4
                    
                    result.set_at((x, y), (avg_r, avg_g, avg_b, min(pixel[3], avg_a)))
        
    return result


def add_soft_outline(surface: pygame.Surface, 
                     color: Tuple[int, int, int] = (0, 0, 0),
                     thickness: int = 1,
                     alpha: int = 180) -> pygame.Surface:
    """
    Ajoute un contour doux (semi-transparent) autour du sprite.
    Plus professionnel qu'un outline noir dur.
    
    Args:
        surface: Surface source
        color: Couleur du contour RGB
        thickness: Épaisseur en pixels
        alpha: Transparence du contour (0-255)
    
    Returns:
        Nouvelle surface avec contour
    """
    w, h = surface.get_size()
    # Surface plus grande pour accueillir le contour
    result = pygame.Surface((w + thickness * 2, h + thickness * 2), pygame.SRCALPHA)
    
    # Dessiner le contour d'abord (décalé dans toutes les directions)
    for dy in range(-thickness, thickness + 1):
        for dx in range(-thickness, thickness + 1):
            if dx == 0 and dy == 0:
                continue
            # Distance au centre pour falloff
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > thickness:
                continue
            
            # Alpha basé sur la distance
            local_alpha = int(alpha * (1 - dist / (thickness + 1)))
            
            # Créer une version colorée semi-transparente
            outline_layer = pygame.Surface((w, h), pygame.SRCALPHA)
            for y in range(h):
                for x in range(w):
                    pixel = surface.get_at((x, y))
                    if pixel[3] > 128:
                        outline_layer.set_at((x, y), (*color, local_alpha))
            
            result.blit(outline_layer, (thickness + dx, thickness + dy))
    
    # Dessiner le sprite par-dessus
    result.blit(surface, (thickness, thickness))
    
    return result


# =============================================================================
# HELPERS POUR GÉNÉRATION DE TILES
# =============================================================================

def create_tile_variation(base_surface: pygame.Surface,
                          seed: int,
                          noise_scale: float = 0.2,
                          noise_intensity: float = 0.25) -> pygame.Surface:
    """
    Crée une variation d'une tuile de base en appliquant du bruit.
    
    Args:
        base_surface: Tuile de base
        seed: Graine pour le bruit (différent = variation différente)
        noise_scale: Échelle du bruit
        noise_intensity: Intensité de l'effet
    
    Returns:
        Nouvelle tuile avec variations
    """
    noise = PerlinNoise(seed)
    return apply_noise_texture(base_surface, noise, noise_scale, noise_intensity)


def add_detail_pixels(surface: pygame.Surface,
                      detail_colors: List[Tuple[int, int, int]],
                      density: float = 0.1,
                      seed: int = 0) -> pygame.Surface:
    """
    Ajoute des pixels de détail aléatoires (brins d'herbe, grains de sable...).
    
    Args:
        surface: Surface de base
        detail_colors: Liste de couleurs possibles pour les détails
        density: Probabilité qu'un pixel ait un détail (0-1)
        seed: Graine aléatoire
    
    Returns:
        Surface avec détails ajoutés
    """
    random.seed(seed)
    w, h = surface.get_size()
    result = surface.copy()
    
    for y in range(h):
        for x in range(w):
            if random.random() < density:
                pixel = surface.get_at((x, y))
                if pixel[3] > 0:  # Seulement sur pixels visibles
                    color = random.choice(detail_colors)
                    result.set_at((x, y), (*color, pixel[3]))
    
    return result


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Graphics Utils Test")
    
    # Test du Perlin Noise
    noise = PerlinNoise(seed=42)
    noise_surface = pygame.Surface((200, 200))
    
    for y in range(200):
        for x in range(200):
            value = noise.octave(x * 0.05, y * 0.05, octaves=4)
            gray = int((value + 1) * 127.5)  # Normaliser -1..1 vers 0..255
            noise_surface.set_at((x, y), (gray, gray, gray))
    
    # Test dégradé radial
    gradient = create_radial_gradient(100, (255, 200, 100, 255), (0, 0, 0, 0))
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((40, 40, 40))
        screen.blit(noise_surface, (10, 10))
        screen.blit(gradient, (220, 10))
        
        pygame.display.flip()
    
    pygame.quit()
    print("✅ Test graphics_utils terminé !")
