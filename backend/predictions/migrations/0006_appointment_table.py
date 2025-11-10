from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('predictions', '0005_patient_created_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateTimeField(db_index=True)),
                ('duration_minutes', models.PositiveIntegerField(default=30, help_text='Duration in minutes')),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('no_show', 'No Show')], db_index=True, default='scheduled', max_length=20)),
                ('reason', models.TextField(blank=True, help_text='Reason for appointment')),
                ('notes', models.TextField(blank=True, help_text="Doctor's notes")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='predictions.patient')),
            ],
            options={
                'db_table': 'appointments',
                'ordering': ['appointment_date'],
                'indexes': [
                    models.Index(fields=['appointment_date'], name='appt_date_idx'),
                    models.Index(fields=['patient', 'appointment_date'], name='patient_appt_idx'),
                    models.Index(fields=['doctor', 'appointment_date'], name='doctor_appt_idx'),
                    models.Index(fields=['status'], name='appt_status_idx'),
                ],
            },
        ),
    ]
