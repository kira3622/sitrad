# Configuration Gunicorn pour le déploiement

# Configuration du worker
workers = 4  # Nombre de workers (2-4 x nombre de cœurs CPU)
worker_class = 'sync'  # Classe de worker (sync, eventlet, gevent, tornado)
worker_connections = 1000  # Nombre maximum de connexions par worker
max_requests = 1000  # Nombre maximum de requêtes avant le redémarrage du worker
max_requests_jitter = 50  # Jitter pour éviter le redémarrage simultané
timeout = 30  # Temps d'attente maximum pour une requête
keepalive = 2  # Temps de keepalive

# Configuration du binding
bind = '0.0.0.0:8000'  # Adresse et port d'écoute
backlog = 2048  # Nombre de connexions en attente maximum

# Configuration du logging
accesslog = '-'  # Fichier de log d'accès (- pour stdout)
errorlog = '-'  # Fichier de log d'erreurs (- pour stderr)
loglevel = 'info'  # Niveau de log (debug, info, warning, error, critical)
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuration du processus
daemon = False  # Ne pas exécuter en tant que daemon
pidfile = None  # Fichier PID (None pour désactiver)
user = None  # Utilisateur (None pour ne pas changer)
group = None  # Groupe (None pour ne pas changer)
tmp_upload_dir = None  # Répertoire temporaire pour les uploads

# Configuration de la sécurité
limit_request_line = 4094  # Taille maximum de la ligne de requête
limit_request_fields = 100  # Nombre maximum de champs de requête
limit_request_field_size = 8190  # Taille maximum d'un champ de requête

# Configuration du préchargement
preload_app = True  # Précharger l'application
reload = False  # Ne pas recharger automatiquement en production

# Nom de l'application
proc_name = 'beton_project'  # Nom du processus