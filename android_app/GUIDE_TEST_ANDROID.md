# Guide de Test - Application Android BetonApp

## 🎯 Objectif
Ce guide vous permet de tester l'application Android BetonApp avec l'API locale.

## ✅ Prérequis Validés
- ✅ API locale fonctionnelle sur `http://localhost:8000`
- ✅ Application Android construite avec succès
- ✅ Tests de simulation API réussis à 100%
- ✅ Configuration utilisateur de test prête

## 🚀 Méthodes de Test

### Méthode 1: Installation Automatique (Recommandée)
```bash
# Exécutez le script d'installation automatique
install_and_test.bat
```

### Méthode 2: Installation Manuelle

#### Étape 1: Préparer l'APK
```bash
# Construire l'application
gradlew.bat assembleDebug
```
L'APK sera généré dans: `app\build\outputs\apk\debug\app-debug.apk`

#### Étape 2: Installer sur l'appareil
1. **Avec ADB (appareil connecté):**
   ```bash
   adb install -r app\build\outputs\apk\debug\app-debug.apk
   ```

2. **Installation manuelle:**
   - Copiez `app-debug.apk` sur votre appareil Android
   - Activez "Sources inconnues" dans Paramètres > Sécurité
   - Ouvrez l'APK et installez

#### Étape 3: Configuration de l'application
1. Lancez l'application BetonApp
2. Allez dans les paramètres de l'application
3. Configurez l'URL de l'API:
   - **Pour émulateur:** `http://10.0.2.2:8000/api/v1`
   - **Pour appareil physique:** `http://[VOTRE_IP_PC]:8000/api/v1`

#### Étape 4: Test de connexion
1. **Identifiants de test:**
   - Nom d'utilisateur: `testuser`
   - Mot de passe: `testpass123`

2. **Tests à effectuer:**
   - ✅ Connexion utilisateur
   - ✅ Récupération des notifications
   - ✅ Affichage des détails de notification
   - ✅ Marquage comme lue/non lue
   - ✅ Rafraîchissement des données

## 🔧 Dépannage

### Problème: Impossible de se connecter à l'API
**Solutions:**
1. Vérifiez que l'API locale fonctionne:
   ```bash
   curl http://localhost:8000/api/v1/health/
   ```

2. Pour appareil physique, trouvez votre IP:
   ```bash
   ipconfig | findstr "IPv4"
   ```

3. Vérifiez le pare-feu Windows (port 8000)

### Problème: Erreur d'authentification
**Solutions:**
1. Vérifiez les identifiants dans l'application
2. Régénérez les tokens si nécessaire:
   ```bash
   python ..\generate_tokens.py
   ```

### Problème: Pas de notifications
**Solutions:**
1. Vérifiez que des notifications existent:
   ```bash
   python comprehensive_api_test.py
   ```

2. Créez des notifications de test si nécessaire

## 📱 Tests de Fonctionnalités

### Test 1: Authentification
- [ ] Ouvrir l'application
- [ ] Saisir les identifiants de test
- [ ] Vérifier la connexion réussie

### Test 2: Liste des Notifications
- [ ] Voir la liste des notifications
- [ ] Vérifier l'affichage des titres
- [ ] Vérifier les indicateurs lue/non lue

### Test 3: Détails de Notification
- [ ] Toucher une notification
- [ ] Voir les détails complets
- [ ] Vérifier le formatage du contenu

### Test 4: Marquage Lue/Non Lue
- [ ] Marquer une notification comme lue
- [ ] Vérifier le changement d'état
- [ ] Marquer comme non lue

### Test 5: Rafraîchissement
- [ ] Tirer pour rafraîchir
- [ ] Vérifier la mise à jour des données
- [ ] Vérifier les nouvelles notifications

### Test 6: Performance
- [ ] Navigation fluide entre les écrans
- [ ] Temps de chargement acceptable
- [ ] Pas de plantages ou erreurs

## 📊 Validation des Résultats

### Critères de Réussite
- ✅ Connexion API réussie
- ✅ Authentification fonctionnelle
- ✅ Notifications affichées correctement
- ✅ Interactions utilisateur fluides
- ✅ Synchronisation des états

### Métriques de Performance
- Temps de connexion: < 3 secondes
- Chargement des notifications: < 2 secondes
- Réactivité de l'interface: < 1 seconde

## 🔍 Logs et Débogage

### Capture des logs Android
```bash
# Logs généraux de l'application
adb logcat | findstr "BetonApp"

# Logs réseau
adb logcat | findstr "OkHttp\|Retrofit"

# Logs d'erreurs
adb logcat | findstr "ERROR\|FATAL"
```

### Logs de l'API
Les logs de l'API sont visibles dans le terminal où vous avez lancé:
```bash
python manage.py runserver
```

## 📋 Rapport de Test

Après les tests, documentez:
- [ ] Fonctionnalités testées
- [ ] Problèmes rencontrés
- [ ] Solutions appliquées
- [ ] Performance observée
- [ ] Recommandations

## 🎉 Conclusion

Si tous les tests passent, l'application Android BetonApp est prête pour:
- ✅ Déploiement en environnement de test
- ✅ Tests utilisateur étendus
- ✅ Intégration avec l'API de production

---

**Note:** Ce guide suppose que l'API locale fonctionne correctement. Tous les tests de simulation ont été validés avec succès.