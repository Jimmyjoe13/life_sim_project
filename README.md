## 🏡 LifeSim Project (Python MVP)

LifeSim est un moteur de simulation de vie en 2D (Top-Down) développé en Python. Ce projet démontre une architecture logicielle robuste (MVC, OOP) capable de gérer des systèmes complexes comme l'économie, la gestion des besoins, les interactions PNJ et la transition entre différents environnements (Intérieur/Extérieur).

## ✨ Fonctionnalités Actuelles

### 🧠 Système de Simulation

Cycle de Vie : Gestion en temps réel de la Faim et de l'Énergie.

Économie : Gagner de l'argent en travaillant (échange Énergie -> Argent) et le dépenser au magasin.

Inventaire : Système de stockage d'objets consommables (Pommes, Café).

Persistance : Sauvegarde et Chargement complet de l'état du joueur via JSON (F5/F9).

### 🌍 Monde & Environnement

Système Multi-Map : Transition fluide entre le Monde Extérieur et l'Intérieur de la maison.

Interactions Contextuelles : Menus dynamiques selon l'objet touché (Lit, Frigo, PNJ, Bureau).

Maison Meublée : Intérieur détaillé avec zones distinctes (Cuisine, Salon, Chambre, SDB) et meubles interactifs.

### 🤖 Entités Intelligentes

PNJs Vivants : Personnages non-joueurs (Bob, Alice) avec système de dialogue style RPG.

Feedback Visuel : Bulles de dialogue, Menus contextuels, Jauges de statut.

## 🛠️ Installation & Démarrage

Ce projet utilise un générateur d'assets procédural pour ne pas dépendre de fichiers externes lourds.

1. Pré-requis

Avoir Python 3.10 ou supérieur installé.

2. Installation des dépendances

pip install -r requirements.txt


(Le fichier requirements contient principalement pygame-ce et pandas)

3. Génération des Graphismes (Première fois uniquement)

Avant de lancer le jeu, il faut générer les sprites (Pixel Art) :

python LifeSim/tools/make_assets.py


Cela va créer le dossier assets/images avec tous les PNG nécessaires.

4. Lancer le Jeu

python LifeSim/src/main.py


## 🎮 Contrôles

Action

Touche(s)

Description

Mouvement

Flèches ou ZQSD

Déplacer le personnage

Interaction

ESPACE

Entrer, Dormir, Travailler, etc.

Manger

E

Consomme le 1er objet de l'inventaire

Parler

T

Discuter avec un PNJ proche

Acheter

1 / 2

Acheter des objets (dans la zone Shop)

Sauvegarder

F5

Sauvegarde rapide (JSON)

Charger

F9

Chargement rapide

Quitter

Echap / Fermer

Quitter le jeu

## 🏗️ Architecture du Projet

Le projet suit une architecture modulaire stricte pour faciliter l'évolution.
```
LifeSim/
├── assets/                 # Généré automatiquement (Images)
├── data/
│   └── saves/              # Fichiers de sauvegarde (.json)
├── tools/
│   └── make_assets.py      # Script de génération procédurale d'images
├── src/
│   ├── core/
│   │   ├── asset_manager.py # Singleton de gestion des sprites
│   │   ├── save_manager.py  # Gestion lecture/écriture JSON
│   │   └── settings.py      # Constantes globales (Écran, Couleurs)
│   ├── entities/
│   │   ├── player.py        # Logique joueur (Stats, Mouvement)
│   │   ├── house.py         # Gestion Intérieur/Extérieur & Meubles
│   │   ├── npc.py           # IA et Dialogues
│   │   ├── shop.py          # Logique d'achat
│   │   ├── workplace.py     # Logique de travail
│   │   └── item.py          # DataClass des objets
│   └── main.py              # Point d'entrée & Boucle de jeu (Game Loop)
└── requirements.txt
```

## 🚀 Roadmap (Prochaines Étapes)

[x] Déplacement & Collisions

[x] Système de Faim/Énergie

[x] Magasin & Travail

[x] Sauvegarde JSON

[x] Intérieur de Maison

[ ] Quêtes PNJ : Système de missions données par Bob ou Alice.

[ ] Cycle Jour/Nuit : Assombrissement progressif et fatigue accrue la nuit.

[ ] Système de Tuiles : Remplacer le fond vert par une vraie carte (Herbe, Chemins, Eau).

---

Développé avec ❤️ et Python.