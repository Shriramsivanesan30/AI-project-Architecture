import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_activity_system.settings')
django.setup()
from activity_system.models import Activity, User

# Show all non-IQAC activities and their point_claimed flag
acts = Activity.objects.exclude(status='IQAC_APPROVED')
print(f'Non-IQAC activities: {acts.count()}')
for a in acts:
    print(f'  [{a.status}] {a.faculty.username} - {a.sheet_name} | point_claimed={a.point_claimed}')

print()

# Check all faculty users and their calculated points
for u in User.objects.filter(role='FACULTY'):
    iqac_count = u.activities.filter(status='IQAC_APPROVED').count()
    pts = u.get_total_points()
    print(f'  {u.username}: total_pts={pts} | iqac_approved={iqac_count}')
