import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_activity_system.settings')
django.setup()

from activity_system.models import User
from activity_system.sheet_config import DEPARTMENTS

departments = [d[0] for d in DEPARTMENTS]
roles = ['HOD', 'SPOC', 'PC', 'FACULTY']

print('Creating default users...')
for dept in departments:
    dept_lower = dept.lower()
    for role in roles:
        username = f'{dept_lower}_{role.lower()}'
        user_obj, created = User.objects.get_or_create(
            username=username, 
            defaults={
                'role': role, 
                'department': dept, 
                'full_name': f'{dept} {role}', 
                'is_staff': False, 
                'is_superuser': False
            }
        )
        if created:
            user_obj.set_password('mcet@1234')
            user_obj.save()
            print(f'Created user: {username}')
        else:
            print(f'User already exists: {username}')

iqac_user, created = User.objects.get_or_create(
    username='iqac_admin', 
    defaults={
        'role': 'IQAC', 
        'department': 'IT', 
        'full_name': 'IQAC Admin', 
        'is_staff': True, 
        'is_superuser': True
    }
)
if created:
    iqac_user.set_password('mcet@1234')
    iqac_user.save()
    print('Created iqac_admin')
print('Done.')
