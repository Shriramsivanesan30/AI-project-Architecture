import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_activity_system.settings')
django.setup()

from activity_system.models import Department
from activity_system.sheet_config import DEPARTMENTS

for code, name in DEPARTMENTS:
    dept, created = Department.objects.get_or_create(code=code, defaults={'name': name})
    if created:
        print(f"Created department: {code}")
    else:
        print(f"Department already exists: {code}")
print("Departments loaded.")
