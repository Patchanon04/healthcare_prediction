import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('predictions', '0006_appointment_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecondOpinionRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.TextField(help_text='Clinical question or context for the second opinion')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('completed', 'Completed'), ('declined', 'Declined')], default='pending', max_length=20)),
                ('due_at', models.DateTimeField(blank=True, help_text='Deadline for the response', null=True)),
                ('notes', models.TextField(blank=True, default='', help_text='Additional requester notes')),
                ('response', models.TextField(blank=True, default='', help_text="Responder's detailed answer")),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_second_opinions', to=settings.AUTH_USER_MODEL)),
                ('diagnosis', models.ForeignKey(blank=True, help_text='Primary diagnosis transaction for context', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='second_opinion_requests', to='predictions.transaction')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='second_opinion_requests', to='predictions.patient')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_second_opinions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'second_opinion_requests',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='secondopinionrequest',
            index=models.Index(fields=['status'], name='second_opinion_status_idx'),
        ),
        migrations.AddIndex(
            model_name='secondopinionrequest',
            index=models.Index(fields=['assignee', 'status'], name='second_opinion_assignee_status_idx'),
        ),
        migrations.AddIndex(
            model_name='secondopinionrequest',
            index=models.Index(fields=['patient'], name='second_opinion_patient_idx'),
        ),
    ]
