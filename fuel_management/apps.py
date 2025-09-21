from django.apps import AppConfig


class FuelManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fuel_management'
    verbose_name = 'Gestion du Gasoil'
    
    def ready(self):
        """Méthode appelée quand l'application est prête"""
        # Importer les signaux pour les enregistrer automatiquement
        import fuel_management.signals
