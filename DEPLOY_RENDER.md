# Guide de Déploiement sur Render

## 🚀 Configuration Render

### Variables d'environnement requises

Dans le dashboard Render, configurez ces variables d'environnement :

```bash
# Django
DJANGO_SETTINGS_MODULE=beton_project.settings
SECRET_KEY=votre-clé-secrète-très-longue-et-sécurisée
DEBUG=False
ALLOWED_HOSTS=votre-app.onrender.com,127.0.0.1,localhost

# Base de données (automatique avec Render PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Superutilisateur (optionnel)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=motdepasse-sécurisé

# Python
PYTHON_VERSION=3.11.0
```

### Configuration du service

1. **Build Command** : `./build.sh`
2. **Start Command** : `gunicorn beton_project.wsgi:application`
3. **Environment** : `Python 3`

## 🔧 Résolution des Problèmes

### Erreur de Base de Données

Si vous rencontrez l'erreur :
```
django.db.backends.utils.py", line 105, in _execute
return self.cursor.execute(sql, params)
```

**Solutions :**

1. **Vérifiez la variable DATABASE_URL**
   ```bash
   # Doit être au format PostgreSQL
   postgresql://user:password@host:port/database
   ```

2. **Redéployez avec le nouveau build.sh**
   - Le script vérifie maintenant la connexion DB avant les migrations
   - Gestion améliorée des erreurs SSL

3. **Vérifiez les logs Render**
   ```bash
   # Dans le dashboard Render, section "Logs"
   # Recherchez les erreurs spécifiques
   ```

### Problèmes SSL

La configuration a été mise à jour pour :
- `ssl_require=False` : N'exige plus SSL strictement
- `sslmode=prefer` : Préfère SSL mais accepte les connexions non-SSL

### Migration manuelle

Si les migrations automatiques échouent :

```bash
# Connectez-vous au shell Render
python manage.py shell

# Vérifiez la connexion DB
from django.db import connection
connection.ensure_connection()

# Exécutez les migrations manuellement
python manage.py migrate --verbosity=2
```

## 📋 Checklist de Déploiement

- [ ] Variables d'environnement configurées
- [ ] Base de données PostgreSQL créée sur Render
- [ ] Build command : `./build.sh`
- [ ] Start command : `gunicorn beton_project.wsgi:application`
- [ ] Domaine personnalisé configuré (optionnel)
- [ ] SSL/TLS activé
- [ ] Logs vérifiés après déploiement

## 🆘 Support

En cas de problème persistant :

1. Vérifiez les logs Render en temps réel
2. Testez la connexion DB avec le script `deploy.py`
3. Contactez le support Render si nécessaire

## 📁 Fichiers Importants

- `build.sh` : Script de construction amélioré
- `deploy.py` : Script de diagnostic et déploiement
- `requirements.txt` : Dépendances Python
- `beton_project/settings.py` : Configuration Django mise à jour