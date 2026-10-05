"""Management command to create seed users for all 11 departments."""
from django.core.management.base import BaseCommand
from activity_system.models import User
from activity_system.sheet_config import DEPT_CODES


class Command(BaseCommand):
    help = 'Seed demo users for all 11 departments'

    def handle(self, *args, **options):
        roles = ['FACULTY', 'SPOC', 'HOD']

        for dept in DEPT_CODES:
            for role in roles:
                username = f"{dept.lower()}_{role.lower()}"
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        password='mcet@1234',
                        role=role,
                        department=dept,
                        full_name=f"{dept} {role.capitalize()}",
                        email=f"{username}@mcet.ac.in"
                    )
                    self.stdout.write(self.style.SUCCESS(f'  Created: {username}'))
                else:
                    self.stdout.write(f'  Exists: {username}')

        # IQAC user (institution-wide)
        if not User.objects.filter(username='iqac_admin').exists():
            User.objects.create_user(
                username='iqac_admin',
                password='mcet@1234',
                role='IQAC',
                department='IT',
                full_name='IQAC Coordinator',
                email='iqac@mcet.ac.in'
            )
            self.stdout.write(self.style.SUCCESS('  Created: iqac_admin'))

        self.stdout.write(self.style.SUCCESS('\nSeed complete! Login with password: mcet@1234'))
        self.stdout.write('\nSample users:')
        self.stdout.write('  it_faculty   / mcet@1234  (IT Faculty)')
        self.stdout.write('  it_spoc      / mcet@1234  (IT SPOC)')
        self.stdout.write('  it_hod       / mcet@1234  (IT HOD)')
        self.stdout.write('  cse_faculty  / mcet@1234  (CSE Faculty)')
        self.stdout.write('  iqac_admin   / mcet@1234  (IQAC)')
