import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_activity_system.settings')
django.setup()

from activity_system.models import User

NEW_PASSWORD = 'mcet@1234'

print(f'Updating passwords to: {NEW_PASSWORD}...')
users = User.objects.all()
count = 0
for user in users:
    user.set_password(NEW_PASSWORD)
    user.save()
    count += 1

print(f'Done. Updated passwords for {count} users.')
