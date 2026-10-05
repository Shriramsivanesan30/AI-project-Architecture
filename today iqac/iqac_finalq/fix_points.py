"""
Fix Script: Reset point_claimed on all non-IQAC_APPROVED activities.
The old code incorrectly marked activities as point_claimed=True even though
they were only PENDING/SPOC_APPROVED/HOD_APPROVED.
This script resets them so the correct state is restored.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_activity_system.settings')
django.setup()

from activity_system.models import Activity

# Reset point_claimed=True on activities that are NOT IQAC_APPROVED
# (These were wrongly claimed by the old 50-pts-default code)
wrongly_claimed = Activity.objects.filter(point_claimed=True).exclude(status='IQAC_APPROVED')
count = wrongly_claimed.count()
wrongly_claimed.update(point_claimed=False)
print(f"Reset {count} wrongly claimed activities (non-IQAC_APPROVED).")

# Show current state
total = Activity.objects.count()
iqac_approved = Activity.objects.filter(status='IQAC_APPROVED').count()
correctly_claimed = Activity.objects.filter(status='IQAC_APPROVED', point_claimed=True).count()
unclaimed_approved = Activity.objects.filter(status='IQAC_APPROVED', point_claimed=False).count()

print(f"\nDatabase state after fix:")
print(f"  Total activities     : {total}")
print(f"  IQAC Approved        : {iqac_approved}")
print(f"  Correctly claimed    : {correctly_claimed}")
print(f"  Unclaimed (pending)  : {unclaimed_approved} <- these will trigger animation on next login")
print("Done.")
