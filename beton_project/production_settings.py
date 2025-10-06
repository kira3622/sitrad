# Configuration de sécurité pour la production sur Render
# Mise à jour pour forcer le redéploiement des fichiers statiques Material Dashboard
import os

# Configuration HTTPS pour la production uniquement (pas en développement local)
if os.environ.get('RENDER_EXTERNAL_HOSTNAME') and not os.environ.get('DEBUG', 'False') == 'True':
    # HTTPS/SSL Configuration
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookies sécurisés
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Configuration CSRF pour les domaines de confiance
    CSRF_TRUSTED_ORIGINS = [
        'https://sitrad-web.onrender.com',
        'https://*.onrender.com',
    ]
    
    # Headers de sécurité
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Proxy headers pour Render
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_TZ = True