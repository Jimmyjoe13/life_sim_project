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
                        # Falloff quadratique pour un rendu naturel
                        # Plus doux au centre, s'atténue vers les bords
                        t = dist / radius
                        falloff = 1.0 - (t * t)  # Quadratique
                        
                        # Appliquer la couleur avec falloff
                        alpha = int(255 * falloff * 0.8)  # 0.8 pour pas surexposer
                        
                        halo.set_at((x, y), (*color, alpha))
            
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
        Effectue le rendu de l'éclairage sur l'écran (VERSION OPTIMISÉE).
        
        Cette méthode doit être appelée APRÈS le rendu du monde et des sprites,
        mais AVANT le rendu de l'UI.
        
        Technique:
        1. On remplit la surface d'ambiance avec la couleur jour/nuit
        2. On dessine des cercles blancs aux positions des lumières (pour "percer" l'obscurité)
        3. On applique en mode MULTIPLY pour assombrir le tout sauf les zones éclairées
        4. On ajoute les halos colorés en mode ADDITIVE pour l'effet lumineux
        
        Args:
            screen: Surface de destination
            camera_offset: Décalage de la caméra (pour les lumières du monde)
        """
        # === ÉTAPE 1: Préparer la surface d'ambiance ===
        # Calculer la couleur d'ambiance pour le multiply
        ambient_r = int(self.ambient_color[0] * self.ambient_intensity)
        ambient_g = int(self.ambient_color[1] * self.ambient_intensity)
        ambient_b = int(self.ambient_color[2] * self.ambient_intensity)
        
        self.ambient_surface.fill((ambient_r, ambient_g, ambient_b))
        
        # === ÉTAPE 2: "Percer" les zones éclairées (OPTIMISÉ) ===
        # On dessine des cercles plus clairs là où il y a des lumières
        # Utilise des cercles concentriques au lieu de pixel-par-pixel
        
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
            
            # Dessiner des cercles concentriques pour créer le falloff
            # C'est beaucoup plus rapide que pixel-par-pixel !
            num_circles = min(radius // 4, 20)  # Limiter pour performance
            
            for i in range(num_circles, 0, -1):
                # Rayon de ce cercle
                circle_radius = (radius * i) // num_circles
                
                # Falloff quadratique
                t = i / num_circles
                falloff = t * t  # Plus sombre vers l'extérieur
                
                # Couleur pour ce cercle (interpolation vers blanc au centre)
                boost = (1 - falloff) * effective_intensity * 0.7
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
        screen.blit(self.ambient_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        # === ÉTAPE 4: Ajouter les halos lumineux (additif) ===
        # Seulement si l'ambiance est assez sombre
        if self.ambient_intensity > 0.75:
            return  # Pas besoin de halos en plein jour
        
        self.light_surface.fill((0, 0, 0, 0))  # Transparent
        
        for light in self.lights:
            if not light.active:
                continue
            
            # Position
            lx = int(light.x - camera_offset[0])
            ly = int(light.y - camera_offset[1])
            
            # Skip si hors écran
            if lx < -light.radius or lx > self.width + light.radius:
                continue
            if ly < -light.radius or ly > self.height + light.radius:
                continue
            
            # Intensité
            effective_intensity = light.intensity + light._flicker_offset
            effective_intensity = max(0.1, min(1.0, effective_intensity))
            
            # Récupérer le halo pré-rendu (depuis le cache)
            halo = self._get_cached_halo(light.radius, light.color)
            
            # Dessiner le halo (centré sur la position)
            halo_rect = halo.get_rect(center=(lx, ly))
            
            # Appliquer l'intensité en fonction de l'obscurité
            darkness_factor = 1.0 - self.ambient_intensity
            final_alpha = int(255 * effective_intensity * darkness_factor)
            
            scaled_halo = halo.copy()
            scaled_halo.set_alpha(final_alpha)
            self.light_surface.blit(scaled_halo, halo_rect)
        
        # Appliquer les halos en mode additif
        screen.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    
    def render_player_light(self, screen: pygame.Surface, player_pos: Tuple[int, int],
                            radius: int = 80, color: Tuple[int, int, int] = (255, 220, 180)):
        """
        Ajoute un halo de lumière autour du joueur (torche, lanterne, etc.).
        
        Args:
            screen: Surface de destination
            player_pos: Position du joueur (centre)
            radius: Rayon du halo
            color: Couleur de la lumière
        """
        # Seulement la nuit
        if self.ambient_intensity > 0.6:
            return
        
        # Intensité basée sur l'obscurité ambiante
        intensity = 1.0 - self.ambient_intensity
        
        halo = self._get_cached_halo(radius, color)
        halo_copy = halo.copy()
        halo_copy.set_alpha(int(200 * intensity))
        
        halo_rect = halo_copy.get_rect(center=player_pos)
        screen.blit(halo_copy, halo_rect, special_flags=pygame.BLEND_RGBA_ADD)
    
    def is_night(self) -> bool:
        """Retourne True si c'est la nuit (faible luminosité)."""
        return self.ambient_intensity < 0.5
    
    def get_ambient_intensity(self) -> float:
        """Retourne l'intensité ambiante actuelle (0-1)."""
        return self.ambient_intensity


# =============================================================================
# PRESETS DE LUMIÈRES POUR PLACEMENT FACILE
# =============================================================================

def create_streetlamp(lighting: LightingSystem, x: float, y: float) -> LightSource:
    """Crée un lampadaire avec lumière jaune-orange."""
    return lighting.add_light(
        x, y, radius=120,
        color=(255, 220, 150),
        intensity=0.9,
        flicker=True
    )


def create_window_light(lighting: LightingSystem, x: float, y: float) -> LightSource:
    """Crée une fenêtre éclairée avec lumière chaude."""
    return lighting.add_light(
        x, y, radius=60,
        color=(255, 200, 120),
        intensity=0.7,
        light_type=LightType.WINDOW
    )


def create_campfire(lighting: LightingSystem, x: float, y: float) -> LightSource:
    """Crée un feu de camp avec vacillement prononcé."""
    return lighting.add_light(
        x, y, radius=100,
        color=(255, 150, 50),
        intensity=0.85,
        flicker=True
    )
    # Augmenter le vacillement
    light = lighting.lights[-1]
    light.flicker_speed = 0.15
    light.flicker_amount = 0.35
    return light


def create_torch(lighting: LightingSystem, x: float, y: float) -> LightSource:
    """Crée une torche murale."""
    return lighting.add_light(
        x, y, radius=70,
        color=(255, 180, 80),
        intensity=0.75,
        flicker=True
    )
