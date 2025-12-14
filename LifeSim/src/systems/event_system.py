# LifeSim/src/systems/event_system.py
"""
Système d'événements aléatoires pour ajouter de la variété au gameplay.
"""

import random
from dataclasses import dataclass
from typing import Callable, Optional, List
from enum import Enum


class EventType(Enum):
    WEATHER = "weather"
    VISITOR = "visitor"
    GIFT = "gift"
    MOOD = "mood"


@dataclass
class GameEvent:
    """Représente un événement aléatoire."""
    name: str
    event_type: EventType
    message: str
    probability: float  # Probabilité d'occurrence (0.0 à 1.0)
    effect_hunger: float = 0.0
    effect_energy: float = 0.0
    effect_money: int = 0
    effect_happiness: float = 0.0
    duration_minutes: int = 0  # Durée en minutes de jeu


class WeatherType(Enum):
    SUNNY = "Ensoleillé"
    CLOUDY = "Nuageux"
    RAINY = "Pluvieux"
    STORMY = "Orageux"


class EventSystem:
    """Gère les événements aléatoires du jeu."""
    
    def __init__(self):
        self.current_weather = WeatherType.SUNNY
        self.active_events: List[GameEvent] = []
        self.last_check_time = 0
        self.check_interval = 30  # Vérifie toutes les 30 minutes de jeu
        
        # Définition des événements possibles
        self.possible_events = self._create_event_pool()
    
    def _create_event_pool(self) -> List[GameEvent]:
        """Crée la liste des événements possibles."""
        return [
            # === ÉVÉNEMENTS MÉTÉO ===
            GameEvent(
                name="Pluie Soudaine",
                event_type=EventType.WEATHER,
                message="☔ Il commence à pleuvoir ! Vous devriez rentrer à l'abri.",
                probability=0.15,
                effect_happiness=-5.0,
                duration_minutes=60
            ),
            GameEvent(
                name="Belle Journée",
                event_type=EventType.WEATHER,
                message="☀️ Quelle belle journée ! Vous vous sentez revigoré.",
                probability=0.20,
                effect_happiness=10.0,
                effect_energy=5.0,
                duration_minutes=120
            ),
            
            # === ÉVÉNEMENTS VISITEURS ===
            GameEvent(
                name="Visiteur Surprise",
                event_type=EventType.VISITOR,
                message="🚪 Quelqu'un frappe à la porte ! Un voisin vous apporte un cadeau.",
                probability=0.08,
                effect_happiness=15.0
            ),
            GameEvent(
                name="Facteur Généreux",
                event_type=EventType.VISITOR,
                message="📦 Le facteur vous apporte un colis mystérieux avec de l'argent !",
                probability=0.05,
                effect_money=50
            ),
            
            # === ÉVÉNEMENTS CADEAUX/TROUVAILLES ===
            GameEvent(
                name="Trouvaille Chanceuse",
                event_type=EventType.GIFT,
                message="🍀 Vous trouvez un billet par terre ! La chance vous sourit.",
                probability=0.10,
                effect_money=25
            ),
            GameEvent(
                name="Vent de Fatigue",
                event_type=EventType.MOOD,
                message="😴 Un coup de fatigue vous envahit soudainement...",
                probability=0.12,
                effect_energy=-15.0
            ),
            
            # === ÉVÉNEMENTS D'HUMEUR ===
            GameEvent(
                name="Élan de Motivation",
                event_type=EventType.MOOD,
                message="💪 Vous vous sentez particulièrement motivé aujourd'hui !",
                probability=0.15,
                effect_energy=20.0,
                effect_happiness=10.0
            ),
            GameEvent(
                name="Petit Creux",
                event_type=EventType.MOOD,
                message="🍽️ Votre estomac gargouille... Vous avez un peu faim.",
                probability=0.10,
                effect_hunger=-10.0
            ),
        ]
    
    def update(self, game_minutes: int) -> Optional[GameEvent]:
        """
        Vérifie si un événement doit se déclencher.
        Appelé à chaque update du jeu.
        Retourne l'événement déclenché, ou None.
        """
        # On ne check que toutes les X minutes de jeu
        if game_minutes - self.last_check_time < self.check_interval:
            return None
        
        self.last_check_time = game_minutes
        
        # Parcourir les événements et lancer les dés
        for event in self.possible_events:
            if random.random() < event.probability:
                self.active_events.append(event)
                return event
        
        return None
    
    def apply_event_effects(self, player, event: GameEvent):
        """Applique les effets d'un événement au joueur."""
        if event.effect_hunger != 0:
            player.stats.hunger = max(0, min(100, player.stats.hunger + event.effect_hunger))
        if event.effect_energy != 0:
            player.stats.energy = max(0, min(100, player.stats.energy + event.effect_energy))
        if event.effect_money != 0:
            player.stats.money += event.effect_money
        if event.effect_happiness != 0:
            player.stats.happiness = max(0, min(100, player.stats.happiness + event.effect_happiness))
    
    def update_weather(self):
        """Change aléatoirement la météo."""
        weather_chances = [
            (WeatherType.SUNNY, 0.50),
            (WeatherType.CLOUDY, 0.30),
            (WeatherType.RAINY, 0.15),
            (WeatherType.STORMY, 0.05),
        ]
        
        roll = random.random()
        cumulative = 0.0
        
        for weather, chance in weather_chances:
            cumulative += chance
            if roll < cumulative:
                if weather != self.current_weather:
                    self.current_weather = weather
                    print(f"🌤️ La météo change : {weather.value}")
                break
    
    def get_weather_string(self) -> str:
        """Retourne la météo actuelle en texte."""
        return self.current_weather.value
    
    def get_weather_effect_on_energy(self) -> float:
        """Retourne un modificateur d'énergie selon la météo."""
        effects = {
            WeatherType.SUNNY: 0.0,      # Normal
            WeatherType.CLOUDY: -0.5,    # Légèrement fatigant
            WeatherType.RAINY: -1.0,     # Plus fatigant
            WeatherType.STORMY: -2.0,    # Très fatigant
        }
        return effects.get(self.current_weather, 0.0)
    
    # --- Sauvegarde ---
    
    def to_dict(self) -> dict:
        """Exporte pour la sauvegarde."""
        return {
            "current_weather": self.current_weather.value,
            "last_check_time": self.last_check_time
        }
    
    def from_dict(self, data: dict):
        """Charge depuis une sauvegarde."""
        if not data:
            return
        
        weather_value = data.get("current_weather", "Ensoleillé")
        for w in WeatherType:
            if w.value == weather_value:
                self.current_weather = w
                break
        
        self.last_check_time = data.get("last_check_time", 0)
        print(f"🌤️ Météo chargée : {self.current_weather.value}")
