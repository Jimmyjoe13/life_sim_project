# LifeSim/src/systems/skill_system.py
"""
Système de compétences (Skills) pour le joueur.
Chaque action dans le jeu peut faire progresser une compétence.
"""

from dataclasses import dataclass, asdict
from typing import Dict
from enum import Enum


class SkillType(Enum):
    COOKING = "Cuisine"
    SOCIAL = "Social"
    WORK = "Travail"
    FITNESS = "Forme"


@dataclass
class Skill:
    """Représente une compétence individuelle."""
    name: str
    level: int = 1
    xp: int = 0
    xp_to_next_level: int = 100  # XP requis pour le niveau suivant
    
    def add_xp(self, amount: int) -> bool:
        """
        Ajoute de l'XP. Retourne True si le joueur a levelé up.
        """
        self.xp += amount
        leveled_up = False
        
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            # L'XP requis augmente de 50% à chaque niveau
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
            leveled_up = True
            print(f"🌟 LEVEL UP ! {self.name} est maintenant niveau {self.level} !")
        
        return leveled_up
    
    def get_bonus_multiplier(self) -> float:
        """Retourne un bonus basé sur le niveau (ex: +10% par niveau)."""
        return 1.0 + (self.level - 1) * 0.1


class SkillSystem:
    """Gère toutes les compétences du joueur."""
    
    def __init__(self):
        self.skills: Dict[SkillType, Skill] = {
            SkillType.COOKING: Skill(name="Cuisine"),
            SkillType.SOCIAL: Skill(name="Social"),
            SkillType.WORK: Skill(name="Travail"),
            SkillType.FITNESS: Skill(name="Forme"),
        }
    
    def gain_xp(self, skill_type: SkillType, amount: int) -> bool:
        """
        Ajoute de l'XP à une compétence spécifique.
        Retourne True si le joueur a gagné un niveau.
        """
        if skill_type not in self.skills:
            return False
        
        skill = self.skills[skill_type]
        leveled_up = skill.add_xp(amount)
        print(f"✨ +{amount} XP en {skill.name} (Total: {skill.xp}/{skill.xp_to_next_level})")
        return leveled_up
    
    def get_skill(self, skill_type: SkillType) -> Skill:
        """Retourne la compétence demandée."""
        return self.skills.get(skill_type)
    
    def get_level(self, skill_type: SkillType) -> int:
        """Retourne le niveau d'une compétence."""
        skill = self.skills.get(skill_type)
        return skill.level if skill else 1
    
    def get_bonus(self, skill_type: SkillType) -> float:
        """Retourne le multiplicateur de bonus d'une compétence."""
        skill = self.skills.get(skill_type)
        return skill.get_bonus_multiplier() if skill else 1.0
    
    def get_all_skills_info(self) -> Dict[str, dict]:
        """Retourne un résumé de toutes les compétences."""
        return {
            skill.name: {
                "level": skill.level,
                "xp": skill.xp,
                "xp_needed": skill.xp_to_next_level,
                "bonus": f"+{int((skill.get_bonus_multiplier() - 1) * 100)}%"
            }
            for skill in self.skills.values()
        }
    
    # --- Sauvegarde / Chargement ---
    
    def to_dict(self) -> dict:
        """Exporte pour la sauvegarde JSON."""
        return {
            skill_type.value: {
                "name": skill.name,
                "level": skill.level,
                "xp": skill.xp,
                "xp_to_next_level": skill.xp_to_next_level
            }
            for skill_type, skill in self.skills.items()
        }
    
    def from_dict(self, data: dict):
        """Charge depuis une sauvegarde."""
        if not data:
            return
        
        for skill_type in self.skills:
            skill_data = data.get(skill_type.value)
            if skill_data:
                self.skills[skill_type].level = skill_data.get("level", 1)
                self.skills[skill_type].xp = skill_data.get("xp", 0)
                self.skills[skill_type].xp_to_next_level = skill_data.get("xp_to_next_level", 100)
        
        print("📊 Compétences chargées !")
