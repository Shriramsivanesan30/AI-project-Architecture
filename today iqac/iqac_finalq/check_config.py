import os
import django
import sys

# Set up Django environment
sys.path.append('d:/iqac/iqac')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_activity_system.settings')
django.setup()

from activity_system.sheet_config import SHEETS_BY_CATEGORY, SHEET_CONFIG

print("SHEETS_BY_CATEGORY['Faculty Development']:")
print(SHEETS_BY_CATEGORY.get('Faculty Development'))
print("\n'Financial Support (Faculty)' in SHEET_CONFIG:")
print('Financial Support (Faculty)' in SHEET_CONFIG)
