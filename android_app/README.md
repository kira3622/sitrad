# Application Android de Gestion de Béton

Cette application Android moderne utilise l'architecture MVVM avec Jetpack Compose et les vues traditionnelles pour gérer les commandes, la production et l'inventaire de béton.

## 🏗️ Architecture

- **MVVM** avec Repository Pattern
- **Hilt** pour l'injection de dépendances
- **Navigation Component** avec Safe Args
- **Retrofit** pour les appels API
- **Room** pour le stockage local
- **Material Design 3**

## 📱 Fonctionnalités

### Fragments Principaux
- **Dashboard** : Vue d'ensemble avec statistiques et graphiques
- **Commandes** : Gestion des commandes avec recherche et filtres
- **Production** : Suivi de la production avec statuts
- **Inventaire** : Gestion du stock des matières premières

### Fragments de Détail
- **Détail Commande** : Informations complètes d'une commande
- **Détail Production** : Détails d'une production

## 🛠️ Configuration Requise

- **Android Studio** Arctic Fox ou plus récent
- **JDK 8** ou plus récent
- **Android SDK** niveau 24 (Android 7.0) minimum
- **Gradle 8.4**

## 🚀 Installation et Build

### Méthode 1 : Android Studio (Recommandée)
1. Ouvrir Android Studio
2. Sélectionner "Open an existing project"
3. Naviguer vers le dossier `android_app`
4. Laisser Android Studio synchroniser les dépendances
5. Cliquer sur "Build" → "Make Project" (Ctrl+F9)
6. Exécuter l'application (Shift+F10)

### Méthode 2 : Ligne de commande
```bash
# Assurez-vous que JAVA_HOME est configuré
# Windows
set JAVA_HOME=C:\Program Files\Java\jdk-11.0.x

# Puis exécuter
gradlew.bat build
```

## 🔧 Configuration

### API Backend
L'application est configurée pour se connecter à :
- **Production** : `https://beton-project.onrender.com/api/v1/`
- **Debug** : `http://10.0.2.2:8000/api/v1/` (émulateur Android)

### Modification de l'URL API
Pour changer l'URL de l'API, modifiez les valeurs dans `app/build.gradle.kts` :
```kotlin
buildConfigField("String", "BASE_URL", "\"VOTRE_URL_PRODUCTION\"")
buildConfigField("String", "BASE_URL_DEBUG", "\"VOTRE_URL_DEBUG\"")
```

## 📂 Structure du Projet

```
app/src/main/
├── java/com/betonapp/
│   ├── data/
│   │   ├── api/          # Services API
│   │   ├── model/        # Modèles de données
│   │   └── repository/   # Repositories
│   ├── di/               # Injection de dépendances
│   ├── ui/
│   │   ├── dashboard/    # Fragment Dashboard
│   │   ├── orders/       # Fragment Commandes
│   │   ├── production/   # Fragment Production
│   │   ├── inventory/    # Fragment Inventaire
│   │   └── adapters/     # Adapters RecyclerView
│   └── MainActivity.kt
└── res/
    ├── layout/           # Layouts XML
    ├── navigation/       # Graphe de navigation
    ├── values/           # Ressources (strings, colors)
    └── drawable/         # Icônes et images
```

## 🎨 Thème et Design

L'application utilise Material Design 3 avec :
- **Couleurs** : Palette moderne avec support du mode sombre
- **Typography** : Roboto avec hiérarchie claire
- **Components** : Material Components (Cards, Buttons, FAB, etc.)

## 🔄 Navigation

Navigation fluide entre les écrans :
- **Bottom Navigation** : 4 onglets principaux
- **Safe Args** : Passage sécurisé de paramètres
- **Deep Links** : Support des liens profonds

## 🧪 Tests

Pour exécuter les tests :
```bash
# Tests unitaires
gradlew.bat test

# Tests d'instrumentation
gradlew.bat connectedAndroidTest
```

## 📝 Notes de Développement

### Problèmes Résolus
- ✅ Configuration AndroidX
- ✅ Safe Args avec androidx
- ✅ Injection de dépendances Hilt
- ✅ Navigation Component
- ✅ Gestion des états UI

### Prochaines Étapes
- [ ] Tests d'intégration avec l'API
- [ ] Optimisation des performances
- [ ] Mode hors ligne complet
- [ ] Notifications push

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.