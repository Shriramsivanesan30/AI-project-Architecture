from django.db import models
from django.contrib.auth.models import AbstractUser


class Department(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.code} - {self.name}"


class User(AbstractUser):
    ROLE_CHOICES = (
        ('FACULTY', 'Faculty'),
        ('SPOC', 'SPOC'),
        ('HOD', 'HOD'),
        ('PC', 'PC'),
        ('IQAC', 'IQAC'),
        ('DEAN_RI', 'Dean (R&I)'),
    )
    CADRE_CHOICES = (
        ('Assistant Professor', 'Assistant Professor'),
        ('Assistant Professor (SS)', 'Assistant Professor (SS)'),
        ('Assistant professor(SG)', 'Assistant professor(SG)'),
        ('Associate Professor', 'Associate Professor'),
        ('Professor', 'Professor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='FACULTY')
    cadre = models.CharField(max_length=50, choices=CADRE_CHOICES, null=True, blank=True)
    department = models.CharField(max_length=50, default='IT')
    full_name = models.CharField(max_length=200, blank=True)
    profile_picture = models.FileField(upload_to='profiles/', null=True, blank=True)

    def get_research_target(self):
        targets = {
            'Assistant Professor': 200,
            'Assistant Professor (SS)': 250,
            'Assistant professor(SG)': 300,
            'Associate Professor': 350,
            'Professor': 400,
        }
        return targets.get(self.cadre, 0)

    def get_display_name(self):
        name = self.full_name or self.username
        # Clean up common redundant role appendages (e.g., "Name (HOD) (HOD)" -> "Name (HOD)")
        import re
        role_label = f"({self.role})"
        # If the name already has the role label once, and we were about to add it elsewhere, 
        # or if it has it twice, this regex will help deduplicate or just return the clean name.
        # However, the user wants us to *remove* the redundant part.
        # Let's just strip any trailing "(HOD)" "(SPOC)" etc if it matches the role.
        name = re.sub(r'\s*\(' + re.escape(self.role) + r'\)\s*\(' + re.escape(self.role) + r'\)$', f' ({self.role})', name)
        # Even simpler: if it has it twice, just replace double with single.
        name = name.replace(f'({self.role}) ({self.role})', f'({self.role})')
        return name.strip()

    def get_total_points(self):
        """Points are only awarded after full IQAC approval."""
        total = 0.0
        faculty_targets = {t.sheet_name: t.points for t in self.targets.all()}
        for act in self.activities.filter(status__in=['IQAC_APPROVED', 'DEAN_APPROVED']):
            if act.awarded_points is not None:
                total += float(act.awarded_points)
            elif act.category == 'Research':
                total += float(act.calculate_rpp_points())
            else:
                total += float(faculty_targets.get(act.sheet_name, 0))
        return round(total, 1)


class Activity(models.Model):
    STATUS_CHOICES = (
        ('OD_PENDING', 'Pending OD (SPOC)'),
        ('OD_SPOC_APPROVED', 'Pending OD (HOD)'),
        ('OD_APPROVED', 'OD Approved (Awaiting Proof)'),
        ('PENDING', 'Pending'),
        ('SPOC_APPROVED', 'SPOC Approved'),
        ('HOD_APPROVED', 'HOD Approved'),
        ('DEAN_APPROVED', 'Dean (R&I) Approved'),
        ('IQAC_APPROVED', 'IQAC Approved'),
        ('REJECTED', 'Rejected'),
    )

    requires_od = models.BooleanField(default=False)

    CATEGORY_CHOICES = (
        ('Faculty Development', 'Faculty Development'),
        ('Research', 'Research'),
        ('Student Activity', 'Student Activity'),
    )

    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    department = models.CharField(max_length=50, default='IT')
    sheet_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    academic_year = models.CharField(max_length=20)
    title = models.CharField(max_length=500, null=True, blank=True)
    data_json = models.JSONField(default=dict)
    proof_file = models.FileField(upload_to='proofs/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    remarks = models.TextField(null=True, blank=True)
    point_claimed = models.BooleanField(default=False)
    awarded_points = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.faculty.get_display_name()} — {self.sheet_name} ({self.status})"

    def get_status_badge(self):
        badges = {
            'OD_PENDING': 'badge-pending',
            'OD_SPOC_APPROVED': 'badge-spoc',
            'OD_APPROVED': 'badge-approved',
            'PENDING': 'badge-pending',
            'SPOC_APPROVED': 'badge-spoc',
            'HOD_APPROVED': 'badge-hod',
            'DEAN_APPROVED': 'badge-approved',
            'IQAC_APPROVED': 'badge-approved',
            'REJECTED': 'badge-rejected',
        }
        return badges.get(self.status, 'badge-pending')

    def get_status_icon(self):
        icons = {
            'OD_PENDING': '✈️',
            'OD_SPOC_APPROVED': '👍',
            'OD_APPROVED': '✅',
            'PENDING': '⏳',
            'SPOC_APPROVED': '✅',
            'HOD_APPROVED': '✅',
            'DEAN_APPROVED': '👨‍🔬',
            'IQAC_APPROVED': '🏆',
            'REJECTED': '❌',
        }
        return icons.get(self.status, '⏳')

    def calculate_rpp_points(self):
        """
        Calculates RPP points strictly per the official RPP matrix.
        Returns 0 for any activity type NOT in the RPP matrix
        (e.g. Google Scholar indexing, UGC Care List, PhD Registration,
        PhD Supervisor, Financial Support, Students In-house Seed Money).
        """
        data = self.data_json
        if not isinstance(data, dict):
            return 0

        def get_num(label, default=0):
            val = data.get(label, default)
            try:
                return float(val) if val else default
            except (TypeError, ValueError):
                return default

        def get_int(label, default=1):
            val = data.get(label, default)
            try:
                return int(float(val)) if val else default
            except (TypeError, ValueError):
                return default

        sn = self.sheet_name
        base_points = 0

        # ── Journal Publications ─────────────────────────────────────────────
        if sn == 'Journal Publications':
            idx = str(data.get('Indexed By', '')).strip().upper()
            if 'Q1' in idx or 'AHCI' in idx:
                base_points = 100        # Q1/AHCI Journal → 100 pts
            elif 'SCIE' in idx:
                base_points = 60         # SCIE Journal → 60 pts
            elif 'SCOPUS' in idx:
                base_points = 40         # Scopus Indexed Journal → 40 pts
            else:
                # Google Scholar, UGC Care List, Not Indexed → 0 per RPP matrix
                return 0

        # ── Book Chapter / Conference Paper (Scopus) → 20 pts ───────────────
        elif sn == 'Book Publication':
            idx = str(data.get('Indexing', '')).strip().upper()
            if 'SCOPUS' in idx:
                base_points = 20
            else:
                return 0  # Non-Scopus book chapters → 0 pts

        elif sn == 'Conference':
            idx = str(data.get('Indexing', '')).strip().upper()
            if 'SCOPUS' in idx:
                base_points = 20
            else:
                return 0  # Non-Scopus conference papers → 0 pts

        # ── Patent / IP ──────────────────────────────────────────────────────
        elif sn == 'Patent':
            p_type = str(data.get('Type of Patent', '')).strip()
            status = str(data.get('Published / Granted', '')).strip()
            if status == 'Granted':
                if p_type == 'Utility':
                    base_points = 100    # Utility Patent Grant → 100 pts
                else:
                    base_points = 10     # Design Registration / Copyright grant → 10 pts
            elif status in ('Published', 'Filed'):
                if p_type == 'Utility':
                    base_points = 20     # Utility Patent Filing & Publication → 20 pts
                else:
                    base_points = 10     # Design Registration / Copyright filing → 10 pts
            else:
                return 0

        # ── Technology Transfer → 100 pts ───────────────────────────────────
        elif sn == 'Technology Transfer':
            base_points = 100

        # ── Consultancy (10 pts per ₹1 lakh revenue) ────────────────────────
        elif sn in ('Consultancy (Project)', 'Consultancy (Training)'):
            revenue_lakhs = get_num('Revenue Generated (INR in Lakhs)')
            if revenue_lakhs > 0:
                base_points = max(10, int(revenue_lakhs * 10))
            else:
                return 0

        # ── Research Project (10 pts per ₹1 lakh funds) ─────────────────────
        elif sn == 'Research Project':
            funds_lakhs = get_num('Total Funds Provided (INR in Lakhs)')
            if funds_lakhs > 0:
                base_points = max(10, int(funds_lakhs * 10))
            else:
                return 0

        # ── Expert Certification → 50 pts ───────────────────────────────────
        elif sn == 'Expert Certification':
            base_points = 50

        # ── Skill Services → 10 pts ─────────────────────────────────────────
        elif sn == 'Skill Services':
            base_points = 10

        # ── Conference Organization (Scopus indexed only) → 100 pts ─────────
        elif sn == 'Conference Organization':
            idx = str(data.get('Indexing', '')).strip().upper()
            if 'SCOPUS' in idx:
                base_points = 100
            else:
                return 0  # Non-Scopus conference org → 0 pts per RPP

        # ── PhD Completion → 40 pts ─────────────────────────────────────────
        elif sn == 'PhD Completion':
            scholar_type = str(data.get('Scholar Type', '')).strip()
            if scholar_type in ('Full Time', 'Part Time Internal'):
                base_points = 40
            else:
                return 0

        else:
            # Sheets NOT in RPP matrix:
            # PhD Registration, PhD Supervisor, Financial Support (Research),
            # Students In-house Seed Money, and all Faculty/Student activity sheets
            return 0

        if base_points == 0:
            return 0

        # ── Contributor count ────────────────────────────────────────────────
        if sn == 'Conference Organization':
            contributors = get_int('Number of MCET Contributors in Role', 1)
        elif sn == 'PhD Completion':
            contributors = get_int('Number of MCET Contributors (for Guide Sharing)', 1)
        else:
            contributors = get_int('Total Number of MCET Contributors (including you)', 1)

        if contributors < 1:
            contributors = 1

        # ── PhD Scholar / Supervisor / Guide split ───────────────────────────
        is_phd_case = (
            str(data.get('Involves Ph.D. Scholar with MCET Guide?', '')).strip() == 'Yes'
            or sn == 'PhD Completion'
        )

        if sn == 'PhD Completion':
            role = str(data.get('Your Role', '')).strip()
        else:
            role = str(
                data.get('Your Role (if Ph.D. case)', '') or data.get('Your Role', '')
            ).strip()

        if is_phd_case and role and role != 'N/A':
            if role == 'Scholar':
                # Scholar gets FULL points (no sharing)
                return round(float(base_points), 1)
            elif role in ('Guide', 'Supervisor'):
                # Guide gets HALF points, split equally among MCET guides
                return round((base_points / 2.0) / contributors, 1)

        # ── Standard equal sharing among MCET contributors ───────────────────
        return round(float(base_points) / contributors, 1)



class DepartmentTarget(models.Model):
    department = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)
    sheet_name = models.CharField(max_length=255)
    target_count = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('department', 'academic_year', 'sheet_name')

    def __str__(self):
        return f"{self.department} - {self.sheet_name} ({self.academic_year}): {self.target_count}"


class FacultyTarget(models.Model):
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='targets')
    academic_year = models.CharField(max_length=20)
    sheet_name = models.CharField(max_length=255)
    target_count = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('faculty', 'academic_year', 'sheet_name')

    def __str__(self):
        return f"{self.faculty.username} - {self.sheet_name} ({self.academic_year}): {self.target_count}"
