# 🎮 LifeSim - Simulateur de Vie Moderne

Un jeu de simulation de vie en pixel art développé avec Python et Pygame.
Gérez votre personnage, interagissez avec les PNJ, achetez des objets et explorez le monde !

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Pygame](https://img.shields.io/badge/Pygame-CE-green)

---

## 📸 Caractéristiques

### 🎨 Graphismes Modernes

- **Sprites 64x64** haute définition avec contours et ombrages
- **Animations de marche** (4 frames par personnage)
- **Tuiles avec variations** (3 types d'herbe, textures naturelles)
- **Variations saisonnières** (été/hiver)
- **Bâtiments détaillés** (maison avec tuiles, magasin avec enseigne)

### 🖥️ Interface Utilisateur Moderne

- **HUD animé** avec barres de progression à gradient
- **Mini-carte** interactive en haut à droite
- **Messages stylisés** avec animations fade in/out
- **Menus contextuels** avec flèches et style moderne
- **Interface de magasin** affichant tous les articles

### 🏠 Intérieur de Maison Amélioré

- **4 pièces distinctes** : Chambre, Salle de bain, Cuisine, Salon
- **Sols texturés** : Parquet et carrelage réalistes
- **Murs avec profondeur** et plinthes
- **Décorations** : Fenêtres, tapis, zone de sortie stylisée

### 👥 Système de PNJ

- **5 PNJ uniques** avec personnalités et tenues distinctes
- **Système de relations** (Inconnu → Ami → Meilleur Ami)
- **Système de cadeaux** avec réactions personnalisées
- **Quêtes** (ex: livrer une pomme à Bob)

### ⚡ Systèmes de Jeu

- **Compétences** : Cuisine, Social, Travail, Forme (avec XP)
- **Événements aléatoires** : Pluie d'argent, fatigue soudaine, etc.
- **Météo dynamique** : Ensoleillé, Nuageux, Pluvieux, Orageux
- **Cycle jour/nuit** avec filtre visuel

---

## 🎮 Contrôles

| Touche           | Action                                 |
| ---------------- | -------------------------------------- |
| `↑↓←→` ou `ZQSD` | Se déplacer                            |
| `ESPACE`         | Interagir (entrer, dormir, travailler) |
| `I`              | Ouvrir/Fermer l'inventaire             |
| `K`              | Ouvrir/Fermer les compétences          |
| `M`              | Afficher/Masquer la mini-carte         |
| `T`              | Parler à un PNJ                        |
| `G`              | Offrir un cadeau                       |
| `E`              | Manger un objet                        |
| `1-9`            | Acheter au magasin                     |
| `F5`             | Sauvegarder                            |
| `F9`             | Charger                                |

---

## 🏪 Magasin

9 articles disponibles à l'achat :

| #   | Article      | Catégorie  | Effets         |
| --- | ------------ | ---------- | -------------- |
| 1   | Pomme Rouge  | Nourriture | +Faim          |
| 2   | Croissant    | Nourriture | +Faim          |
| 3   | Café         | Boisson    | +Énergie       |
| 4   | Sandwich     | Nourriture | +Faim +Énergie |
| 5   | Energy Drink | Boisson    | ++Énergie      |
| 6   | Pizza        | Nourriture | ++Faim         |
| 7   | Fleurs       | Cadeau     | +Amitié        |
| 8   | Chocolats    | Cadeau     | ++Amitié       |
| 9   | Livre        | Cadeau     | +Amitié        |

---

## 🏠 Lieux

### Maison

- **Lit** : Restaure l'énergie et la santé
- **Canapé** : Petite pause (+5 énergie)
- **Cuisine/Frigo** : Accès futur à la préparation de repas

### Magasin

- Achetez nourriture, boissons et cadeaux

### Bureau

- Travaillez pour gagner de l'argent (+XP Travail)

---

## 📁 Structure du Projet

```
LifeSim/
├── assets/
│   └── images/          # Sprites et graphismes
├── data/
│   └── npcs.json        # Données des PNJ
├── src/
│   ├── core/            # Systèmes de base
│   │   ├── asset_manager.py
│   │   ├── save_manager.py
│   │   ├── settings.py
│   │   ├── time_manager.py
│   │   └── world_map.py
│   ├── entities/        # Entités du jeu
│   │   ├── house.py
│   │   ├── item.py
│   │   ├── npc.py
│   │   ├── npc_manager.py
│   │   ├── player.py
│   │   ├── quest.py
│   │   ├── shop.py
│   │   └── workplace.py
│   ├── systems/         # Systèmes avancés
│   │   ├── event_system.py
│   │   ├── relationship_system.py
│   │   └── skill_system.py
│   ├── ui/              # Interfaces utilisateur
│   │   ├── colors.py
│   │   ├── components.py
│   │   ├── dialogue_ui.py
│   │   ├── house_interior.py
│   │   ├── hud.py
│   │   ├── inventory_ui.py
│   │   ├── minimap.py
│   │   └── shop_ui.py
│   └── main.py          # Point d'entrée
└── tools/
    └── make_assets_modern.py  # Générateur de sprites
```

---

## 🚀 Installation

```bash
# Cloner le projet
git clone <repo-url>
cd LifeSim

# Installer les dépendances
pip install pygame-ce

# Générer les assets (optionnel, déjà inclus)
python tools/make_assets_modern.py

# Lancer le jeu
python src/main.py
```

---

## 🛠️ Technologies

- **Python 3.10+**
- **Pygame-CE** (Community Edition)
- **JSON** pour les données

---

## 📋 Roadmap

### ✅ Complété

- [x] Interface moderne (HUD, menus, mini-carte)
- [x] Sprites 64x64 avec animations
- [x] Variations saisonnières (été/hiver)
- [x] Système de compétences avec XP
- [x] Événements aléatoires et météo
- [x] 5 PNJ uniques avec relations
- [x] Magasin avec 9 articles
- [x] Intérieur de maison moderne

### 🔜 À venir

- [ ] Système de saisons automatique
- [ ] Plus de quêtes
- [ ] Animations de marche intégrées
- [ ] Effets de particules (pluie, feuilles)
- [ ] Sons et musique

---

## 🎨 Crédits

Développé avec ❤️ en Python/Pygame
