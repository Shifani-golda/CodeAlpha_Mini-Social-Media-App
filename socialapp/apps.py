from django.apps import AppConfig

class SocialappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'socialapp'

    def ready(self):
        import socialapp.signals  # 👈 This line is VERY important




