# src/core/lighting.py
"""
Système d'éclairage dynamique pour LifeSim.

Ce module gère :
- L'ambiance lumineuse globale (cycle jour/nuit)
- Les sources de lumière ponctuelles (lampadaires, fenêtres, torches)
- Les halos autour des entités (joueur la nuit)
- Les ombres portées basiques

Techniques utilisées :
- BLEND_RGBA_MULT : Pour l'assombrissement global (nuit)
- BLEND_RGBA_ADD : Pour les sources de lumière (additif)
- Dégradés radiaux pré-calculés : Pour les halos de lumière
"""

import pygame
import math
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum


class LightType(Enum):
    """Types de sources lumineuses."""
    POINT = "point"         # Lumière ponctuelle (lampadaire, torche)
    SPOT = "spot"           # Lumière directionnelle (projecteur)
    AMBIENT = "ambient"     # Lumière d'ambiance (soleil, lune)
    WINDOW = "window"       # Fenêtre éclairée (rectangle lumineux)


@dataclass
class LightSource:
    """
    Représente une source de lumière dans le monde.
    
    Attributes:
        x, y: Position de la source (centre)
        radius: Rayon d'effet de la lumière en pixels
        color: Couleur RGB de la lumière
        intensity: Intensité (0.0 à 1.0)
        light_type: Type de lumière
        active: Si la lumière est active
        flicker: Si la lumière vacille (torche, bougie)
        flicker_speed: Vitesse de vacillement
    """
    x: float
    y: float
    radius: int
    color: Tuple[int, int, int] = (255, 200, 150)  # Blanc chaud par défaut
    intensity: float = 1.0
    light_type: LightType = LightType.POINT
    active: bool = True
    flicker: bool = False
    flicker_speed: float = 0.1
    flicker_amount: float = 0.2
    
    # État interne pour le vacillement
    _flicker_offset: float = 0.0


class LightingSystem:
    """
    Système d'éclairage dynamique.
    
    Gère l'ambiance lumineuse et les sources de lumière ponctuelles.
    
    Usage:
        lighting = LightingSystem(800, 600)
        lighting.add_light(400, 300, 100, (255, 200, 150))
        
        # Dans la boucle de rendu:
        lighting.update(dt, time_manager)
        lighting.render(screen)
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        
        # Surface d'éclairage principal (mode multiply pour assombrir)
        self.ambient_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        # Surface pour les lumières additives
        self.light_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        # Liste des sources de lumière
        self.lights: List[LightSource] = []
        
        # Lumière ambiante courante (couleur et intensité)
        self.ambient_color = (255, 255, 255)  # Plein jour
        self.ambient_intensity = 1.0
        
        # Cache des halos pré-rendus (pour performance)
        self._light_cache: Dict[Tuple[int, Tuple[int, int, int]], pygame.Surface] = {}
        
        # Configuration du cycle jour/nuit
        self.day_colors = {
            # Heure: (R, G, B, intensité)
            0: (20, 25, 60, 0.15),      # Minuit - très sombre, bleu profond
            4: (40, 50, 80, 0.25),      # Avant l'aube
            6: (180, 140, 100, 0.6),    # Lever du soleil - doré
            8: (255, 250, 240, 1.0),    # Matin - lumière chaude
            12: (255, 255, 255, 1.0),   # Midi - plein soleil
            16: (255, 245, 230, 0.95),  # Après-midi
            18: (255, 180, 120, 0.7),   # Coucher de soleil - orange
            20: (100, 80, 120, 0.35),   # Crépuscule - violet
            22: (30, 35, 70, 0.2),      # Nuit
        }
        
        # Timer pour le vacillement
        self._time = 0.0
    
    def add_light(self, x: float, y: float, radius: int, 
                  color: Tuple[int, int, int] = (255, 200, 150),
                  intensity: float = 1.0,
                  light_type: LightType = LightType.POINT,
                  flicker: bool = False) -> LightSource:
        """
        Ajoute une source de lumière au système.
        
        Args:
            x, y: Position de la lumière
            radius: Rayon d'effet en pixels
            color: Couleur RGB
            intensity: Intensité (0-1)
            light_type: Type de lumière
            flicker: Si la lumière vacille
        
        Returns:
            La source de lumière créée
        """
        light = LightSource(
            x=x, y=y, radius=radius, color=color,
            intensity=intensity, light_type=light_type,
            flicker=flicker
        )
        self.lights.append(light)
        return light
    
    def remove_light(self, light: LightSource):
        """Retire une source de lumière."""
        if light in self.lights:
            self.lights.remove(light)
    
    def clear_lights(self):
        """Retire toutes les lumières."""
        self.lights.clear()
    
    def _get_cached_halo(self, radius: int, color: Tuple[int, int, int]) -> pygame.Surface:
        """
        Récupère ou génère un halo de lumière (pré-rendu pour performance).
        
        RECALIBRÉ : Halos plus subtils et réalistes.
        
        Args:
            radius: Rayon du halo
            color: Couleur de la lumière
        
        Returns:
            Surface avec le halo pré-rendu
        """
        cache_key = (radius, color)
        
        if cache_key not in self._light_cache:
            # Créer le halo
            size = radius * 2
            halo = pygame.Surface((size, size), pygame.SRCALPHA)
            center = radius
            
            for y in range(size):
                for x in range(size):
                    # Distance au centre
                    dx, dy = x - center, y - center
                    dist = math.sqrt(dx * dx + dy * dy)
                    
                    if dist < radius:
                        # Falloff CUBIQUE pour un dégradé très doux
                        # Plus naturel que quadratique
                        t = dist / radius
                        falloff = (1.0 - t) ** 3  # Cubique - beaucoup plus doux
                        
                        # Alpha très réduit pour éviter la saturation
                        # Max alpha = 80 au lieu de 200+
                        alpha = int(80 * falloff)
                        
                        # Réduire aussi l'intensité de la couleur
                        r = int(color[0] * 0.7)
                        g = int(color[1] * 0.6)
                        b = int(color[2] * 0.5)
                        
                        halo.set_at((x, y), (r, g, b, alpha))
            
            self._light_cache[cache_key] = halo
        
        return self._light_cache[cache_key]
    
    def _interpolate_color(self, hour: float) -> Tuple[Tuple[int, int, int], float]:
        """
        Interpole la couleur ambiante en fonction de l'heure.
        
        Args:
            hour: Heure actuelle (0-24, peut être décimale)
        
        Returns:
            (couleur RGB, intensité)
        """
        # Trouver les deux heures encadrantes
        hours = sorted(self.day_colors.keys())
        
        prev_hour = hours[-1]  # Dernier si on boucle
        next_hour = hours[0]
        
        for i, h in enumerate(hours):
            if h > hour:
                next_hour = h
                prev_hour = hours[i - 1] if i > 0 else hours[-1]
                break
        else:
            # Après la dernière heure définie, interpoler vers minuit
            prev_hour = hours[-1]
            next_hour = hours[0]
        
        # Calcul du facteur d'interpolation
        if next_hour > prev_hour:
            t = (hour - prev_hour) / (next_hour - prev_hour)
        else:
            # Transition minuit
            if hour >= prev_hour:
                t = (hour - prev_hour) / (24 - prev_hour + next_hour)
            else:
                t = (hour + 24 - prev_hour) / (24 - prev_hour + next_hour)
        
        t = max(0, min(1, t))  # Clamp
        
        # Récupérer les couleurs
        prev_color = self.day_colors[prev_hour]
        next_color = self.day_colors[next_hour]
        
        # Interpolation linéaire
        r = int(prev_color[0] * (1 - t) + next_color[0] * t)
        g = int(prev_color[1] * (1 - t) + next_color[1] * t)
        b = int(prev_color[2] * (1 - t) + next_color[2] * t)
        intensity = prev_color[3] * (1 - t) + next_color[3] * t
        
        return (r, g, b), intensity
    
    def update(self, dt: float, time_manager=None, hour: float = None):
        """
        Met à jour le système d'éclairage.
        
        Args:
            dt: Delta time en secondes
            time_manager: Gestionnaire de temps du jeu (optionnel)
            hour: Heure actuelle si pas de time_manager
        """
        self._time += dt
        
        # Récupérer l'heure
        if time_manager:
            current_hour = time_manager.minutes / 60.0
        elif hour is not None:
            current_hour = hour
        else:
            current_hour = 12.0  # Midi par défaut
        
        # Mettre à jour l'ambiance
        self.ambient_color, self.ambient_intensity = self._interpolate_color(current_hour)
        
        # Mettre à jour le vacillement des lumières
        for light in self.lights:
            if light.flicker and light.active:
                # Variation sinusoïdale + bruit
                noise = math.sin(self._time * light.flicker_speed * 20) * 0.5
                noise += math.sin(self._time * light.flicker_speed * 37) * 0.3
                noise += math.sin(self._time * light.flicker_speed * 53) * 0.2
                
                light._flicker_offset = noise * light.flicker_amount
    
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Effectue le rendu de l'éclairage sur l'écran.
        
        NOUVELLE APPROCHE (style Stardew Valley) :
        - Pas de halos colorés additifs
        - On crée une couche sombre et on "perce" des trous dedans
        - Les lumières révèlent simplement le monde en-dessous
        
        Args:
            screen: Surface de destination
            camera_offset: Décalage de la caméra
        """
        # Si c'est le plein jour, pas besoin d'éclairage
        if self.ambient_intensity >= 0.95:
            return
        
        # === ÉTAPE 1: Créer la couche sombre ===
        # Couleur d'ambiance (plus sombre = plus bleu nuit)
        ambient_r = int(self.ambient_color[0] * self.ambient_intensity)
        ambient_g = int(self.ambient_color[1] * self.ambient_intensity)
        ambient_b = int(self.ambient_color[2] * self.ambient_intensity)
        
        self.ambient_surface.fill((ambient_r, ambient_g, ambient_b))
        
        # === ÉTAPE 2: "Percer" les zones éclairées ===
        # On dessine des cercles plus clairs (vers blanc) pour révéler le monde
        
        for light in self.lights:
            if not light.active:
                continue
            
            # Position avec offset caméra
            lx = int(light.x - camera_offset[0])
            ly = int(light.y - camera_offset[1])
            
            # Skip si hors écran
            if lx < -light.radius or lx > self.width + light.radius:
                continue
            if ly < -light.radius or ly > self.height + light.radius:
                continue
            
            # Intensité effective (avec vacillement)
            effective_intensity = light.intensity + light._flicker_offset
            effective_intensity = max(0.1, min(1.0, effective_intensity))
            
            # Rayon effectif
            radius = int(light.radius * effective_intensity)
            
            # Nombre de cercles pour le dégradé (plus = plus lisse)
            num_circles = min(radius // 3, 25)
            
            if num_circles < 3:
                num_circles = 3
            
            # Dessiner des cercles du plus grand au plus petit
            for i in range(num_circles, 0, -1):
                # Rayon de ce cercle (du plus grand au plus petit)
                circle_radius = (radius * i) // num_circles
                
                # Facteur de progression (0 au bord, 1 au centre)
                t = 1.0 - (i / num_circles)
                
                # Falloff cubique pour un dégradé doux
                falloff = t ** 2.5
                
                # Calculer la couleur : interpoler de ambient vers blanc
                # Plus on est proche du centre, plus c'est clair
                boost = falloff * effective_intensity
                
                # La couleur tend vers le blanc (255, 255, 255) au centre
                circle_r = min(255, int(ambient_r + (255 - ambient_r) * boost))
                circle_g = min(255, int(ambient_g + (255 - ambient_g) * boost))
                circle_b = min(255, int(ambient_b + (255 - ambient_b) * boost))
                
                pygame.draw.circle(
                    self.ambient_surface,
                    (circle_r, circle_g, circle_b),
                    (lx, ly),
                    circle_radius
                )
        
        # === ÉTAPE 3: Appliquer l'ambiance avec BLEND_MULT ===
        # Cela assombrit tout SAUF les zones où on a mis du blanc
        screen.blit(self.ambient_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        # PAS D'ÉTAPE 4 : On ne rajoute PAS de halos colorés
        # Le résultat est un éclairage subtil style Stardew Valley
    
    def render_player_light(self, screen: pygame.Surface, player_pos: Tuple[int, int],
                            radius: int = 60, color: Tuple[int, int, int] = (255, 200, 150)):
        """
        Désactivé pour éviter les halos colorés.
        La lumière du joueur est maintenant gérée comme une source de lumière normale.
        """
        # DÉSACTIVÉ - Pas de halo additionnel autour du joueur
        # Pour activer une lumière autour du joueur, ajouter une LightSource dynamique
        pass
    
    def is_night(self) -> bool:
        """Retourne True si c'est la nuit (faible luminosité)."""
        return self.ambient_intensity < 0.5
    
    def get_ambient_intensity(self) -> float:
        """Retourne l'intensité ambiante actuelle (0-1)."""
        return self.ambient_intensity


# =============================================================================
# PRESETS DE LUMIÈRES POUR PLACEMENT FACILE
# RAYONS AUGMENTÉS pour des zones éclairées plus grandes
# =============================================================================

def create_streetlamp(lighting: LightingSystem, x: float, y: float) -> LightSource:
    """
    Crée un lampadaire avec une grande zone de lumière.
    """
    return lighting.add_light(
        x, y, radius=150,  # AUGMENTÉ : 70 → 150
        color=(255, 200, 120),
        intensity=0.85,  # AUGMENTÉ : 0.6 → 0.85
        flicker=True
    )


def create_window_light(lighting: LightingSystem, x: float, y: float) -> LightSource:
    """
    Crée une fenêtre éclairée avec lumière chaude.
    """
    return lighting.add_light(
        x, y, radius=80,  # AUGMENTÉ : 40 → 80
        color=(255, 180, 100),
        intensity=0.7,  # AUGMENTÉ : 0.5 → 0.7
        light_type=LightType.WINDOW
    )


def create_campfire(lighting: LightingSystem, x: float, y: float) -> LightSource:
    """Crée un feu de camp avec vacillement prononcé."""
    light = lighting.add_light(
        x, y, radius=130,  # AUGMENTÉ : 80 → 130
        color=(255, 140, 40),
        intensity=0.85,  # AUGMENTÉ : 0.7 → 0.85
        flicker=True
    )
    # Augmenter le vacillement
    light.flicker_speed = 0.15
    light.flicker_amount = 0.25
    return light


def create_torch(lighting: LightingSystem, x: float, y: float) -> LightSource:
    """Crée une torche murale."""
    return lighting.add_light(
        x, y, radius=50,  # Réduit de 70 à 50
        color=(255, 160, 60),
        intensity=0.55,  # Réduit de 0.75 à 0.55
        flicker=True
    )
