from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Create seed super admin user"

    def handle(self, *args, **options):
        user = User.objects.filter(username="admin").first()

        if user:
            user.delete()

        User.objects.create_superuser(
            email="admin@admin.com",
            username="admin",
            password="admin",
            address_cp=37170,
        )
