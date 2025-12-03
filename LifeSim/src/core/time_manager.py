# src/core/time_manager.py
from src.core.settings import DAY_START_HOUR

class TimeManager:
    def __init__(self):
        # On commence au Jour 1, à l'heure définie dans les settings
        self.day = 1
        self.minutes = DAY_START_HOUR * 60  # On convertit tout en minutes
        self.total_minutes_in_day = 24 * 60

    def update(self, dt, time_speed):
        """Fait avancer le temps."""
        # On ajoute des minutes en fonction du temps écoulé (dt) et de la vitesse
        self.minutes += dt * time_speed

        # Si on dépasse 24h (1440 minutes), on passe au jour suivant
        if self.minutes >= self.total_minutes_in_day:
            self.minutes = 0
            self.day += 1
            print(f"🌅 Nouveau jour : Jour {self.day}")

    def get_time_string(self):
        """Retourne l'heure formatée (ex: '08:30') pour l'affichage."""
        current_hour = int(self.minutes // 60)
        current_minute = int(self.minutes % 60)
        return f"{current_hour:02d}:{current_minute:02d}"

    def get_day_phase(self):
        """Retourne la phase de la journée pour savoir s'il fait nuit."""
        # Exemple simple : Nuit entre 20h et 6h du matin
        current_hour = self.minutes // 60
        if 6 <= current_hour < 20:
            return "day"
        else:
            return "night"
            
    def get_night_intensity(self):
        """(Bonus) Calcule à quel point il fait sombre (0 à 255)."""
        phase = self.get_day_phase()
        if phase == "day":
            return 0 # Pas sombre du tout
        else:
            return 150 # Semi-transparent sombre (ajuste selon tes goûts)