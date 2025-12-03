# 🏡 LifeSim Project

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> Moteur de simulation de vie 2D top-down développé en Python avec Pygame, démontrant une architecture MVC robuste et des systèmes de jeu complexes.

## 📋 Table des matières

- [Aperçu](#-aperçu)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Démarrage rapide](#-démarrage-rapide)
- [Contrôles](#-contrôles)
- [Architecture](#-architecture)
- [Technologies](#-technologies)
- [Roadmap](#-roadmap)
- [Contribution](#-contribution)
- [License](#-license)

## 🎮 Aperçu

LifeSim est un moteur de simulation qui reproduit les mécaniques d'un jeu de vie quotidienne. Le joueur évolue dans un monde 2D où il doit gérer ses besoins vitaux (faim, énergie), gagner de l'argent en travaillant, effectuer des achats et interagir avec des PNJ dans différents environnements.

### Démo

![Gameplay Screenshot](docs/screenshot.png) *(À ajouter)*

## ✨ Fonctionnalités

### 🧠 Systèmes de simulation

- **Gestion des besoins** : Cycle de vie en temps réel avec faim et énergie.
- **Cycle Jour / Nuit** : Gestion du temps qui passe, horloge en temps réel et assombrissement nocturne dynamique.
- **Économie dynamique** : Système travail → argent → achats.
- **Inventaire** : Gestion d'objets consommables (pommes, café, etc.).
- **Persistance** : Sauvegarde/chargement complet en JSON (F5/F9).

### 🌍 Monde interactif

- **Monde en Tuiles (Tile System)** : Carte générée avec différents terrains (herbe, chemin, eau).
- **Multi-environnements** : Transition fluide entre extérieur et intérieur.
- **Maison détaillée** : Zones distinctes (cuisine, salon, chambre, salle de bain) avec meubles interactifs.
- **Interactions contextuelles** : Menus dynamiques selon l'objet (lit, frigo, bureau, PNJ).

### 🤖 Intelligence Artificielle & Quêtes

- **PNJ autonomes** : Personnages avec comportements et dialogues (Bob, Alice).
- **Système de Quêtes** : Les PNJ peuvent donner des missions, valider des objectifs (objets requis) et donner des récompenses.
- **Feedback visuel** : Bulles de dialogue, menus, jauges de statut.

### 🎨 Graphismes Procéduraux

- **Générateur d'Assets** : Un outil intégré (`make_assets.py`) génère tous les sprites du jeu (Pixel Art vectoriel) au démarrage, garantissant un style cohérent et des collisions parfaites.

## 🚀 Installation

### Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le dépôt**

```bash
git clone [https://github.com/Jimmyjoe13/life_sim_project.git](https://github.com/Jimmyjoe13/life_sim_project.git)
cd life_sim_project
````

2.  **Installer les dépendances**

<!-- end list -->

```bash
pip install -r LifeSim/requirements.txt
```

3.  **Générer les assets** (première fois uniquement)

<!-- end list -->

```bash
python LifeSim/tools/make_assets.py
```

Cette commande génère les sprites pixel art dans `assets/images/`.

## ⚡ Démarrage rapide

```bash
python LifeSim/src/main.py
```

Le jeu se lance en fenêtre plein écran. Utilisez `Échap` pour quitter.

## 🎮 Contrôles

| Action | Touche(s) | Description |
|--------|-----------|-------------|
| **Déplacement** | `↑ ↓ ← →` ou `ZQSD` | Déplacer le personnage |
| **Interaction** | `Espace` | Entrer, dormir, travailler, etc. |
| **Manger** | `E` | Consommer le premier objet de l'inventaire |
| **Parler / Quête** | `T` | Discuter avec un PNJ / Prendre ou valider une quête |
| **Acheter** | `1` / `2` | Acheter des objets (zone shop) |
| **Sauvegarder** | `F5` | Sauvegarde rapide |
| **Charger** | `F9` | Chargement rapide |
| **Quitter** | `Échap` | Quitter le jeu |

## 🏗️ Architecture

Le projet suit une architecture **MVC modulaire** pour faciliter l'évolutivité :

```
LifeSim/
├── assets/              # Assets générés (sprites PNG)
├── data/
│   └── saves/           # Fichiers de sauvegarde JSON
├── tools/
│   └── make_assets.py   # Générateur procédural d'images (Pixel Art)
├── src/
│   ├── core/            # Modules centraux
│   │   ├── asset_manager.py
│   │   ├── save_manager.py
│   │   ├── settings.py
│   │   ├── time_manager.py  # Gestion du cycle jour/nuit
│   │   └── world_map.py     # Gestion de la carte (Tuiles)
│   ├── entities/        # Entités du jeu
│   │   ├── player.py
│   │   ├── house.py
│   │   ├── npc.py
│   │   ├── quest.py         # Structure des quêtes
│   │   ├── shop.py
│   │   ├── workplace.py
│   │   └── item.py
│   ├── systems/         # Systèmes de jeu
│   ├── ui/              # Interface utilisateur
│   └── main.py          # Point d'entrée
├── tests/               # Tests unitaires
└── requirements.txt
```

### Principes architecturaux

  - **Séparation des préoccupations** : MVC strict
  - **Singleton Pattern** : Asset Manager pour optimiser la mémoire
  - **Data Classes** : Structures d'objets typées
  - **Event-driven** : Boucle de jeu réactive

## 🛠️ Technologies

  - **[Pygame CE](https://pyga.me/)** : Moteur de jeu 2D
  - **[Python 3.10+](https://www.python.org/)** : Langage de programmation
  - **[Pandas](https://pandas.pydata.org/)** : Gestion de données (optionnel)
  - **JSON** : Persistance des sauvegardes

## 🗺️ Roadmap

### ✅ Implémenté

  - [x] Système de déplacement et collisions
  - [x] Gestion faim/énergie
  - [x] Économie (magasin + travail)
  - [x] Sauvegarde/chargement JSON
  - [x] Multi-environnements (intérieur/extérieur)
  - [x] PNJ avec dialogues
  - [x] **Système de quêtes** : Missions données par les PNJ
  - [x] **Cycle jour/nuit** : Assombrissement progressif
  - [x] **Système de tuiles** : Carte avec herbe, chemins, eau

### 🔜 À venir

  - [ ] **Augmenter le nombre de PNJ**
  - [ ] **Relations sociales** : Jauge d'amitié avec les PNJ
  - [ ] **Compétences** : Arbre de progression du joueur (XP)
  - [ ] **Événements aléatoires** : Surprises et défis dynamiques (Pluie, visiteurs...)
  - [ ] **Menu Inventaire** : Interface graphique pour gérer les objets

## 🤝 Contribution

Les contributions sont les bienvenues \! Pour contribuer :

1.  Fork le projet
2.  Créez une branche (`git checkout -b feature/AmazingFeature`)
3.  Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4.  Pushez vers la branche (`git push origin feature/AmazingFeature`)
5.  Ouvrez une Pull Request

### Standards de code

  - Suivre [PEP 8](https://pep8.org/)
  - Documenter les fonctions avec docstrings
  - Ajouter des tests pour les nouvelles fonctionnalités

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👤 Auteur

**Jimmy** - [Jimmyjoe13](https://github.com/Jimmyjoe13)

## 🙏 Remerciements

  - Pygame Community pour la documentation
  - Inspiré par Stardew Valley et The Sims

-----

**Développé avec ❤️ et Python**