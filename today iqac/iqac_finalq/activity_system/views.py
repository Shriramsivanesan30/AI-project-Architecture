from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import models as db_models
from io import BytesIO
import json
import pandas as pd
from .models import Activity, User, Department, DepartmentTarget, FacultyTarget
from .sheet_config import SHEET_CONFIG, SHEETS_BY_CATEGORY, ACADEMIC_YEARS

def get_departments():
    return [(d.code, d.name) for d in Department.objects.all()]

from .export_utils import generate_consolidation_df


def _get_target_progress(user, active_role, current_year='2025-2026'):
    """Helper to calculate target progress for a user's department."""
    target_progress = []
    if active_role in ['HOD', 'SPOC', 'FACULTY']:
        dept_targets = DepartmentTarget.objects.filter(department=user.department, academic_year=current_year)
        for dt in dept_targets:
            achieved = Activity.objects.filter(
                department=user.department,
                sheet_name=dt.sheet_name,
                academic_year=dt.academic_year,
                status__in=['IQAC_APPROVED', 'DEAN_APPROVED'],
            ).count()
            gap = max(0, dt.target_count - achieved)
            pct = min(100, int((achieved / dt.target_count * 100) if dt.target_count else 0))
            target_progress.append({
                'dept': user.department,
                'sheet_name': dt.sheet_name,
                'category': SHEET_CONFIG.get(dt.sheet_name, {}).get('category', 'Other'),
                'academic_year': dt.academic_year,
                'target': dt.target_count,
                'achieved': achieved,
                'gap': gap,
                'pct': pct,
            })
    return target_progress


# ─────────────────────────────────────────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Authenticate with actual username and password
        user = authenticate(request, username=username, password=password)
        
        if user:
            # Always default to the user's assigned role on initial login
            request.session['active_role'] = user.role
            login(request, user)
            return redirect('dashboard')
        
        messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'login.html', {
        'departments': get_departments(),
    })


def logout_view(request):
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user = request.user
    role = request.session.get('active_role', user.role)
    
    # Allow switching to list view for admin roles
    if request.GET.get('view') == 'list' and role in ['IQAC', 'DEAN_RI']:
        return iqac_dashboard(request)

    if role == 'FACULTY':
        return faculty_dashboard(request)
    elif role == 'IQAC':
        return iqac_dashboard(request)
    elif role == 'DEAN_RI':
        return dean_research_dashboard(request)
    else:  # SPOC, HOD, PC
        return approval_dashboard(request)


@login_required
def faculty_dashboard(request):
    user = request.user
    activities = Activity.objects.filter(faculty=user)
    stats = {
        'total': activities.count(),
        'pending': activities.exclude(status__in=['IQAC_APPROVED', 'DEAN_APPROVED', 'REJECTED']).count(),
        'approved': activities.filter(status__in=['IQAC_APPROVED', 'DEAN_APPROVED']).count(),
        'rejected': activities.filter(status='REJECTED').count(),
    }
    recent = activities[:10]
    # Target Progress Calculation
    target_progress = []
    academic_year = '2025-2026'
    faculty_targets = FacultyTarget.objects.filter(faculty=user, academic_year=academic_year)
    for ft in faculty_targets:
        achieved = Activity.objects.filter(
            faculty=user,
            sheet_name=ft.sheet_name,
            academic_year=academic_year,
            status__in=['IQAC_APPROVED', 'DEAN_APPROVED']
        ).count()
        gap = max(0, ft.target_count - achieved)
        pct = min(100, int((achieved/ft.target_count*100) if ft.target_count else 0))
        target_progress.append({
            'sheet': ft.sheet_name,
            'sheet_cat': SHEET_CONFIG.get(ft.sheet_name, {}).get('category', ''),
            'target': ft.target_count,
            'points': ft.points,
            'achieved': achieved,
            'gap': gap,
            'pct': pct
        })

    # Global RPP Research Target progress
    research_activities = activities.filter(category='Research', status__in=['IQAC_APPROVED', 'DEAN_APPROVED'], academic_year=academic_year)
    total_research_points = 0
    for a in research_activities:
        if a.awarded_points is not None:
            total_research_points += a.awarded_points
        else:
            total_research_points += a.calculate_rpp_points()
            
    research_target = user.get_research_target()
    research_pct = min(100, int((total_research_points / research_target * 100) if research_target else 0))
    research_gap = max(0, research_target - total_research_points)

    # Identify newly approved activities (unclaimed points)
    newly_approved_ids = list(activities.filter(status__in=['IQAC_APPROVED', 'DEAN_APPROVED'], point_claimed=False).values_list('id', flat=True))
    newly_approved = activities.filter(id__in=newly_approved_ids)
    
    # Calculate points to award in animation (float-safe)
    anim_points = 0.0
    targets_map = {t.sheet_name: t.points for t in faculty_targets}
    for act in newly_approved:
        if act.awarded_points is not None:
            anim_points += float(act.awarded_points)
        elif act.category == 'Research':
            anim_points += float(act.calculate_rpp_points())
        else:
            anim_points += float(targets_map.get(act.sheet_name, 0))
    anim_points = round(anim_points, 1)
    
    # Mark as claimed AFTER calculating — prevents double-animation on refresh
    if newly_approved_ids:
        activities.filter(id__in=newly_approved_ids).update(point_claimed=True)

    return render(request, 'dashboards/faculty.html', {
        'activities': recent,
        'stats': stats,
        'anim_points': anim_points,
        'target_progress': target_progress,
        'sheets_by_category': SHEETS_BY_CATEGORY,
        'cat_count_fd': len(SHEETS_BY_CATEGORY.get('Faculty Development', [])),
        'cat_count_r': len(SHEETS_BY_CATEGORY.get('Research', [])),
        'cat_count_sa': len(SHEETS_BY_CATEGORY.get('Student Activity', [])),
        'cat_count_ir': len(SHEETS_BY_CATEGORY.get('Industrial Relationship', [])),
        'cat_count_as': len(SHEETS_BY_CATEGORY.get('Association', [])),
    })


@login_required
def approval_dashboard(request):
    user = request.user
    active_role = request.session.get('active_role', user.role)
    # Flow: Faculty (PENDING) → SPOC (SPOC_APPROVED) → HOD (HOD_APPROVED) → IQAC
    status_map = {
        'SPOC': ['PENDING', 'OD_PENDING'],
        'PC': ['PENDING', 'OD_PENDING'],
        'HOD': ['SPOC_APPROVED', 'OD_SPOC_APPROVED', 'PENDING'], 
    }
    target_statuses = status_map.get(active_role, ['PENDING'])

    # SPOC and HOD are scoped to their department
    base_qs = Activity.objects.filter(department=user.department)
    
    all_activities = base_qs
    
    pending_activities = base_qs.filter(status__in=target_statuses)
    all_activities = all_activities.order_by('-created_at')

    cat_data = all_activities.values('category').annotate(count=db_models.Count('id'))
    status_data = all_activities.values('status').annotate(count=db_models.Count('id'))

    analytics = {
        'total': all_activities.count(),
        'pending': all_activities.exclude(status__in=['IQAC_APPROVED', 'DEAN_APPROVED', 'REJECTED']).count(),
        'approved': all_activities.filter(status__in=['IQAC_APPROVED', 'DEAN_APPROVED']).count(),
        'rejected': all_activities.filter(status='REJECTED').count(),
        'cat_labels': json.dumps([c['category'] for c in cat_data]),
        'cat_counts': json.dumps([c['count'] for c in cat_data]),
        'status_labels': json.dumps([s['status'] for s in status_data]),
        'status_counts': json.dumps([s['count'] for s in status_data]),
    }

    # Target Logic for HOD
    current_year = '2025-2026'
    target_progress = _get_target_progress(user, active_role, current_year)
    faculty_list = User.objects.filter(department=user.department, role__in=['FACULTY', 'SPOC', 'HOD'])
    all_sheets = list(SHEET_CONFIG.keys())
    iqac_fixed_sheets = DepartmentTarget.objects.filter(
        department=user.department, academic_year=current_year
    ).values_list('sheet_name', flat=True).distinct()
        
    # Consolidation data for HOD preview
    if active_role in ['HOD', 'SPOC']:
        df_consolidation = generate_consolidation_df(base_qs, academic_year=ACADEMIC_YEARS[0])
        consolidation_rows = df_consolidation.to_dict('records')
    else:
        consolidation_rows = []

    active_iqac = any(t['category'] != 'Research' and t['gap'] > 0 for t in target_progress)
    active_res = any(t['category'] == 'Research' and t['gap'] > 0 for t in target_progress)
    any_completed = any(t['gap'] == 0 for t in target_progress)

    return render(request, 'dashboards/approval.html', {
        'dept_obj': Department.objects.filter(code=user.department).first(),
        'pending_activities': pending_activities,
        'all_activities': all_activities,
        'analytics': analytics,
        'departments': get_departments(),
        'faculty_list': faculty_list,
        'academic_years': ACADEMIC_YEARS,
        'target_progress': target_progress,
        'consolidation_rows': consolidation_rows,
        'all_sheets': all_sheets,
        'iqac_fixed_sheets': iqac_fixed_sheets,
        'active_iqac': active_iqac,
        'active_res': active_res,
        'any_completed': any_completed,
        'active_role': active_role,
    })


@login_required
def dean_research_dashboard(request):
    user = request.user
    role = request.session.get('active_role', user.role)
    if role != 'DEAN_RI':
        return redirect('dashboard')
        
    current_year = '2025-2026'
    # Base Research Activities across college
    research_qs = Activity.objects.filter(category='Research', academic_year=current_year)
    
    # Institution Research Stats
    stats = {
        'total': research_qs.count(),
        'approved': research_qs.filter(status__in=['IQAC_APPROVED', 'DEAN_APPROVED']).count(),
        'pending': research_qs.exclude(status__in=['IQAC_APPROVED', 'DEAN_APPROVED', 'REJECTED']).count(),
        'rejected': research_qs.filter(status='REJECTED').count(),
    }
    
    # Research stages breakdown
    res_cats = {
       'Journal': research_qs.filter(sheet_name='Journal Publications').count(),
       'PatentIPR': research_qs.filter(sheet_name__in=['Patent', 'IPR-Preparation']).count(),
       'Conference': research_qs.filter(sheet_name='Conference').count(),
       'Funding': research_qs.filter(sheet_name__in=['Research Project', 'Research-Funding-Submitted']).count(),
       'Consultancy': research_qs.filter(sheet_name__startswith='Consultancy').count(),
    }
    
    # Top departments by research
    dept_res = research_qs.values('department').annotate(count=db_models.Count('id')).order_by('-count')
    dept_labels = [d['department'] for d in dept_res]
    dept_counts = [d['count'] for d in dept_res]

    # Category breakdown per department for drill-down
    dept_cat_data = {}
    for d_code in dept_labels:
        d_qs = research_qs.filter(department=d_code)
        dept_cat_data[d_code] = {
            'Journal': d_qs.filter(sheet_name='Journal Publications').count(),
            'PatentIPR': d_qs.filter(sheet_name__in=['Patent', 'IPR-Preparation']).count(),
            'Conference': d_qs.filter(sheet_name='Conference').count(),
            'Funding': d_qs.filter(sheet_name__in=['Research Project', 'Research-Funding-Submitted']).count(),
            'Consultancy': d_qs.filter(sheet_name__startswith='Consultancy').count(),
        }
    
    # Comprehensive research list for in-page filtering
    dept_filter = request.GET.get('dept', None)
    all_research = research_qs.select_related('faculty').order_by('-created_at')
    if dept_filter:
        all_research = all_research.filter(department=dept_filter)
    all_research = all_research[:200]
    
    # Research sheets for target assignment
    research_sheets = [k for k,v in SHEET_CONFIG.items() if v['category'] == 'Research']
    
    # Logic for department research dots
    all_depts = Department.objects.all()
    dept_stats = []
    for d in all_depts:
        pending_count = research_qs.filter(department=d.code, status='HOD_APPROVED').count()
        dept_stats.append({
            'code': d.code,
            'name': d.name,
            'pending_count': pending_count
        })

    return render(request, 'dashboards/dean_ri.html', {
        'stats': stats,
        'res_cats': res_cats,
        'dept_labels': dept_labels,
        'dept_counts': dept_counts,
        'dept_cat_data': dept_cat_data,
        'all_research': all_research,
        'departments': get_departments(),
        'dept_stats': dept_stats,
        'dept_filter': dept_filter,
        'research_sheets': research_sheets,
        'current_year': current_year,
    })


@login_required
def iqac_dashboard(request):
    dept_filter = request.GET.get('dept', '')
    sheet_filter = request.GET.get('sheet', '')
    cat_filter = request.GET.get('cat', '')
    status_filter = request.GET.get('status', '')

    # Define querysets: base_qs for stats (no status filter), qs for only viewable items (table)
    base_qs = Activity.objects.exclude(category='Research')
    if dept_filter:
        base_qs = base_qs.filter(department=dept_filter)
    if sheet_filter:
        base_qs = base_qs.filter(sheet_name=sheet_filter)
    if cat_filter:
        base_qs = base_qs.filter(category=cat_filter)
    
    # Identify activities strictly pending IQAC approval (HOD Approved)
    # Requirement: Exclude Research from IQAC
    pending_iqac = Activity.objects.filter(status='HOD_APPROVED').exclude(category='Research')

    # Logic for department dots
    all_depts = Department.objects.all()
    dept_stats = []
    for d in all_depts:
        pending_count = Activity.objects.filter(department=d.code, status='HOD_APPROVED').exclude(category='Research').count()
        dept_stats.append({
            'code': d.code,
            'name': d.name,
            'pending_count': pending_count
        })
    if dept_filter:
        pending_iqac = pending_iqac.filter(department=dept_filter)
    if sheet_filter:
        pending_iqac = pending_iqac.filter(sheet_name=sheet_filter)

    # Current table view (restricted) - includes HOD_APPROVED, IQAC_APPROVED, and REJECTED
    qs = base_qs
    if status_filter:
        qs = qs.filter(status=status_filter)
    else:
        qs = qs.filter(status__in=['HOD_APPROVED', 'IQAC_APPROVED', 'REJECTED'])

    # Analytics should reflect everything in the institution based on dept/sheet filters
    cat_data = base_qs.values('category').annotate(count=db_models.Count('id'))
    status_data = base_qs.values('status').annotate(count=db_models.Count('id'))
    dept_data = base_qs.values('department').annotate(count=db_models.Count('id'))

    analytics = {
        'total': base_qs.count(),
        'pending': base_qs.exclude(status__in=['IQAC_APPROVED', 'REJECTED']).count(),
        'approved': base_qs.filter(status='IQAC_APPROVED').count(),
        'rejected': base_qs.filter(status='REJECTED').count(),
        'cat_labels': [c['category'] for c in cat_data],
        'cat_counts': [c['count'] for c in cat_data],
        'status_labels': [s['status'] for s in status_data],
        'status_counts': [s['count'] for s in status_data],
        'dept_labels': [d['department'] for d in dept_data],
        'dept_counts': [d['count'] for d in dept_data],
    }

    all_sheets = [k for k, v in SHEET_CONFIG.items() if v.get('category') != 'Research']

    # Target Progress for IQAC
    current_year = '2025-2026'
    targets = DepartmentTarget.objects.filter(academic_year=current_year)
    if dept_filter:
        targets = targets.filter(department=dept_filter)
    
    target_progress = []
    for t in targets:
        if SHEET_CONFIG.get(t.sheet_name, {}).get('category') == 'Research':
            continue
            
        achieved = Activity.objects.filter(
            department=t.department, 
            sheet_name=t.sheet_name, 
            academic_year=t.academic_year, 
            status__in=['IQAC_APPROVED', 'DEAN_APPROVED']
        ).count()
        
        pct = min(100, int((achieved / t.target_count * 100) if t.target_count else 0))
        
        target_progress.append({
            'dept': t.department,
            'sheet_name': t.sheet_name,
            'target': t.target_count,
            'achieved': achieved,
            'gap': max(0, t.target_count - achieved),
            'pct': pct
        })

    df_consolidation = generate_consolidation_df(qs, academic_year=ACADEMIC_YEARS[0])
    consolidation_rows = df_consolidation.to_dict('records')

    return render(request, 'dashboards/iqac.html', {
        'activities': qs.order_by('-created_at'),
        'pending_iqac': pending_iqac,
        'analytics': analytics,
        'departments': get_departments(),
        'dept_stats': dept_stats,
        'all_sheets': all_sheets,
        'targets': targets,
        'target_progress': target_progress,
        'consolidation_rows': consolidation_rows,
        'academic_years': ACADEMIC_YEARS,
        'dept_filter': dept_filter,
        'sheet_filter': sheet_filter,
        'status_filter': status_filter,
    })


@login_required
def department_exports(request):
    if request.session.get('active_role', request.user.role) != 'IQAC':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    return render(request, 'dashboards/department_exports.html', {
        'departments': get_departments(),
        'academic_years': ACADEMIC_YEARS,
    })

@login_required
def submit_activity(request):
    allowed_roles = ['FACULTY', 'DEAN_RI']
    active_role = request.session.get('active_role', request.user.role)
    if active_role not in allowed_roles:
        messages.error(request, "Only faculty members can submit activities.")
        return redirect('dashboard')

    if request.method == 'POST':
        sheet_name = request.POST.get('sheet_name')
        academic_year = request.POST.get('academic_year')

        if sheet_name not in SHEET_CONFIG:
            messages.error(request, "Invalid sheet selected.")
            return redirect('submit_activity')

        config = SHEET_CONFIG[sheet_name]
        category = config['category']

        # The title is the first text field value for that sheet
        fields = config['fields']
        title_value = request.POST.get(fields[0]['name'], sheet_name) if fields else sheet_name

        # Collect all field data, respecting the OD hide flag
        data = {}
        requires_od = request.POST.get('requires_od') == 'on'
        if category != 'Faculty Development' and category != 'Student Activity':
            requires_od = False

        for field in fields:
            if requires_od and field.get('hide_on_od'):
                continue
            val = request.POST.get(field['name'], '').strip()
            
            # Skip validation if field is explicitly not required and empty
            if not val:
                if not field.get('required', True):
                    data[field['label']] = val
                    continue
                else:
                    messages.error(request, f"Please fill in all required fields. '{field['label']}' is required.")
                    return redirect('submit_activity')
            
            data[field['label']] = val

        initial_status = 'OD_PENDING' if requires_od else 'PENDING'
        proof_file = request.FILES.get('proof_file')
        
        # Superior (Dean R&I) bypasses SPOC/HOD but NOW goes to IQAC for final validation
        if request.user.role == 'DEAN_RI':
            initial_status = 'HOD_APPROVED'
            requires_od = False

        obj = Activity.objects.create(
            faculty=request.user,
            department=request.user.department,
            sheet_name=sheet_name,
            category=category,
            academic_year=academic_year,
            title=title_value,
            data_json=data,
            requires_od=requires_od,
            status=initial_status,
        )

        if proof_file:
            obj.proof_file = proof_file
            obj.save()

        if request.user.role == 'DEAN_RI':
            msg = "Activity submitted for IQAC approval (Dean R&I submission)."
        else:
            msg = "OD request submitted for SPOC approval." if requires_od else "Activity submitted for SPOC approval."
        
        messages.success(request, f'✅ {msg}')
        return redirect('dashboard')

    return render(request, 'submit_activity.html', {
        'sheets_by_category': SHEETS_BY_CATEGORY,
        'sheet_config_json': json.dumps(SHEET_CONFIG),
        'academic_years': ACADEMIC_YEARS,
        'departments': get_departments(),
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACTIVITY DETAIL
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    user = request.user
    active_role = request.session.get('active_role', user.role)

    # Access control
    if active_role == 'FACULTY' and activity.faculty != user:
        messages.error(request, "You can only view your own activities.")
        return redirect('dashboard')
    if active_role in ['SPOC', 'HOD'] and activity.department != user.department:
        messages.error(request, "You can only view activities from your department.")
        return redirect('dashboard')
        
    config = SHEET_CONFIG.get(activity.sheet_name, {})
    od_fields = [f for f in config.get('fields', []) if f.get('hide_on_od')]

    if request.method == 'POST' and user.role == 'FACULTY' and activity.status == 'OD_APPROVED':
        proof_file = request.FILES.get('proof_file')
        if proof_file:
            # Update data_json with the now-revealed fields
            data = activity.data_json or {}
            for field in od_fields:
                val = request.POST.get(field['name'], '')
                data[field['label']] = val
            
            activity.data_json = data
            activity.proof_file = proof_file
            activity.status = 'PENDING'  # Restart approval flow with actual proof
            activity.save()
            messages.success(request, "Proof uploaded and details updated successfully! Activity is now pending SPOC approval.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please select a file to upload.")

    spoc = User.objects.filter(role='SPOC', department=activity.department).first()
    hod = User.objects.filter(role='HOD', department=activity.department).first()

    return render(request, 'activity_detail.html', {
        'activity': activity,
        'spoc': spoc,
        'hod': hod,
        'od_fields': od_fields,
        'active_role': active_role,
    })

# ─────────────────────────────────────────────────────────────────────────────
# APPROVE / REJECT
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def approve_activity(request, pk, action):
    activity = get_object_or_404(Activity, pk=pk)
    user = request.user
    active_role = request.session.get('active_role', user.role)

    # Scope guard
    if active_role in ['SPOC', 'HOD'] and activity.department != user.department:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    if action == 'approve':
        status_progression = {
            'SPOC': 'SPOC_APPROVED',
            'HOD': 'HOD_APPROVED',
            'DEAN_RI': 'DEAN_APPROVED', # Final research terminal
            'IQAC': 'IQAC_APPROVED',   # Final standard terminal
        }
        od_status_progression = {
            'SPOC': 'OD_SPOC_APPROVED',
            'HOD': 'OD_APPROVED',
        }
        if activity.status in ['OD_PENDING', 'OD_SPOC_APPROVED']:
            activity.status = od_status_progression.get(active_role, activity.status)
        else:
            # Special case: If Research activity is at HOD_APPROVED, it goes to DEAN_RI
            # If Non-research activity is at HOD_APPROVED, it goes to IQAC
            activity.status = status_progression.get(active_role, activity.status)
        
        # Point calculation and mark claimed only at terminal states
        if activity.status in ['DEAN_APPROVED', 'IQAC_APPROVED']:
             if activity.category == 'Research' and activity.awarded_points is None:
                  activity.awarded_points = activity.calculate_rpp_points()
             activity.point_claimed = False # Reveal animation on faculty dashboard
        
        activity.remarks = ''

        if activity.status in ['HOD_APPROVED', 'DEAN_APPROVED', 'IQAC_APPROVED']:
            # Check if superior manually specified points via POST form
            pts_override = request.POST.get('awarded_points', '').strip()
            if pts_override:
                try:
                    activity.awarded_points = float(pts_override)
                except ValueError:
                    pass
            else:
                # Auto-calculate from RPP matrix for Research activities
                if activity.awarded_points is None and activity.category == 'Research':
                    calculated = activity.calculate_rpp_points()
                    activity.awarded_points = calculated

    elif action == 'reject':
        activity.status = 'REJECTED'
        activity.remarks = request.POST.get('remarks') or request.GET.get('remarks') or ('Rejected by ' + user.role)

    activity.save()
    verb = 'approved' if action == 'approve' else 'rejected'
    if action == 'approve' and active_role in ['HOD', 'DEAN_RI', 'IQAC'] and activity.awarded_points is not None:
        pts_display = int(activity.awarded_points) if activity.awarded_points == int(activity.awarded_points) else round(activity.awarded_points, 1)
        messages.success(request, f'Activity {verb}. Points awarded: {pts_display} RPP.')
    else:
        messages.success(request, f'Activity successfully {verb}.')

    return redirect('dashboard')


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def export_activities(request):
    if request.user.role not in ['IQAC', 'HOD']:
        messages.error(request, "You do not have permission to export.")
        return redirect('dashboard')

    dept_filter = request.GET.get('dept', '')
    qs = Activity.objects.filter(status='IQAC_APPROVED')
    if dept_filter:
        qs = qs.filter(department=dept_filter)

    if not qs.exists():
        messages.error(request, "No approved data to export.")
        return redirect('dashboard')

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        sheets_in_data = qs.values_list('sheet_name', flat=True).distinct()
        for sheet in sheets_in_data:
            sheet_qs = qs.filter(sheet_name=sheet)
            data = []
            for item in sheet_qs:
                row = {
                    'S.No': '',
                    'Department': item.department,
                    'Academic Year': item.academic_year,
                    'Faculty': item.faculty.get_display_name(),
                    'Submitted On': item.created_at.strftime('%d-%m-%Y'),
                }
                row.update(item.data_json)
                data.append(row)

            df = pd.DataFrame(data)
            # Add S.No column
            df['S.No'] = range(1, len(df) + 1)
            safe_name = sheet[:31].replace('/', '-')
            df.to_excel(writer, sheet_name=safe_name, index=False)

        # Consolidation sheet (Detailed NAAC Metrics)
        df_consolidation = generate_consolidation_df(qs, academic_year=ACADEMIC_YEARS[0])
        df_consolidation.to_excel(writer, sheet_name='Consolidation', index=False)

    output.seek(0)
    filename = f"MCET_Activity_Report_{dept_filter or 'ALL'}.xlsx"
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ─────────────────────────────────────────────────────────────────────────────
# API
# ─────────────────────────────────────────────────────────────────────────────

def api_sheet_config(request):
    """Returns sheet config as JSON for the dynamic form JS."""
    return JsonResponse(SHEET_CONFIG)


# ─────────────────────────────────────────────────────────────────────────────
# TARGET SETTING VIEWS
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def set_department_target(request):
    role = request.session.get('active_role', request.user.role)
    if role not in ['IQAC', 'DEAN_RI']:
        messages.error(request, "Only IQAC or Dean (R&I) can set department targets.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        dept = request.POST.get('dept')
        year = request.POST.get('year')
        sheet = request.POST.get('sheet')
        count = request.POST.get('count')
        points = request.POST.get('points', 0)
        
        DepartmentTarget.objects.update_or_create(
            department=dept, academic_year=year, sheet_name=sheet,
            defaults={'target_count': int(count or 0), 'points': int(points or 0)}
        )
        messages.success(request, f"Target updated for {dept} - {sheet}")
    
    return redirect('dashboard')

@login_required
def set_faculty_target(request):
    role = request.session.get('active_role', request.user.role)
    if role not in ['HOD', 'DEAN_RI', 'IQAC']:
        messages.error(request, "You do not have permission to assign faculty targets.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        year = request.POST.get('year')
        sheet = request.POST.get('sheet')
        count = request.POST.get('count')
        points = request.POST.get('points', 0)
        
        faculty = get_object_or_404(User, id=faculty_id)
        FacultyTarget.objects.update_or_create(
            faculty=faculty, academic_year=year, sheet_name=sheet,
            defaults={'target_count': int(count or 0), 'points': int(points or 0)}
        )
        messages.success(request, f"Target assigned to {faculty.get_display_name()} for {sheet}")
    
    return redirect('dashboard')

@login_required
def import_targets(request):
    # Placeholder for bulk import if needed
    messages.info(request, "Bulk import feature is coming soon.")
    return redirect('dashboard')

# ─────────────────────────────────────────────────────────────────────────────
# USER MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def manage_users(request):
    user = request.user
    if user.role not in ['IQAC', 'HOD', 'SPOC', 'PC']:
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    error_msg = ''
    success_msg = ''

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_department' and user.role == 'IQAC':
            code = request.POST.get('code', '').strip().upper()
            name = request.POST.get('name', '').strip()
            if code and name:
                Department.objects.get_or_create(code=code, defaults={'name': name})
                success_msg = f"Department {code} added successfully."
        elif action == 'add_user':
            username = request.POST.get('username', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            role = request.POST.get('role', '')
            dept_code = request.POST.get('dept_code', '')
            cadre = request.POST.get('cadre', '')
            
            if user.role == 'HOD':
                role = 'FACULTY'
                dept_code = user.department
            elif user.role == 'IQAC':
                if role not in ['HOD', 'SPOC']:
                    error_msg = "IQAC can only create HOD and SPOC accounts."
            
            if not error_msg:
                if User.objects.filter(username=username).exists():
                    error_msg = f"User {username} already exists."
                else:
                    new_user = User.objects.create_user(
                        username=username,
                        password='password', # default GUI password
                        role=role,
                        department=dept_code,
                        full_name=full_name,
                        cadre=cadre
                    )
                    new_user.set_password('mcet@1234')
                    new_user.save()
                    success_msg = f"User {username} created. Password is 'mcet@1234'."
        
        elif action == 'update_cadre':
            username = request.POST.get('username', '')
            new_cadre = request.POST.get('cadre', '')
            if user.role == 'HOD' and username and new_cadre:
                try:
                    target_user = User.objects.get(username=username, department=user.department, role='FACULTY')
                    target_user.cadre = new_cadre
                    target_user.save()
                    success_msg = f"Cadre updated to {new_cadre} for {target_user.get_display_name()}"
                except User.DoesNotExist:
                    error_msg = "User not found or permission denied."
        
        elif action == 'delete_user':
            username = request.POST.get('username', '')
            if username:
                try:
                    target_user = User.objects.get(username=username)
                    # Safety check: HOD can only delete faculty from their department
                    if user.role == 'HOD':
                        if target_user.department == user.department and target_user.role == 'FACULTY':
                            target_user.delete()
                            success_msg = f"User {username} deleted successfully."
                        else:
                            error_msg = "Permission denied. You can only delete faculties in your department."
                    # IQAC can delete HOD/SPOC
                    elif user.role == 'IQAC':
                        if target_user.role in ['HOD', 'SPOC']:
                            target_user.delete()
                            success_msg = f"User {username} deleted successfully."
                        else:
                            error_msg = "IQAC can only delete HOD and SPOC accounts from this interface."
                except User.DoesNotExist:
                    error_msg = "User not found."
        
        if success_msg:
            messages.success(request, success_msg)
        if error_msg:
            messages.error(request, error_msg)
        return redirect('manage_users')
        
    users_list = []
    dept_filter = request.GET.get('dept', '')
    
    if user.role == 'IQAC':
        # Exclude administrative utility accounts to prevent double-counting
        users_list = User.objects.exclude(username__in=['iqac_admin']).order_by('department')
        if dept_filter:
            users_list = users_list.filter(department=dept_filter)
    elif user.role in ['HOD', 'SPOC', 'PC']:
        users_list = User.objects.filter(department=user.department)

    # Convert to list for custom sorting
    users_list = list(users_list)
    
    CADRE_ORDER = {
        'Professor': 1,
        'Associate Professor': 2,
        'Assistant professor(SG)': 3,
        'Assistant Professor (SS)': 4,
        'Assistant Professor': 5,
    }
    
    # Custom sort: Department -> Cadre Priority -> Username
    users_list.sort(key=lambda u: (u.department, CADRE_ORDER.get(u.cadre, 99), u.username))
    
    depts = Department.objects.all().order_by('code')
    
    return render(request, 'manage_users.html', {
        'users_list': users_list,
        'depts': depts,
        'dept_filter': dept_filter,
    })

@login_required
def reset_password(request, username):
    user = request.user
    if user.role not in ['HOD', 'SPOC', 'PC']:
        return JsonResponse({'status': 'error', 'message': 'Access denied.'}, status=403)
    
    target_user = get_object_or_404(User, username=username, department=user.department)
    target_user.set_password('mcet@1234')
    target_user.save()
    return JsonResponse({'status': 'success', 'message': f'Password reset to mcet@1234 for {target_user.get_display_name()}.'})

@login_required
def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if not new_password:
            messages.error(request, "Password cannot be empty.")
            return redirect('dashboard')
        
        request.user.set_password(new_password)
        request.user.save()
        # Re-login the user to keep session alive
        login(request, request.user)
        messages.success(request, "Password changed successfully!")
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def get_faculty_profile(request, username):
    user = request.user
    if user.role not in ['HOD', 'IQAC']:
        return JsonResponse({'status': 'error', 'message': 'Access denied.'}, status=403)
    
    target_user = get_object_or_404(User, username=username)
    if user.role == 'HOD' and target_user.department != user.department:
        return JsonResponse({'status': 'error', 'message': 'Access denied.'}, status=403)
        
    data = {
        'full_name': target_user.get_display_name(),
        'username': target_user.username,
        'department': target_user.department,
        'cadre': target_user.cadre,
        'points': target_user.get_total_points(),
        'profile_pic': target_user.profile_picture.url if target_user.profile_picture else '/static/img/default-avatar.png'
    }
    return JsonResponse(data)

# ─────────────────────────────────────────────────────────────────────────────
# PROFILE PICTURE
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def upload_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_pic'):
        user = request.user
        user.profile_picture = request.FILES['profile_pic']
        user.save()
        messages.success(request, 'Profile picture updated successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

# ─────────────────────────────────────────────────────────────────────────────
# SELF APPRAISAL REPORT
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def self_appraisal_report(request):
    user = request.user
    active_role = request.session.get('active_role', user.role)
    if active_role != 'FACULTY':
        messages.error(request, 'Only faculty view can generate self-appraisal reports.')
        return redirect('dashboard')

    academic_year = request.GET.get('year', '2025-2026')
    activities = Activity.objects.filter(faculty=user, status='IQAC_APPROVED', academic_year=academic_year).order_by('created_at')
    
    # 2. Research and Development Mapping
    sections = {
        's21': {'title': 'Journal Publications', 'sheets': ['Journal Publications'], 'items': []},
        's22': {'title': 'Research Publications', 'sheets': ['Book Publication', 'Conference'], 'items': []},
        's23': {'title': 'IPR', 'sheets': ['Patent'], 'items': []},
        's24': {'title': 'Research Projects', 'sheets': ['Research Project'], 'items': []},
        's25': {'title': 'Consultancy', 'sheets': ['Consultancy (Project)', 'Consultancy (Training)'], 'items': []},
        's26': {'title': 'PhD', 'sheets': ['PhD Completion'], 'items': []},
        's31': {'title': 'FDP/STTP Attend', 'sheets': ['FDP-STTP', 'Seminar-Workshop'], 'items': []},
        's32': {'title': 'Events Organized', 'sheets': ['Event Organised', 'Conference Organization'], 'items': []},
        's33': {'title': 'Online Courses', 'sheets': ['Online Course (Faculty)', 'Skill Development & VAC'], 'items': []},
        's34': {'title': 'Resource Person', 'sheets': ['Resource Person'], 'items': []},
    }

    section_scores = {k: 0 for k in sections.keys()}

    for act in activities:
        # Pre-process act for template display (map labels to common keys)
        d = act.data_json
        act.display_authors = d.get('Name of Faculty') or d.get('Name of Faculty who attended') or d.get('Name of the Author and Position') or d.get('Co-Authors and Position') or d.get('Author Name') or d.get('Name of the Student') or d.get('pi_name') or '-'
        act.display_title = d.get('Title of the Paper') or d.get('Title of the Book') or d.get('Innovation Title') or d.get('Innovation Title') or d.get('Title of the Programme') or d.get('Course Name') or d.get('Innovation Title') or act.title
        act.display_venue = d.get('Name of the Journal') or d.get('Journal Name') or d.get('Organised By / Venue') or d.get('Organised By') or d.get('Venue') or d.get('Sponsoring Agency') or d.get('Funding Agency') or d.get('Name of Institution') or d.get('Agency Name') or '-'
        act.display_indexing = d.get('Indexed By') or d.get('Indexing') or '-'
        act.display_month_year = d.get('Month-Year of Publication (MM-YYYY)') or d.get('Date of Application (DD-MM-YYYY)') or d.get('Duration From (DD-MM-YYYY)') or d.get('Date') or d.get('Submission Date') or '-'
        act.display_others = d.get('Volume and Issue') or d.get('IPR Number') or d.get('Application Number') or d.get('ISBN') or d.get('DOI') or '-'

        for s_key, s_data in sections.items():
            if act.sheet_name in s_data['sheets']:
                s_data['items'].append(act)
                if act.awarded_points:
                    section_scores[s_key] += float(act.awarded_points)
                break

    # Summary Calculations
    total_r_and_d = sum(v for k, v in section_scores.items() if k.startswith('s2'))
    reduced_r_and_d = round(total_r_and_d * 0.3, 2)
    
    total_prof_dev = sum(v for k, v in section_scores.items() if k.startswith('s3'))

    context = {
        'sections': sections,
        'section_scores': section_scores,
        'total_r_and_d': total_r_and_d,
        'reduced_r_and_d': reduced_r_and_d,
        'total_prof_dev': total_prof_dev,
        'academic_year': academic_year,
        'academic_years': ACADEMIC_YEARS,
    }
    response = render(request, 'dashboards/self_appraisal.html', context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


@login_required
def faculty_profile(request, username):
    user = request.user
    active_role = request.session.get('active_role', user.role)
    
    if active_role not in ['HOD', 'IQAC', 'SPOC']:
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    target_user = get_object_or_404(User, username=username)
    
    # HOD/SPOC can only view their department
    if active_role in ['HOD', 'SPOC'] and target_user.department != user.department:
        messages.error(request, "You can only view profiles from your department.")
        return redirect('manage_users')
        
    activities = Activity.objects.filter(faculty=target_user).order_by('-created_at')
    
    # Points stats
    points_by_category = {
        'Research': 0,
        'Faculty_Development': 0,
        'Student_Activity': 0,
        'Industrial_Relationship': 0,
        'Association': 0,
    }
    
    for act in activities:
        if act.status == 'IQAC_APPROVED':
            pts = act.awarded_points or 0
            # Normalize sheet name/category for dict key
            cat_key = act.category.replace(' ', '_')
            points_by_category[cat_key] = points_by_category.get(cat_key, 0) + pts

    total_points = sum(points_by_category.values())

    return render(request, 'dashboards/faculty_profile.html', {
        'target_user': target_user,
        'activities': activities,
        'points_by_category': points_by_category,
        'total_points': total_points,
    })

@login_required
def update_department_name(request):
    if request.user.role != 'HOD':
        messages.error(request, "Only HODs can update department names.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        new_name = request.POST.get('name', '').strip()
        if new_name:
            dept = Department.objects.filter(code=request.user.department).first()
            if dept:
                old_name = dept.name
                dept.name = new_name
                dept.save()
                messages.success(request, f"Department name updated from '{old_name}' to '{new_name}'.")
            else:
                messages.error(request, "Department record not found.")
        else:
            messages.error(request, "Department name cannot be empty.")
    
    return redirect('dashboard')
@login_required
def mrpc_report(request, username=None):
    user = request.user
    role = request.session.get('active_role', user.role)
    
    if username and role in ['HOD', 'SPOC', 'PC', 'IQAC', 'DEAN_RI']:
        target_user = get_object_or_404(User, username=username)
    else:
        target_user = user

    # Allow HOD/IQAC to view any faculty; faculty can only view themselves
    if role == 'FACULTY' and target_user != user:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    academic_year = request.GET.get('year', '2025-2026')
    all_res = Activity.objects.filter(faculty=target_user, category='Research', academic_year=academic_year)

    def normalize(act):
        d = act.data_json
        # Common fields across sheets
        act.m_author = d.get('Name of the Author and Position') or d.get('Name of Faculty') or d.get('Name of Faculty who attended') or d.get('Authors') or d.get('faculty_name') or d.get('author_name') or d.get('authors')
        act.m_title = d.get('Title of the Paper') or d.get('Title of the Book') or d.get('Title of Paper Presented') or d.get('Title of Innovation') or d.get('paper_title') or d.get('book_title') or d.get('Title of Paper') or d.get('Project Title') or d.get('Tentative Title') or d.get('innovation_title')
        act.m_venue = d.get('Name of the Journal') or d.get('Title of Conference Proceedings') or d.get('Journal/Conf Name') or d.get('journal_name') or d.get('conference_title')
        act.m_indexing = d.get('Indexed By') or d.get('Indexing') or d.get('Target Indexing') or d.get('indexing')
        act.m_date = d.get('Month & Year of Publish/Grant (MM-YYYY)') or d.get('Month-Year of Publication (MM-YYYY)') or d.get('Year and Month of Publication') or d.get('Week/Month of Submission') or d.get('Tentative Date') or d.get('Submission Date') or d.get('Expected Date') or d.get('publish_grant_date')
        act.m_status = d.get('Status') or d.get('Status*') or d.get('Current Status') or d.get('status')
        act.m_id = d.get('Application Number') or d.get('Submission ID') or d.get('File No') or d.get('submission_id') or d.get('application_number')
        act.m_pct = d.get('Completion Percentage (%)') or d.get('completion_pct')
        act.m_amount = d.get('Amount (INR in Lakhs)') or d.get('Expected Revenue (INR in Lakhs)') or d.get('amount')
        act.m_investigators = d.get('Investigators') or d.get('Investigator(s)') or d.get('investigators')
        act.m_type = d.get('Type of Patent') or d.get('Type') or d.get('type') or d.get('patent_type')
        act.m_publisher = d.get('Name of the Publisher') or d.get('publisher_name')
        act.m_vol = d.get('Volume and Issue') or d.get('volume_issue')
        act.m_pages = d.get('Page No') or d.get('Page No in Proceedings') or d.get('page_no')
        act.m_doi = d.get('DOI of the Paper') or d.get('DOI') or d.get('doi')
        
        # PRO 600 specific
        act.m_batch = d.get('Batch') or d.get('batch')
        act.m_students = d.get('Name and Roll No. of Students') or d.get('student_details')
        act.m_outcome = d.get('Committed outcome (Conference / Patent / Journal)') or d.get('committed_outcome')
        
        # IPR specific
        act.m_applicant = d.get('Applicant') or d.get('applicant')
        act.m_inventors = d.get('Inventors') or d.get('inventors') or act.m_author
        return act

    # Approved statuses for research activities (research goes to DEAN_APPROVED, not IQAC_APPROVED)
    APPROVED_STATUSES = ['IQAC_APPROVED', 'DEAN_APPROVED']

    # 1.1 Published (Indexed Journals/Books/Conference)
    pub_sheets = ['Journal Publications', 'Book Publication', 'Conference']
    published = []
    for act in all_res.filter(sheet_name__in=pub_sheets, status__in=APPROVED_STATUSES):
        act = normalize(act)
        idx = str(act.m_indexing or '').upper()
        if any(x in idx for x in ['Q1', 'SCIE', 'SCOPUS', 'AHCI']):
            published.append(act)

    # 1.2 Submitted
    submitted = [normalize(a) for a in all_res.filter(sheet_name='Research-Submitted')]
    # 1.3 Under Preparation
    preparation = [normalize(a) for a in all_res.filter(sheet_name='Research-Preparation')]
    
    # 2. IPR
    ipr_pub = [normalize(a) for a in all_res.filter(sheet_name='Patent', status__in=APPROVED_STATUSES)]
    ipr_prep = [normalize(a) for a in all_res.filter(sheet_name='IPR-Preparation')]
    
    # 3. Funding & Consultancy
    funding_sub = [normalize(a) for a in all_res.filter(sheet_name='Research-Funding-Submitted')]
    funding_sanc = [normalize(a) for a in all_res.filter(sheet_name='Research Project', status__in=APPROVED_STATUSES)]
    consultancy_sanc = [normalize(a) for a in all_res.filter(sheet_name__startswith='Consultancy', status__in=APPROVED_STATUSES)]
    consultancy_plan = [normalize(a) for a in all_res.filter(sheet_name='Consultancy-Planning')]

    # 4. PRO 600 (Student Project Tracking)
    pro_list = [normalize(a) for a in all_res.filter(sheet_name='PRO 600')]
    student_batches = {
        'Batch 1': [a for a in pro_list if a.m_batch == 'Batch 1'],
        'Batch 2': [a for a in pro_list if a.m_batch == 'Batch 2'],
        'Batch 3': [a for a in pro_list if a.m_batch == 'Batch 3'],
    }

    # Summary Counts
    summary = {
        'published': len(published),
        'submitted': len(submitted),
        'preparation': len(preparation),
        'ipr': len(ipr_pub) + len(ipr_prep),
        'funding': len(funding_sub) + len(funding_sanc),
        'consultancy': len(consultancy_sanc) + len(consultancy_plan),
    }

    return render(request, 'mrpc_report.html', {
        'target_user': target_user,
        'summary': summary,
        'published': published,
        'submitted': submitted,
        'preparation': preparation,
        'ipr_pub': ipr_pub,
        'ipr_prep': ipr_prep,
        'funding_sub': funding_sub,
        'funding_sanc': funding_sanc,
        'consultancy_sanc': consultancy_sanc,
        'consultancy_plan': consultancy_plan,
        'student_batches': student_batches,
        'active_role': role,
        'academic_year': academic_year,
        'academic_years': ACADEMIC_YEARS,
    })
@login_required
def switch_role(request, role):
    user = request.user
    # Allow switching to FACULTY view (always allowed) or back to user's own primary role
    allowed_roles = [user.role, 'FACULTY']
    if role in allowed_roles:
        request.session['active_role'] = role
        messages.success(request, f"Switched to {role} view.")
    else:
        messages.error(request, f"You cannot switch to the {role} role.")
    return redirect('dashboard')
@login_required
def dean_assign_research(request):
    user = request.user
    role = request.session.get('active_role', user.role)
    if role != 'DEAN_RI':
        return redirect('dashboard')
    
    research_sheets = [k for k,v in SHEET_CONFIG.items() if v['category'] == 'Research']
    
    if request.method == 'POST':
        dept_code = request.POST.get('dept_code')
        year = request.POST.get('year', '2025-2026')
        sheet = request.POST.get('sheet')
        count = request.POST.get('count')
        
        DepartmentTarget.objects.update_or_create(
            department=dept_code, academic_year=year, sheet_name=sheet,
            defaults={'target_count': int(count or 0)}
        )
        messages.success(request, f"Research target assigned to {dept_code} department.")
        return redirect('dean_assign_research')

    return render(request, 'dashboards/dean_assign_research.html', {
        'departments': get_departments(),
        'research_sheets': research_sheets,
    })

@login_required
def dean_mrpc_report(request):
    user = request.user
    role = request.session.get('active_role', user.role)
    if role not in ['DEAN_RI', 'IQAC']:
        messages.error(request, 'Access denied. Only Dean (R&I) and IQAC can view this report.')
        return redirect('dashboard')

    academic_year = request.GET.get('year', '2025-2026')
    all_research = Activity.objects.filter(
        category='Research', 
        academic_year=academic_year, 
        status__in=['IQAC_APPROVED', 'DEAN_APPROVED', 'HOD_APPROVED', 'SPOC_APPROVED', 'PENDING']
    ).select_related('faculty')
    
    # 1. Aggregate directly using a loop
    depts = get_departments()
    dept_data_map = {}
    
    for code, name in depts:
        dept_data_map[code] = {
            'code': code, 'name': name, 'fac': User.objects.filter(department=code).count(), 'pts': 0,
            'fund': 0, 'amt': 0.0, 'jour': 0, 'bc': 0, 'pat': 0, 'des': 0, 'total': 0,
            'q1':0, 'scie':0, 'scopus':0, 'bc_pts':0, 'conf':0,
            'pat_f':0, 'pat_g':0, 'des_f':0, 'des_r':0, 'cp_f':0, 'cp_r':0,
            'p_pts':0, 'ipr_pts':0, 'f_pts':0, 'c_pts':0,
            'prof_e':0, 'asp_e':0, 'apsg_e':0, 'apss_e':0, 'ap_e':0
        }
    
    # Populate DEPT_DATA
    for act in all_research:
        u = act.faculty
        cadre = u.cadre or 'Assistant Professor'
        d = act.data_json
        indexing = (d.get('Indexed By') or d.get('Indexing') or '').upper()
        sheet = act.sheet_name
        dept = act.department
        if dept not in dept_data_map: continue
        
        row = dept_data_map[dept]
        points = act.awarded_points or act.calculate_rpp_points() or 0
        row['pts'] += points
        
        # Cadre aggregation
        if cadre == 'Professor': row['prof_e'] += points
        elif cadre == 'Associate Professor': row['asp_e'] += points
        elif cadre == 'Assistant professor(SG)': row['apsg_e'] += points
        elif cadre == 'Assistant Professor (SS)': row['apss_e'] += points
        elif cadre == 'Assistant Professor': row['ap_e'] += points

        if 'Journal' in sheet:
            row['jour'] += 1
            if 'Q1' in indexing: row['q1'] += 1; row['p_pts'] += points
            elif 'SCIE' in indexing: row['scie'] += 1; row['p_pts'] += points
            elif 'SCOPUS' in indexing: row['scopus'] += 1; row['p_pts'] += points
        elif 'Book' in sheet:
            row['bc'] += 1; row['p_pts'] += points
        elif 'Conference' in sheet:
            row['conf'] += 1; row['p_pts'] += points
        elif 'Patent' in sheet or 'IPR' in sheet:
            status = (d.get('status') or d.get('Status') or d.get('Current Status') or d.get('Published / Granted') or '').upper()
            ipr_type = (d.get('Type of Patent') or d.get('Type') or d.get('type') or d.get('patent_type') or '').upper()
            row['pat'] += 1
            row['ipr_pts'] += points
            
            if 'DESIGN' in ipr_type:
                if 'GRANT' in status or 'REG' in status: row['des_r'] += 1
                else: row['des_f'] += 1
            elif 'COPYRIGHT' in ipr_type:
                if 'GRANT' in status or 'REG' in status: row['cp_r'] += 1
                else: row['cp_f'] += 1
            else:
                if 'GRANT' in status or 'REGISTERED' in status: row['pat_g'] += 1
                else: row['pat_f'] += 1
        elif 'Project' in sheet or 'Funding' in sheet:
            row['fund'] += 1
            row['f_pts'] += points
            amt_str = d.get('Amount (INR in Lakhs)') or d.get('Expected Revenue (INR in Lakhs)') or '0'
            try: row['amt'] += float(amt_str)
            except: pass
        elif 'Consultancy' in sheet:
            row['c_pts'] += points

        row['total'] = row['jour'] + row['bc'] + row['pat'] + row['fund']

    # Normalize cadre pts by faculty count per cadre per dept
    for code, row in dept_data_map.items():
        dept_facs = User.objects.filter(department=code)
        row['prof_e'] = round(row['prof_e'] / dept_facs.filter(cadre='Professor').count(), 1) if dept_facs.filter(cadre='Professor').exists() else 0
        row['asp_e'] = round(row['asp_e'] / dept_facs.filter(cadre='Associate Professor').count(), 1) if dept_facs.filter(cadre='Associate Professor').exists() else 0
        row['apsg_e'] = round(row['apsg_e'] / dept_facs.filter(cadre='Assistant professor(SG)').count(), 1) if dept_facs.filter(cadre='Assistant professor(SG)').exists() else 0
        row['apss_e'] = round(row['apss_e'] / dept_facs.filter(cadre='Assistant Professor (SS)').count(), 1) if dept_facs.filter(cadre='Assistant Professor (SS)').exists() else 0
        row['ap_e'] = round(row['ap_e'] / dept_facs.filter(cadre='Assistant Professor').count(), 1) if dept_facs.filter(cadre='Assistant Professor').exists() else 0

    dept_list = list(dept_data_map.values())
    # Sort for ranking
    dept_list.sort(key=lambda x: x['pts'], reverse=True)
    for i, row in enumerate(dept_list):
        row['rank'] = i + 1
        # Prevent division by zero for points/fac
        if row['fac'] > 0:
            row['pts_per_fac'] = round(row['pts'] / row['fac'], 1)
        else:
            row['pts_per_fac'] = 0

    # Build a dept code->name map for lookups
    dept_name_map = dict(depts)
    
    full_faculty_list = []
    targets = {'Professor':100,'Associate Professor':88,'Assistant professor(SG)':75,'Assistant Professor (SS)':63,'Assistant Professor':50}
    for u in User.objects.all():
        acts = Activity.objects.filter(faculty=u, academic_year=academic_year, status__in=['IQAC_APPROVED', 'DEAN_APPROVED'])
        pp=0; ip=0; fp=0; cp=0
        for a in acts:
            pts = (a.awarded_points or a.calculate_rpp_points() or 0)
            if 'Journal' in a.sheet_name or 'Book' in a.sheet_name or 'Conference' in a.sheet_name: pp+=pts
            elif 'Patent' in a.sheet_name or 'IPR' in a.sheet_name: ip+=pts
            elif 'Project' in a.sheet_name or 'Funding' in a.sheet_name: fp+=pts
            elif 'Consultancy' in a.sheet_name: cp+=pts
        tot = pp+ip+fp+cp
        cadre = u.cadre or 'Assistant Professor'
        targ = targets.get(cadre, 50)
        dept_code = u.department or ''
        dept_full_name = dept_name_map.get(dept_code, dept_code)
        full_faculty_list.append({
            'name': u.get_display_name(),
            'dept': dept_full_name,
            'dept_code': dept_code,
            'cadre': cadre,
            'p_pts': pp, 'ipr_pts': ip, 'f_pts': fp, 'c_pts': cp,
            'total': tot, 'target': targ, 'gap': max(0, targ - tot)
        })
    full_faculty_list.sort(key=lambda x: x['total'], reverse=True)
    leaders = full_faculty_list[:10]

    # 3. TOPPERS
    toppers = []
    for code, name in depts:
        d_best = [f for f in full_faculty_list if f['dept_code'] == code and f['total'] > 0]
        if d_best:
            best = max(d_best, key=lambda x: x['total'])
            toppers.append({
                'dept': name,
                'dept_code': code,
                'name': best['name'],
                'p_pts': best['p_pts'],
                'ipr_pts': best['ipr_pts'],
                'f_pts': best['f_pts'],
                'c_pts': best['c_pts'],
                'total': int(best['total'])
            })

    # 4. Cadre Data
    cadre_stats_list = []
    for c, t in targets.items():
        c_f = [f for f in full_faculty_list if f['cadre'] == c]
        avg = round(sum(f['total'] for f in c_f)/len(c_f), 1) if c_f else 0
        cadre_stats_list.append({'label':c, 'val':avg, 'count':len(c_f), 'target':t})

    return render(request, 'dean_mrpc_report.html', {
        'dept_data': dept_list,
        'leaders': leaders,
        'toppers': toppers,
        'cadre_stats': cadre_stats_list,
        'faculty_data': full_faculty_list,
        'total_inst_points': sum(d['pts'] for d in dept_list),
        'academic_year': academic_year,
        'academic_years': ACADEMIC_YEARS,
        'summary': {
            'pub': sum(d['jour'] + d['bc'] for d in dept_list),
            'q1': sum(d['q1'] for d in dept_list),
            'scie': sum(d['scie'] for d in dept_list),
            'scopus': sum(d['scopus'] for d in dept_list),
            'bc': sum(d['bc'] for d in dept_list),
            'conf': sum(d['conf'] for d in dept_list),
            'ipr': sum(d['pat'] for d in dept_list),
            'pat_f': sum(d['pat_f'] for d in dept_list),
            'pat_g': sum(d['pat_g'] for d in dept_list),
            'des': sum(d['des_f'] + d['des_r'] for d in dept_list),
            'cp': sum(d['cp_f'] + d['cp_r'] for d in dept_list),
            'funding': sum(d['fund'] for d in dept_list),
            'amount': round(sum(d['amt'] for d in dept_list), 2),
        }
    })

@login_required
def get_target_status(request):
    """API for real-time target updates without page refresh."""
    active_role = request.session.get('active_role', request.user.role)
    progress = _get_target_progress(request.user, active_role)
    return JsonResponse({
        'target_progress': progress,
        'active_res': any(t['category'] == 'Research' and t['gap'] > 0 for t in progress),
        'active_iqac': any(t['category'] != 'Research' and t['gap'] > 0 for t in progress),
        'any_completed': any(t['gap'] == 0 for t in progress),
    })


@login_required
def get_target_html(request):
    """API returning HTML fragment for targets."""
    active_role = request.session.get('active_role', request.user.role)
    progress = _get_target_progress(request.user, active_role)
    context = {
        'target_progress': progress,
        'active_res': any(t['category'] == 'Research' and t['gap'] > 0 for t in progress),
        'active_iqac': any(t['category'] != 'Research' and t['gap'] > 0 for t in progress),
        'any_completed': any(t['gap'] == 0 for t in progress),
        'active_role': active_role,
    }
    template = 'dashboards/target_fragment.html'
    return render(request, template, context)
