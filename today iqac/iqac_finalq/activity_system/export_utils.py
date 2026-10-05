import pandas as pd
from datetime import datetime

def determine_quarter(date_obj):
    if not date_obj: return 'Q1'
    m = date_obj.month
    if 6 <= m <= 8: return 'Q1'
    if 9 <= m <= 11: return 'Q2'
    if m == 12 or m <= 2: return 'Q3'
    if 3 <= m <= 5: return 'Q4'
    return 'Q1'

def generate_consolidation_df(activities_qs, academic_year=None):
    # Base layout as requested by USER
    data = [
        # Criteria 1
        "Faculty Achievements (FDP/ Industrial training / Refresher/ Oriented Course - 5 days & above)",
        "NPTEL Achievements (By faculty)",
        "Workshops / Seminars (By faculty)",
        "Conferences Participation (By faculty)",
        "Awards/ Recognition (Regional/National/International level) by faculty",
        "Resource Person / Chairperson / Jury (Other institutions)",
        "Event Organised (FDP)",
        "Event Organised (WS)",
        "Event Organised (IKS)",
        "Event Organised (Industrial Training)",
        "Event Organised (Conference)",
        "Event Organised (Guest Lecture)",
        "Event Organised (Symposium)",
        "Event Organised (MoU signed)",
        "Clubs / Extra curricular Organized",
        "Total Count of Newsletters/Magazine/Blogs (published/coordinated by faculty)",
        "Collaborations / Professional body activities",
        "Extension (Social Activities) - by department",
        "Alumni events Organized",
        
        # Criteria 2
        "Student Co-Curricular Category (Participation)",
        "Student Co-Curricular Category (Awards/Achievements)",
        "Student Extra-Curricular Category (Participation)",
        "Student Extra-Curricular Category (Awards/Achievements)",
        "Student Industry Project / Internships",
        "Competitive Exams Qualifiers (GATE)",
        "Competitive Exams Qualifiers (GRE/TOEFL/GMAT)",
        "Student Publications (Scopus indexed Journals/Conferences only)",
        "Industrial Visits coordinated",
        "Value Added Courses (Organized / Student participation)",
        "Placement Achievements",
        "Higher Studies Achievements",
        "Students' Online Course Completion (other than NPTEL/Internal)",
        
        # Criteria 3
        "Research Journal Publication (indexed in Q1 only)",
        "Research Journal Publication (indexed in Scopus/SCI/WOS excluding Q1)",
        "Conference Publication (indexed in Scopus / WOS)",
        "Papers presented in Conferences (unindexed)",
        "Book / Book chapters published",
        "Seed money provided",
        "Patent (Published/Filed)",
        "Patent (Granted)",
        "Copyrights",
        "Grants Received (Ongoing/Applied/Completed)",
        "Consultancy amount generated",
    ]

    # Map Activity data to rows
    rows = []
    for d in data:
        rows.append({
            "Criteria": d,
            "Key Metric Parameters": d,
            "Target": 0,
            "Description": f"Consolidated metrics for {d}",
            "Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0,
            "Total Program Count": 0,
            "Total Faculty Count": 0,
            "Planned": 0,
            "Achieved (As per Target)": 0,
            "Gap": 0
        })

    df = pd.DataFrame(rows)
    
    # Simple mapping logic
    def get_row_index(title):
        for idx, row in df.iterrows():
            if title.lower() in row['Criteria'].lower():
                return idx
        return -1

    for act in activities_qs:
        sheet = act.sheet_name.lower()
        q = determine_quarter(act.created_at)
        
        target_idx = -1
        if "fdp" in sheet or "refresher" in sheet: target_idx = get_row_index("achievements (fdp")
        elif "workshop" in sheet or "seminar" in sheet: target_idx = get_row_index("workshops / seminars")
        elif "conference" in sheet: target_idx = get_row_index("conference")
        elif "nptel" in sheet: target_idx = get_row_index("nptel")
        elif "award" in sheet: target_idx = get_row_index("awards")
        elif "journal" in sheet:
            if "q1" in act.data_json.get('Index', '').lower(): target_idx = get_row_index("q1 only")
            else: target_idx = get_row_index("scopus/sci")
        elif "patent" in sheet:
            if "grant" in act.data_json.get('Status', '').lower(): target_idx = get_row_index("granted")
            else: target_idx = get_row_index("filed")
        elif "student" in sheet:
            if "award" in sheet or "achievement" in sheet: target_idx = get_row_index("awards/achievements")
            else: target_idx = get_row_index("participation")
        
        if target_idx != -1:
            df.at[target_idx, q] += 1
            df.at[target_idx, 'Total Program Count'] += 1
            # Faculty count would require user tracking per row, let's just increment for now
            df.at[target_idx, 'Total Faculty Count'] += 1
            df.at[target_idx, 'Achieved (As per Target)'] += 1

    return df
