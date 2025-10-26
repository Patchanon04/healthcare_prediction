# Generated migration for Chat models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('predictions', '0002_patient_userprofile_remove_transaction_age_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, help_text='Room name for group chats', max_length=255)),
                ('room_type', models.CharField(choices=[('direct', 'Direct Message'), ('group', 'Group Chat'), ('case', 'Case Discussion')], default='direct', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_rooms', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='chat_rooms', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(blank=True, help_text='Associated patient for case discussions', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='chat_rooms', to='predictions.patient')),
            ],
            options={
                'db_table': 'chat_rooms',
                'ordering': ['-updated_at'],
                'indexes': [
                    models.Index(fields=['room_type'], name='room_type_idx'),
                    models.Index(fields=['updated_at'], name='room_updated_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('attachment_url', models.URLField(blank=True, help_text='URL to attached file/image', max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_by', models.ManyToManyField(blank=True, related_name='read_messages', to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='predictions.chatroom')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'messages',
                'ordering': ['created_at'],
                'indexes': [
                    models.Index(fields=['room', 'created_at'], name='room_created_idx'),
                ],
            },
        ),
    ]
