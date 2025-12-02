import os
from pathlib import Path

def create_structure():
    """Génère l'arborescence du projet LifeSim."""
    root = Path("LifeSim")
    
    dirs = [
        root / "assets" / "images",
        root / "assets" / "sounds",
        root / "assets" / "fonts",
        root / "data" / "saves",     # Pour la sauvegarde locale
        root / "src" / "core",       # Configuration, Gestion du temps
        root / "src" / "entities",   # Le Joueur, PNJ
        root / "src" / "ui",         # Affichage Pygame
        root / "src" / "systems",    # Logique métier (Économie, Job)
        root / "tests"
    ]

    files = [
        root / "src" / "__init__.py",
        root / "src" / "main.py",
        root / "src" / "core" / "settings.py",
        root / "src" / "entities" / "player.py",
        root / "requirements.txt",
        root / "README.md"
    ]

    print(f"🚀 Création de la structure dans {root.absolute()}...")

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        # Création d'un .gitkeep pour que git suive les dossiers vides
        (d / ".gitkeep").touch()

    for f in files:
        if not f.exists():
            f.touch()
            print(f"  - Fichier créé : {f.name}")

    # Remplissage du requirements.txt
    with open(root / "requirements.txt", "w") as req:
        req.write("pygame-ce>=2.3.0\npandas>=2.0.0\n")

    print("\n✅ Structure terminée. Lance 'pip install -r LifeSim/requirements.txt'")

if __name__ == "__main__":
    create_structure()