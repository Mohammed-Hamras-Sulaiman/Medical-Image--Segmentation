from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


def copy_user_id(apps, schema_editor):
    MedicalImage = apps.get_model('segmentation', 'MedicalImage')
    User = apps.get_model('auth', 'User')

    # Get the default user (the first user in the database, or you can specify a condition here)
    default_user = User.objects.first()
    if not default_user:
        raise Exception("No users found in the database. Please create a user before running this migration.")

    # Assign default user to existing MedicalImage entries
    for image in MedicalImage.objects.all():
        image.user = default_user
        image.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('segmentation', '0002_rename_created_at_medicalimage_uploaded_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalimage',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.RunPython(copy_user_id),  # Populate the `user` field for existing data
        migrations.AlterField(
            model_name='medicalimage',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                null=False,  # Ensure `user` cannot be null after data migration
            ),
        ),
    ]
