# Guide de Déploiement sur Render

## 🚀 Statut du Déploiement

✅ **Code préparé et poussé vers GitHub**
✅ **Configuration Render prête**
❌ **Déploiement en cours/problème détecté**

## 📋 Étapes de Déploiement Manuel

### 1. Connexion à Render Dashboard
1. Allez sur [render.com](https://render.com)
2. Connectez-vous avec votre compte GitHub
3. Accédez au dashboard

### 2. Création du Service Web
1. Cliquez sur "New +" → "Web Service"
2. Connectez votre repository GitHub : `kira3622/sitrad`
3. Configurez les paramètres :
   - **Name**: `beton-project`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn beton_project.wsgi:application`

### 3. Variables d'Environnement
Ajoutez ces variables dans l'onglet "Environment" :

```
PYTHON_VERSION=3.11.0
DJANGO_SETTINGS_MODULE=beton_project.production_settings
DEBUG=False
ALLOWED_HOSTS=beton-project.onrender.com
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
DATABASE_URL=[sera automatiquement défini par la base de données]
```

### 4. Création de la Base de Données
1. Cliquez sur "New +" → "PostgreSQL"
2. Configurez :
   - **Name**: `beton-db`
   - **Database**: `beton_db`
   - **User**: `beton_user`
   - **Plan**: Free

### 5. Liaison Base de Données
1. Dans le service web, allez dans "Environment"
2. Ajoutez `DATABASE_URL` et liez-la à votre base PostgreSQL

## 🔧 Configuration des Fichiers

### render.yaml (Déjà configuré)
```yaml
services:
  - type: web
    name: beton-project
    env: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn beton_project.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DJANGO_SETTINGS_MODULE
        value: beton_project.production_settings
      - key: DEBUG
        value: False
      - key: ALLOWED_HOSTS
        value: beton-project.onrender.com
      - key: DJANGO_SUPERUSER_USERNAME
        value: admin
      - key: DJANGO_SUPERUSER_EMAIL
        value: admin@example.com
      - key: DJANGO_SUPERUSER_PASSWORD
        value: admin123
      - key: DATABASE_URL
        fromDatabase:
          name: beton-db
          property: connectionString

databases:
  - name: beton-db
    databaseName: beton_db
    user: beton_user
    plan: free
```

## 🐛 Dépannage

### Problème 404
- Vérifiez que le service est déployé et en cours d'exécution
- Vérifiez les logs de build et de déploiement
- Assurez-vous que `ALLOWED_HOSTS` inclut votre domaine Render

### Problèmes de Base de Données
- Vérifiez que `DATABASE_URL` est correctement configuré
- Assurez-vous que les migrations sont exécutées dans `build.sh`

### Problèmes de Fichiers Statiques
- Vérifiez que `collectstatic` s'exécute dans `build.sh`
- Assurez-vous que `STATIC_ROOT` est configuré dans `production_settings.py`

## 📊 Vérification Post-Déploiement

Une fois le déploiement réussi, testez :

1. **Page d'accueil** : `https://beton-project.onrender.com/`
2. **Interface admin** : `https://beton-project.onrender.com/admin/`
3. **Module production** : `https://beton-project.onrender.com/production/`
4. **Calcul des matières** : `https://beton-project.onrender.com/production/preview-sorties/`

## 🔗 Liens Utiles

- **Repository GitHub** : https://github.com/kira3622/sitrad
- **Render Dashboard** : https://dashboard.render.com
- **URL de Production** : https://beton-project.onrender.com (une fois déployé)

## 📝 Notes Importantes

1. Le premier déploiement peut prendre 10-15 minutes
2. Render peut mettre en veille les services gratuits après 15 minutes d'inactivité
3. Le réveil d'un service en veille peut prendre 30-60 secondes
4. Surveillez les logs de déploiement pour identifier les problèmes

## 🆘 Support

Si le déploiement échoue :
1. Vérifiez les logs dans Render Dashboard
2. Assurez-vous que tous les fichiers sont poussés vers GitHub
3. Vérifiez la configuration des variables d'environnement
4. Testez le build localement avec `./build.sh`