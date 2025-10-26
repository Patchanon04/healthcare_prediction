# Generated migration for Treatment Management models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('predictions', '0003_chatroom_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='TreatmentPlan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Treatment plan title', max_length=200)),
                ('description', models.TextField(help_text='Detailed treatment plan')),
                ('start_date', models.DateField(help_text='Treatment start date')),
                ('end_date', models.DateField(blank=True, help_text='Expected end date', null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_treatment_plans', to=settings.AUTH_USER_MODEL)),
                ('diagnosis', models.ForeignKey(blank=True, help_text='Related diagnosis/transaction', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='treatment_plans', to='predictions.transaction')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='treatment_plans', to='predictions.patient')),
            ],
            options={
                'db_table': 'treatment_plans',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Medication',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('drug_name', models.CharField(help_text='Medication name', max_length=200)),
                ('dosage', models.CharField(help_text='Dosage (e.g., 500mg)', max_length=100)),
                ('frequency', models.CharField(help_text='Frequency (e.g., twice daily)', max_length=100)),
                ('route', models.CharField(blank=True, help_text='Route of administration (e.g., oral, IV)', max_length=50)),
                ('instructions', models.TextField(blank=True, help_text='Special instructions')),
                ('start_date', models.DateField(help_text='Start date')),
                ('end_date', models.DateField(blank=True, help_text='End date', null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('discontinued', 'Discontinued')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medications', to='predictions.patient')),
                ('prescribed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prescribed_medications', to=settings.AUTH_USER_MODEL)),
                ('treatment_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='medications', to='predictions.treatmentplan')),
            ],
            options={
                'db_table': 'medications',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='FollowUpNote',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Note title', max_length=200)),
                ('note', models.TextField(help_text='Follow-up note content')),
                ('note_type', models.CharField(choices=[('checkup', 'Check-up'), ('progress', 'Progress Update'), ('complication', 'Complication'), ('other', 'Other')], default='progress', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_followup_notes', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followup_notes', to='predictions.patient')),
                ('treatment_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followup_notes', to='predictions.treatmentplan')),
            ],
            options={
                'db_table': 'followup_notes',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='treatmentplan',
            index=models.Index(fields=['patient', '-created_at'], name='patient_treatment_idx'),
        ),
        migrations.AddIndex(
            model_name='medication',
            index=models.Index(fields=['patient', '-start_date'], name='patient_medication_idx'),
        ),
        migrations.AddIndex(
            model_name='followupnote',
            index=models.Index(fields=['patient', '-created_at'], name='patient_followup_idx'),
        ),
    ]
