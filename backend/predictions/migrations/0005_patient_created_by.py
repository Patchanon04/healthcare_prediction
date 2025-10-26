# Generated migration to add created_by field to Patient model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('predictions', '0004_treatment_management'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='created_by',
            field=models.ForeignKey(
                help_text='User who created this patient',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='patients',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddIndex(
            model_name='patient',
            index=models.Index(fields=['created_by', '-created_at'], name='patient_created_by_idx'),
        ),
    ]
