from django.apps import AppConfig
from django.contrib.auth import get_user_model
import os

class InvoicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invoices'

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return

        try:
            User = get_user_model()
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser(
                    username="admin",
                    email="admin@example.com",
                    password="admin123"
                )
                print("✅ Superuser created!")
        except Exception as e:
            print("❌ Error creating superuser:", e)