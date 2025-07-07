from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Importa las señales para registrarlas
        import core.signals # Reemplaza 'tu_app' con el nombre real de tu aplicación