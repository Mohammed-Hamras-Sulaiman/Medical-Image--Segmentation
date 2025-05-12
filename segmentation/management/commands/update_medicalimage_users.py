from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from segmentation.models import MedicalImage

class Command(BaseCommand):
    help = 'Update MedicalImage rows to associate with a default user'

    def handle(self, *args, **kwargs):
        # Assuming there is a default user you want to associate
        default_user = User.objects.get(username='your_default_user')  # Change this to your actual default user

        # Update existing rows to associate with default user
        updated_count = MedicalImage.objects.filter(user__isnull=True).update(user=default_user)
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} MedicalImage rows.'))
