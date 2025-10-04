# Guide de Dépannage des Dépendances Android

## Problème Résolu : Configuration des Dépôts

### ❌ Erreur Originale
```
Build was configured to prefer settings repositories over project repositories but repository 'Google' was added by build file 'build.gradle.kts'
```

### ✅ Solution Appliquée
1. **Suppression de la section `allprojects`** dans `build.gradle.kts` (niveau projet) :
   - Lorsque `repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)` est défini dans `settings.gradle.kts`, les dépôts doivent être déclarés uniquement dans ce fichier.
   - Supprimer toute déclaration de dépôts dans les fichiers build.gradle.kts

2. **Vérifier que tous les dépôts nécessaires** sont correctement déclarés dans `settings.gradle.kts` :
```kotlin
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") }
    }
}
```

## Problème Résolu : MPAndroidChart

### ❌ Erreur Originale
```
Could not find com.github.PhilJay:MPAndroidChart:v3.1.0.
```

### ✅ Solution Appliquée

1. **Ajout du repository JitPack** dans `build.gradle.kts` (niveau projet) :
```kotlin
allprojects {
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") }
    }
}
```

2. **Correction de `settings.gradle.kts`** :
```kotlin
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") }
    }
}
```

3. **Mise à jour de la version** dans `app/build.gradle.kts` :
```kotlin
implementation("com.github.PhilJay:MPAndroidChart:v3.1.4")
```

## Vérification de la Solution

### Méthode 1 : Android Studio
1. Ouvrir le projet dans Android Studio
2. Cliquer sur "Sync Project with Gradle Files"
3. Vérifier qu'il n'y a pas d'erreurs de synchronisation

### Méthode 2 : Ligne de commande
```bash
# Tester la résolution des dépendances
gradlew.bat app:dependencies --configuration debugCompileClasspath

# Ou utiliser le script de test
test_dependencies.bat
```

## Autres Problèmes Potentiels

### Corruption du Cache de Dépendances
Si vous rencontrez cette erreur :
```
Unable to find method 'org.gradle.api.file.FileCollection org.gradle.api.artifacts.Configuration.fileCollection(org.gradle.api.specs.Spec)'
Gradle's dependency cache may be corrupt (this sometimes occurs after a network connection timeout.)
```

**Solution** :
1. Arrêtez le daemon Gradle :
```bash
gradlew.bat --stop
```

2. Supprimez le cache de dépendances :
```bash
# Windows
rmdir /s /q %USERPROFILE%\.gradle\caches

# Linux/Mac
rm -rf ~/.gradle/caches
```

3. Relancez la compilation :
```bash
gradlew.bat clean build
```

### Configuration Cache
Si vous voyez des erreurs de cache de configuration :
```bash
gradlew.bat --stop
gradlew.bat clean
gradlew.bat build
```

### Problèmes de Proxy/Réseau
Si vous êtes derrière un proxy d'entreprise, ajoutez dans `gradle.properties` :
```properties
systemProp.http.proxyHost=your.proxy.host
systemProp.http.proxyPort=8080
systemProp.https.proxyHost=your.proxy.host
systemProp.https.proxyPort=8080
```

### Versions Incompatibles
Si d'autres dépendances posent problème, vérifiez :
- Compatibilité avec `compileSdk = 34`
- Versions AndroidX cohérentes
- Versions Kotlin compatibles

## Dépendances Principales du Projet

### Core Android
- `androidx.core:core-ktx:1.12.0`
- `androidx.appcompat:appcompat:1.6.1`
- `androidx.fragment:fragment-ktx:1.6.2`

### Navigation
- `androidx.navigation:navigation-fragment-ktx:2.7.5`
- `androidx.navigation:navigation-ui-ktx:2.7.5`

### Injection de Dépendances
- `com.google.dagger:hilt-android:2.48`

### Networking
- `com.squareup.retrofit2:retrofit:2.9.0`
- `com.squareup.retrofit2:converter-gson:2.9.0`

### Charts
- `com.github.PhilJay:MPAndroidChart:v3.1.4` ✅

## Commandes Utiles

```bash
# Nettoyer le projet
gradlew.bat clean

# Construire le projet
gradlew.bat build

# Voir l'arbre des dépendances
gradlew.bat app:dependencies

# Forcer le téléchargement des dépendances
gradlew.bat build --refresh-dependencies

# Arrêter le daemon Gradle
gradlew.bat --stop
```

## Support

Si vous rencontrez d'autres problèmes :
1. Vérifiez que Java JDK 8+ est installé
2. Assurez-vous que JAVA_HOME est configuré
3. Vérifiez votre connexion internet
4. Consultez les logs détaillés avec `--debug` ou `--info`