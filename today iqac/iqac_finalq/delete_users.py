import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_activity_system.settings')
django.setup()

from activity_system.models import User

usernames_to_delete = [
    'admin',
    'faculty1',
    'Faculty',
    'hod1',
    'Hod',
    'iqac1',
    'spoc1',
    'Spoc'
]

for username in usernames_to_delete:
    users = User.objects.filter(username__iexact=username)
    if users.exists():
        count = users.count()
        users.delete()
        print(f"Deleted {count} user(s) matching '{username}'")
    else:
        print(f"User '{username}' not found.")

print("Cleanup complete.")
