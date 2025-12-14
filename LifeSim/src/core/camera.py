# src/core/camera.py
"""
Système de Caméra avec Y-Sort pour LifeSim.

Ce module gère :
- Le scrolling de la caméra (monde plus grand que l'écran)
- Le suivi fluide du joueur (lerp)
- Le tri Y-Sort pour la profondeur 2.5D
- Les limites de la carte (la caméra ne sort pas du monde)

Le Y-Sort est LA technique qui donne l'impression de profondeur dans les jeux
2D top-down comme Stardew Valley, Zelda: A Link to the Past, etc.

Principe : Les sprites sont dessinés du haut vers le bas de l'écran.
Un sprite plus bas sur l'écran est dessiné PAR-DESSUS ceux qui sont plus haut.
Ainsi, un personnage "devant" un arbre (plus bas sur l'écran) le cache.
"""

import pygame
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class CameraBounds:
    """Limites de la caméra dans le monde."""
    left: float = 0
    top: float = 0
    right: float = 0
    bottom: float = 0


class YSortSprite:
    """
    Interface pour les sprites qui doivent être triés en Y.
    
    Tout objet dessinable qui doit participer au Y-Sort doit avoir :
    - rect: pygame.Rect avec sa position
    - sprite/image: pygame.Surface à dessiner
    - y_sort_offset: décalage optionnel pour ajuster le point de tri
    """
    
    def __init__(self, rect: pygame.Rect, sprite: pygame.Surface, y_sort_offset: int = 0):
        self.rect = rect
        self.sprite = sprite
        self.y_sort_offset = y_sort_offset
    
    @property
    def y_sort_value(self) -> int:
        """Valeur utilisée pour le tri (bas du sprite + offset)."""
        return self.rect.bottom + self.y_sort_offset


class Camera:
    """
    Caméra 2D avec scrolling, lerp et limites.
    
    Usage:
        camera = Camera(800, 600)
        camera.set_target(player)
        
        # Dans la boucle de jeu:
        camera.update(dt)
        
        # Pour dessiner un objet:
        screen_pos = camera.apply(world_pos)
        screen.blit(sprite, screen_pos)
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        
        # Position de la caméra dans le monde (coin haut-gauche)
        self.x = 0.0
        self.y = 0.0
        
        # Cible à suivre (généralement le joueur)
        self.target = None
        self.target_offset = (0, 0)  # Décalage par rapport au centre de la cible
        
        # Paramètres de suivi fluide
        self.lerp_speed = 5.0  # Plus haut = plus rapide
        self.use_lerp = True
        
        # Limites du monde
        self.bounds: Optional[CameraBounds] = None
        
        # Zone morte (la caméra ne bouge pas si le joueur est dans cette zone)
        self.deadzone_width = 100
        self.deadzone_height = 80
        self.use_deadzone = False
        
        # Effets de caméra
        self.shake_amount = 0.0
        self.shake_decay = 5.0
        self._shake_offset = (0, 0)
    
    def set_target(self, target, offset: Tuple[int, int] = (0, 0)):
        """
        Définit la cible à suivre.
        
        Args:
            target: Objet avec un attribut 'rect' (pygame.Rect)
            offset: Décalage par rapport au centre de la cible
        """
        self.target = target
        self.target_offset = offset
    
    def set_bounds(self, world_width: int, world_height: int):
        """
        Définit les limites du monde.
        La caméra ne pourra pas sortir de ces limites.
        
        Args:
            world_width: Largeur totale du monde en pixels
            world_height: Hauteur totale du monde en pixels
        """
        self.bounds = CameraBounds(
            left=0,
            top=0,
            right=max(0, world_width - self.width),
            bottom=max(0, world_height - self.height)
        )
    
    def center_on(self, x: float, y: float, instant: bool = True):
        """
        Centre la caméra sur une position donnée.
        
        Args:
            x, y: Position dans le monde
            instant: Si True, téléporte la caméra. Sinon, elle glisse.
        """
        target_x = x - self.width / 2
        target_y = y - self.height / 2
        
        if instant:
            self.x = target_x
            self.y = target_y
            self._apply_bounds()
        else:
            # Le lerp sera appliqué dans update()
            pass
    
    def _apply_bounds(self):
        """Applique les limites de la caméra."""
        if self.bounds:
            self.x = max(self.bounds.left, min(self.x, self.bounds.right))
            self.y = max(self.bounds.top, min(self.y, self.bounds.bottom))
    
    def update(self, dt: float):
        """
        Met à jour la position de la caméra.
        
        Args:
            dt: Delta time en secondes
        """
        if self.target is None:
            return
        
        # Position cible (centre de l'écran sur la cible)
        target_x = self.target.rect.centerx + self.target_offset[0] - self.width / 2
        target_y = self.target.rect.centery + self.target_offset[1] - self.height / 2
        
        # Appliquer la deadzone si activée
        if self.use_deadzone:
            dx = target_x - self.x
            dy = target_y - self.y
            
            # Ne bouger que si on sort de la deadzone
            if abs(dx) < self.deadzone_width / 2:
                target_x = self.x
            if abs(dy) < self.deadzone_height / 2:
                target_y = self.y
        
        # Déplacement
        if self.use_lerp:
            # Interpolation linéaire pour mouvement fluide
            lerp_factor = 1.0 - pow(0.5, dt * self.lerp_speed)
            self.x += (target_x - self.x) * lerp_factor
            self.y += (target_y - self.y) * lerp_factor
        else:
            # Suivi instantané
            self.x = target_x
            self.y = target_y
        
        # Appliquer les limites
        self._apply_bounds()
        
        # Appliquer le shake
        if self.shake_amount > 0:
            import random
            self._shake_offset = (
                random.uniform(-self.shake_amount, self.shake_amount),
                random.uniform(-self.shake_amount, self.shake_amount)
            )
            self.shake_amount -= self.shake_decay * dt
            if self.shake_amount < 0:
                self.shake_amount = 0
                self._shake_offset = (0, 0)
    
    def shake(self, amount: float, decay: float = 5.0):
        """
        Déclenche un effet de tremblement.
        
        Args:
            amount: Intensité du tremblement (pixels)
            decay: Vitesse de diminution
        """
        self.shake_amount = amount
        self.shake_decay = decay
    
    def apply(self, pos: Union[Tuple[int, int], pygame.Rect]) -> Tuple[int, int]:
        """
        Convertit une position du monde en position écran.
        
        Args:
            pos: Position ou Rect dans l'espace monde
        
        Returns:
            Position dans l'espace écran
        """
        if isinstance(pos, pygame.Rect):
            return (
                int(pos.x - self.x + self._shake_offset[0]),
                int(pos.y - self.y + self._shake_offset[1])
            )
        else:
            return (
                int(pos[0] - self.x + self._shake_offset[0]),
                int(pos[1] - self.y + self._shake_offset[1])
            )
    
    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """
        Convertit un Rect du monde en Rect écran.
        
        Args:
            rect: Rectangle dans l'espace monde
        
        Returns:
            Rectangle dans l'espace écran
        """
        return pygame.Rect(
            rect.x - int(self.x) + int(self._shake_offset[0]),
            rect.y - int(self.y) + int(self._shake_offset[1]),
            rect.width,
            rect.height
        )
    
    def inverse_apply(self, screen_pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Convertit une position écran en position monde.
        Utile pour les clics de souris.
        
        Args:
            screen_pos: Position sur l'écran
        
        Returns:
            Position dans le monde
        """
        return (
            int(screen_pos[0] + self.x - self._shake_offset[0]),
            int(screen_pos[1] + self.y - self._shake_offset[1])
        )
    
    @property
    def offset(self) -> Tuple[int, int]:
        """Retourne l'offset de la caméra (pour le LightingSystem)."""
        return (int(self.x), int(self.y))
    
    def is_visible(self, rect: pygame.Rect, margin: int = 50) -> bool:
        """
        Vérifie si un rectangle est visible à l'écran.
        
        Args:
            rect: Rectangle dans l'espace monde
            margin: Marge supplémentaire autour de l'écran
        
        Returns:
            True si le rectangle est (partiellement) visible
        """
        screen_rect = pygame.Rect(
            self.x - margin,
            self.y - margin,
            self.width + margin * 2,
            self.height + margin * 2
        )
        return screen_rect.colliderect(rect)


class YSortCameraGroup:
    """
    Groupe de sprites avec tri Y-Sort et support caméra.
    
    Cette classe gère :
    - Le tri automatique des sprites par leur position Y
    - L'application de l'offset caméra lors du dessin
    - Le culling (ne pas dessiner les sprites hors écran)
    
    Usage:
        sprites = YSortCameraGroup(camera)
        sprites.add(player)
        sprites.add(npc1)
        sprites.add(tree)
        
        # Dans la boucle de rendu:
        sprites.draw(screen)
    """
    
    def __init__(self, camera: Camera):
        self.camera = camera
        self.sprites: List = []
    
    def add(self, *sprites):
        """Ajoute un ou plusieurs sprites au groupe."""
        for sprite in sprites:
            if sprite not in self.sprites:
                self.sprites.append(sprite)
    
    def remove(self, *sprites):
        """Retire un ou plusieurs sprites du groupe."""
        for sprite in sprites:
            if sprite in self.sprites:
                self.sprites.remove(sprite)
    
    def clear(self):
        """Vide le groupe."""
        self.sprites.clear()
    
    def _get_y_sort_value(self, sprite) -> int:
        """
        Récupère la valeur de tri Y pour un sprite.
        
        Le sprite peut avoir :
        - y_sort_offset: décalage personnalisé
        - Sinon on utilise rect.bottom
        """
        if hasattr(sprite, 'y_sort_offset'):
            return sprite.rect.bottom + sprite.y_sort_offset
        return sprite.rect.bottom
    
    def draw(self, screen: pygame.Surface, draw_shadows: bool = True):
        """
        Dessine tous les sprites triés par Y avec l'offset caméra.
        
        Args:
            screen: Surface de destination
            draw_shadows: Si True, dessine les ombres sous les sprites
        """
        # Filtrer les sprites visibles
        visible_sprites = [
            s for s in self.sprites 
            if hasattr(s, 'rect') and hasattr(s, 'sprite') and s.sprite is not None
            and self.camera.is_visible(s.rect)
        ]
        
        # Trier par Y (bas du sprite)
        sorted_sprites = sorted(visible_sprites, key=self._get_y_sort_value)
        
        # Dessiner dans l'ordre
        for sprite in sorted_sprites:
            # Position écran
            screen_pos = self.camera.apply(sprite.rect)
            
            # Ombre (optionnel)
            if draw_shadows:
                shadow_x = screen_pos[0] + sprite.rect.width // 2 - 10
                shadow_y = screen_pos[1] + sprite.rect.height - 5
                pygame.draw.ellipse(
                    screen, 
                    (30, 30, 30, 100),  # Ombre semi-transparente
                    (shadow_x, shadow_y, 20, 8)
                )
            
            # Sprite
            screen.blit(sprite.sprite, screen_pos)
    
    def draw_custom(self, screen: pygame.Surface, draw_func):
        """
        Dessine les sprites avec une fonction personnalisée.
        
        Args:
            screen: Surface de destination
            draw_func: Fonction(screen, sprite, screen_pos) appelée pour chaque sprite
        """
        visible_sprites = [
            s for s in self.sprites 
            if hasattr(s, 'rect') and self.camera.is_visible(s.rect)
        ]
        
        sorted_sprites = sorted(visible_sprites, key=self._get_y_sort_value)
        
        for sprite in sorted_sprites:
            screen_pos = self.camera.apply(sprite.rect)
            draw_func(screen, sprite, screen_pos)


class TileMap:
    """
    Utilitaire pour dessiner une tilemap avec offset caméra.
    
    Optimisé pour ne dessiner que les tuiles visibles.
    """
    
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
    
    def get_visible_range(self, camera: Camera) -> Tuple[int, int, int, int]:
        """
        Calcule les indices des tuiles visibles.
        
        Returns:
            (start_col, start_row, end_col, end_row)
        """
        start_col = max(0, int(camera.x // self.tile_size))
        start_row = max(0, int(camera.y // self.tile_size))
        end_col = int((camera.x + camera.width) // self.tile_size) + 1
        end_row = int((camera.y + camera.height) // self.tile_size) + 1
        
        return start_col, start_row, end_col, end_row


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def lerp(a: float, b: float, t: float) -> float:
    """
    Interpolation linéaire entre a et b.
    
    Args:
        a: Valeur de départ
        b: Valeur d'arrivée
        t: Facteur d'interpolation (0 = a, 1 = b)
    
    Returns:
        Valeur interpolée
    """
    return a + (b - a) * t


def smooth_damp(current: float, target: float, velocity: float, 
                smooth_time: float, dt: float, max_speed: float = float('inf')) -> Tuple[float, float]:
    """
    Mouvement fluide avec amortissement (comme Unity's SmoothDamp).
    
    Args:
        current: Position actuelle
        target: Position cible
        velocity: Vélocité actuelle (sera modifiée)
        smooth_time: Temps approximatif pour atteindre la cible
        dt: Delta time
        max_speed: Vitesse maximale
    
    Returns:
        (nouvelle_position, nouvelle_vélocité)
    """
    smooth_time = max(0.0001, smooth_time)
    omega = 2.0 / smooth_time
    
    x = omega * dt
    exp = 1.0 / (1.0 + x + 0.48 * x * x + 0.235 * x * x * x)
    
    change = current - target
    original_to = target
    
    max_change = max_speed * smooth_time
    change = max(-max_change, min(max_change, change))
    target = current - change
    
    temp = (velocity + omega * change) * dt
    velocity = (velocity - omega * temp) * exp
    output = target + (change + temp) * exp
    
    if (original_to - current > 0) == (output > original_to):
        output = original_to
        velocity = (output - original_to) / dt
    
    return output, velocity
