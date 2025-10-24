"""
Management command to seed test accounts
Usage: python manage.py seed_accounts
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from predictions.models import UserProfile


class Command(BaseCommand):
    help = 'Seed database with test accounts'

    def handle(self, *args, **kwargs):
        accounts = [
            {
                'username': 'doctor1',
                'password': 'password123',
                'email': 'doctor1@hospital.com',
                'full_name': 'Dr. John Smith',
                'contact': '081-234-5678',
                'role': 'doctor'
            },
            {
                'username': 'nurse1',
                'password': 'password123',
                'email': 'nurse1@hospital.com',
                'full_name': 'Nurse Jane Doe',
                'contact': '082-345-6789',
                'role': 'nurse'
            },
            {
                'username': 'admin1',
                'password': 'password123',
                'email': 'admin1@hospital.com',
                'full_name': 'Admin User',
                'contact': '083-456-7890',
                'role': 'admin'
            },
            {
                'username': 'radiologist1',
                'password': 'password123',
                'email': 'radiologist1@hospital.com',
                'full_name': 'Dr. Sarah Johnson',
                'contact': '084-567-8901',
                'role': 'radiologist'
            },
        ]

        created_count = 0
        for account in accounts:
            # Check if user already exists
            if User.objects.filter(username=account['username']).exists():
                self.stdout.write(
                    self.style.WARNING(f"User '{account['username']}' already exists. Skipping.")
                )
                continue

            # Create user
            user = User.objects.create_user(
                username=account['username'],
                password=account['password'],
                email=account['email']
            )

            # Create profile
            UserProfile.objects.create(
                user=user,
                full_name=account['full_name'],
                contact=account['contact'],
                role=account['role']
            )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f"✅ Created user: {account['username']} ({account['role']})")
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Successfully created {created_count} accounts!")
        )
        
        if created_count > 0:
            self.stdout.write("\n📋 Account Details:")
            self.stdout.write("=" * 50)
            for account in accounts:
                self.stdout.write(f"Username: {account['username']}")
                self.stdout.write(f"Password: {account['password']}")
                self.stdout.write(f"Role: {account['role']}")
                self.stdout.write("-" * 50)
