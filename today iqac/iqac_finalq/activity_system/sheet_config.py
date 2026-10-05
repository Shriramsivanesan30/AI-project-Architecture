"""
SHEET_CONFIG: Central registry for all NAAC activity sheets.
Each entry maps sheet_name -> {category, label, fields}
Fields define the form inputs rendered dynamically in the UI.
"""

DEPARTMENTS = [
    ('IT', 'Information Technology'),
    ('CSE', 'Computer Science & Engineering'),
    ('AIML', 'AI & Machine Learning'),
    ('AIDS', 'AI & Data Science'),
    ('Auto', 'Automobile Engineering'),
    ('Mech', 'Mechanical Engineering'),
    ('EEE', 'Electrical & Electronics Engineering'),
    ('ECE', 'Electronics & Communication Engineering'),
    ('ACT', 'Advanced Communication Technology'),
    ('VLSI', 'VLSI Design'),
    ('Cyber', 'Cyber Security'),
    ('Civil', 'Civil Engineering'),
]

DEPT_CODES = [d[0] for d in DEPARTMENTS]

ACADEMIC_YEARS = [
    '2025-2026', '2026-2027', '2027-2028'
]

# ─────────────────────────────────────────────────────────────────────────────
# Helper field builders
# ─────────────────────────────────────────────────────────────────────────────
def text(name, label, required=True, hide_on_od=False):
    return {'name': name, 'label': label, 'type': 'text', 'required': required, 'hide_on_od': hide_on_od}

def date(name, label, required=True):
    return {'name': name, 'label': label, 'type': 'date', 'required': required}

def number(name, label, required=False):
    return {'name': name, 'label': label, 'type': 'number', 'required': required}

def select(name, label, options, required=True):
    return {'name': name, 'label': label, 'type': 'select', 'options': options, 'required': required}

def textarea(name, label, required=False):
    return {'name': name, 'label': label, 'type': 'textarea', 'required': required}

def url(name, label, required=False):
    return {'name': name, 'label': label, 'type': 'url', 'required': required}

# ─────────────────────────────────────────────────────────────────────────────
# SHEET CONFIG REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
SHEET_CONFIG = {

    # ═══════════════════════════════════════════
    # CATEGORY 1: FACULTY DEVELOPMENT
    # ═══════════════════════════════════════════

    'FDP-STTP': {
        'category': 'Faculty Development',
        'label': 'FDP / STTP',
        'fields': [
            text('faculty_name', 'Name of Faculty who attended'),
            text('programme_title', 'Title of the Programme'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            select('programme_type', 'Programme Type', ['FDP', 'STTP', 'PDP', 'EDP', 'MDP', 'Industrial Training']),
            text('organised_by', 'Organised By / Venue'),
            select('nirf_rank', 'NIRF Rank of Organising Institution', ['Top 100', 'Top 200', 'Top 500', 'Govt Institution', 'Other Institution', 'N/A']),
            select('financial_support', 'Financial Support by Institution', ['Yes', 'No']),
        ]
    },

    'MMTTTP-FDP': {
        'category': 'Faculty Development',
        'label': 'MMTTTP / FDP',
        'fields': [
            text('faculty_name', 'Name of Faculty who attended'),
            text('programme_title', 'Title of the Programme'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            select('programme_type', 'Programme Type', ['FDP', 'STTP', 'PDP', 'EDP', 'MDP', 'Refresher Course']),
            select('mode', 'Online / Offline', ['Online', 'Offline', 'Hybrid']),
            text('mmtttp_center', 'MMTTTP Center'),
            select('financial_support', 'Financial Support by Institution', ['Yes', 'No']),
        ]
    },

    'Seminar-Workshop': {
        'category': 'Faculty Development',
        'label': 'Seminar / Workshop',
        'fields': [
            text('faculty_name', 'Name of Faculty who attended'),
            text('programme_title', 'Title of the Programme'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            select('programme_type', 'Programme Type', ['Seminar', 'Workshop']),
            text('organised_by', 'Organised By / Venue'),
            select('nirf_rank', 'NIRF Rank of Organising Institution', ['Top 100', 'Top 200', 'Top 500', 'Govt Institution', 'Other Institution', 'N/A']),
            select('financial_support', 'Financial Support by Institution', ['Yes', 'No']),
        ]
    },

    'Professional Body Membership': {
        'category': 'Faculty Development',
        'label': 'Professional Body Membership',
        'fields': [
            text('faculty_name', 'Name of Faculty'),
            text('programme_title', 'Title of Program'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            text('professional_body', 'Name of Professional Body'),
            date('membership_fee_date', 'Date of Membership Fees Provided'),
            select('financial_support', 'Financial Support by Institution', ['Yes', 'No']),
            url('financial_support_link', 'Link for Financial Support Page'),
        ]
    },

    'Online Course': {
        'category': 'Faculty Development',
        'label': 'Online Course',
        'fields': [
            text('faculty_name', 'Name of Faculty who attended'),
            text('course_name', 'Course Name'),
            text('course_start', 'Month-Year of Course Started (MM-YYYY)'),
            number('duration_weeks', 'Duration in Weeks'),
            select('platform', 'Platform', ['NPTEL', 'Coursera', 'EdX', 'Udemy', 'Swayam', 'Other']),
            text('recognition', 'Recognition (Elite/Gold/Silver/% of Marks)', hide_on_od=True),
            select('approved_as_fdp', 'Approved as FDP (NPTEL only)', ['Yes', 'No', 'N/A']),
            select('acted_as_mentor', 'Acted as a Mentor', ['Yes', 'No']),
            select('financial_support', 'Financial Support by Institution', ['Yes', 'No']),
            url('financial_support_link', 'Link for Financial Support Page'),
        ]
    },

    'Faculty Internship': {
        'category': 'Faculty Development',
        'label': 'Faculty Internship',
        'fields': [
            text('faculty_name', 'Name of the Faculty'),
            select('designation', 'Designation', ['Professor', 'Associate Professor', 'Assistant Professor', 'Other']),
            text('internship_title', 'Title of Internship'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            text('mou_details', 'Details of MoU Collaboration (if any)', ),
            text('industry_details', 'Details of Industry Collaborated'),
            select('scheme', 'Scheme Name', ['AICTE Faculty Internship', 'ANRF', 'Self', 'Other']),
            number('stipend', 'Stipend Amount (if any, in Rs)'),
        ]
    },

    'Resource Person': {
        'category': 'Faculty Development',
        'label': 'Resource Person',
        'fields': [
            text('faculty_name', 'Name of Faculty'),
            text('programme_title', 'Title of the Programme'),
            text('topic_delivered', 'Topic Delivered'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            select('role', 'Role', ['Resource Person', 'Chair Person', 'Expert in Conference', 'Keynote Speaker', 'FDP Lecture', 'Seminar Lecture', 'Workshop Lecture']),
            text('venue', 'Venue / Invited Organization'),
            select('financial_support', 'Financial Support by Institution', ['Yes', 'No']),
            url('financial_support_link', 'Link for Financial Support Page'),
        ]
    },

    'Faculty Contribution in MOOC': {
        'category': 'Faculty Development',
        'label': 'Faculty Contribution in MOOC',
        'fields': [
            text('faculty_name', 'Name of Faculty'),
            text('course_code', 'Course Code'),
            text('course_name', 'Course Name'),
            text('video_topic', 'Video Content Topic'),
            text('video_duration', 'Duration of Video (HH:MM)'),
            select('platform', 'Content Developed For', ['SWAYAM-NPTEL', 'Coursera', 'EdX', 'YouTube', 'Other']),
            url('video_link', 'Link of the Video Content'),
            select('financial_support', 'Financial Support by Institution', ['Yes', 'No']),
        ]
    },

    'Awards and Recognition': {
        'category': 'Faculty Development',
        'label': 'Awards and Recognition',
        'fields': [
            text('faculty_name', 'Name of the Faculty'),
            text('award_name', 'Name of Award / Recognition / Fellowship'),
            select('level', 'International / National', ['International', 'National']),
            text('awarding_body', 'Name of Awarding Body / Agency'),
            date('award_date', 'Date of Award Received (DD-MM-YYYY)'),
            select('award_type', 'Awarding Type', ['Certificate', 'Trophy with Certification', 'Medal with Certification', 'Cash Award', 'Fellowship']),
            number('fellowship_amount', 'Fellowship Amount (if any, in Rs)'),
        ]
    },


    # ═══════════════════════════════════════════
    # CATEGORY 2: RESEARCH
    # ═══════════════════════════════════════════

    'Journal Publications': {
        'category': 'Research',
        'label': 'Journal Publications',
        'fields': [
            text('author_name', 'Name of the Author and Position'),
            text('author_department', 'Department of the Author'),
            text('coauthors', 'Co-Authors and Position'),
            text('coauthor_dept_institution', 'Department & Institution of Co-Author(s)'),
            select('corresponding_author', 'Corresponding Author', ['Yes', 'No']),
            text('paper_title', 'Title of the Paper'),
            text('journal_name', 'Name of the Journal'),
            text('volume_issue', 'Volume and Issue'),
            text('page_no', 'Page No'),
            text('publication_month_year', 'Month-Year of Publication (MM-YYYY)'),
            text('journal_issn', 'Journal ISSN'),
            number('impact_factor', 'Impact Factor'),
            select('indexing', 'Indexed By', ['Q1/AHCI', 'SCIE', 'Scopus', 'Google Scholar', 'UGC Care List', 'Not Indexed']),
            select('is_phd_case', 'Involves Ph.D. Scholar with MCET Guide?', ['Yes', 'No']),
            select('your_role', 'Your Role (if Ph.D. case)', ['Scholar', 'Guide', 'N/A']),
            number('mcet_contributors', 'Total Number of MCET Contributors (including you)'),
            url('doi', 'DOI of the Paper'),
        ]
    },

    'Book Publication': {
        'category': 'Research',
        'label': 'Book Publication',
        'fields': [
            text('faculty_name', 'Name of Faculty'),
            select('author_position', 'Position of Author', ['First Author', 'Second Author', 'Third Author', 'Fourth Author', 'Editor']),
            select('corresponding_author', 'Corresponding Author', ['Yes', 'No']),
            text('book_title', 'Title of the Book'),
            text('chapter_title', 'Title of the Book Chapter'),
            text('page_no', 'Page No'),
            text('isbn', 'ISBN of the Book'),
            select('print_ebook', 'Print / eBook', ['Print', 'eBook', 'Both']),
            select('indexing', 'Indexing', ['Scopus', 'Other Indexing', 'Not Indexed']),
            select('is_phd_case', 'Involves Ph.D. Scholar with MCET Guide?', ['Yes', 'No']),
            select('your_role', 'Your Role (if Ph.D. case)', ['Scholar', 'Guide', 'N/A']),
            number('mcet_contributors', 'Total Number of MCET Contributors (including you)'),
            url('doi', 'DOI'),
        ]
    },

    'Conference': {
        'category': 'Research',
        'label': 'Conference',
        'fields': [
            text('faculty_name', 'Name of Faculty who attended'),
            text('conference_title', 'Title of the Conference'),
            text('paper_title', 'Title of Paper Presented'),
            select('corresponding_author', 'Corresponding Author', ['Yes', 'No']),
            select('author_position', 'Position of Author', ['First Author', 'Second Author', 'Third Author', 'Fourth Author']),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            select('participation_type', 'Participation Type', ['Attended', 'Presented']),
            select('level', 'Level of Conference', ['National', 'International']),
            text('venue', 'Venue'),
            text('organised_by', 'Organised By'),
            text('proceedings_title', 'Title of Conference Proceedings'),
            text('page_no', 'Page No in Proceedings'),
            text('isbn', 'ISBN of Conference Proceeding'),
            text('publication_month_year', 'Year and Month of Publication'),
            text('affiliating_institute', 'Affiliating Institute at Time of Publication'),
            text('publisher_name', 'Name of the Publisher'),
            select('nirf_rank', 'NIRF Rank of Organising Institution', ['Top 100', 'Top 200', 'Top 500', 'Govt Institution', 'Other Institution', 'N/A']),
            select('financial_support', 'Financial Support by Institution', ['Yes', 'No']),
            url('financial_support_link', 'Link for Financial Support Page'),
            select('indexing', 'Indexing', ['Scopus', 'Other Indexing', 'Not Indexed']),
            select('is_phd_case', 'Involves Ph.D. Scholar with MCET Guide?', ['Yes', 'No']),
            select('your_role', 'Your Role (if Ph.D. case)', ['Scholar', 'Guide', 'N/A']),
            number('mcet_contributors', 'Total Number of MCET Contributors (including you)'),
        ]
    },

    'Patent': {
        'category': 'Research',
        'label': 'Patent',
        'fields': [
            text('faculty_name', 'Name of Faculty'),
            select('innovator_position', 'Position of Innovator', ['First Inventor', 'Second Inventor', 'Third Inventor', 'Fourth Inventor']),
            select('corresponding_author', 'Corresponding Author', ['Yes', 'No']),
            text('innovation_title', 'Innovation Title'),
            text('application_number', 'Application Number'),
            date('application_date', 'Date of Application (DD-MM-YYYY)'),
            select('status', 'Published / Granted', ['Published', 'Granted', 'Filed']),
            date('publish_grant_date', 'Date of Published/Granted (DD-MM-YYYY)'),
            select('patent_type', 'Type of Patent', ['Utility', 'Design', 'Copyright']),
            select('is_phd_case', 'Involves Ph.D. Scholar with MCET Guide?', ['Yes', 'No']),
            select('your_role', 'Your Role (if Ph.D. case)', ['Scholar', 'Guide', 'N/A']),
            select('patenting_body', 'Patenting Body', ['National', 'International']),
            select('financial_support', 'Financial Support by Institution', ['Yes', 'No']),
            url('financial_support_link', 'Link for Financial Support Page'),
            number('mcet_contributors', 'Total Number of MCET Contributors (including you)'),
        ]
    },

    'Research Project': {
        'category': 'Research',
        'label': 'Research Project (Sanctioned)',
        'fields': [
            text('pi_name', 'Name of Principal Investigator and Department'),
            text('co_pi_1', 'Name of Co-Principal Investigator 1 and Department'),
            text('co_pi_2', 'Name of Co-Principal Investigator 2 and Department (if any)'),
            text('funding_agency', 'Name of Funding Agency'),
            select('funding_type', 'Type', ['Government', 'Non-Government', 'Institution']),
            text('scheme_name', 'Name of the Scheme'),
            text('sanction_letter', 'Sanction Letter No and Date'),
            text('other_faculty', 'Other Faculty Details (outside MCET)'),
            text('supporting_staff', 'Supporting Staff Details'),
            date('submission_date', 'Date of Submission (DD-MM-YYYY)'),
            number('total_funds', 'Total Funds Provided (INR in Lakhs)'),
            number('amount_current_year', 'Amount Received in Current Financial Year'),
            number('amount_utilized', 'Amount Utilized'),
            date('utilization_cert_date', 'Date of Submission of Utilization Certificate'),
            number('seed_money', 'Seed Money by Institution (Internal R&D)'),
            date('grant_received_date', 'Date of Receiving the Grant (DD-MM-YYYY)'),
            text('project_duration', 'Duration of the Project'),
            url('policy_link', 'Link to Policy Document and Sanction Letter'),
            number('mcet_contributors', 'Total Number of MCET Contributors (including you)'),
        ]
    },




    'Consultancy (Project)': {
        'category': 'Research',
        'label': 'Consultancy (Project)',
        'fields': [
            text('faculty_consultants', 'Names of Faculty-Consultants'),
            text('project_name', 'Name of the Consultancy Project'),
            text('agency_name', 'Consulting/Sponsoring Agency with Contact Details'),
            textarea('project_details', 'Project Details'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            number('revenue', 'Revenue Generated (INR in Lakhs)'),
        ]
    },

    'Consultancy (Training)': {
        'category': 'Research',
        'label': 'Consultancy (Training)',
        'fields': [
            text('faculty_consultants', 'Names of Faculty-Consultants'),
            text('training_name', 'Name of the Training Program'),
            select('program_type', 'Type of Program', ['Corporate Training', 'Train the Trainer', 'FDP', 'MDP', 'EDP']),
            text('agency_name', 'Agency/Organization with Contact Details'),
            number('internal_participants', 'Number of Internal Participants'),
            number('external_participants', 'Number of External Participants'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            number('revenue', 'Revenue Generated (INR in Lakhs)'),
        ]
    },

    'Students In-house Seed Money': {
        'category': 'Research',
        'label': 'Students In-house Seed Money',
        'fields': [
            text('student_names', 'Name of the Students'),
            text('mentor_name', 'Name of the Mentor/Guide'),
            text('project_title', 'Title of the Project'),
            number('funds_provided', 'Funds Provided (INR in Lakhs)'),
            date('grant_received_date', 'Date of Receiving the Grant (DD-MM-YYYY)'),
            text('sanction_letter', 'Sanction Letter No and Date'),
            text('outside_collaboration', 'Details of Any Outside Collaboration'),
            text('project_duration', 'Duration of the Project'),
            select('outcome', 'Outcome', ['Patent', 'Publication', 'Both', 'Other']),
            url('policy_link', 'Link to Policy Document and Sanction Letter'),
        ]
    },


    'Technology Transfer': {
        'category': 'Research',
        'label': 'Technology Transfer',
        'fields': [
            text('item_name', 'Name of Technology / Item'),
            text('transferred_to', 'Transferred to (Organization/Agency)'),
            date('transfer_date', 'Date of Transfer'),
            number('mcet_contributors', 'Number of MCET Contributors'),
        ]
    },

    'Expert Certification': {
        'category': 'Research',
        'label': 'Expert Certification',
        'fields': [
            text('cert_name', 'Name of Certification (Expert/Auditor/Agent)'),
            text('awarding_body', 'Awarding Body / Govt Agency'),
            date('award_date', 'Date of Certification'),
            number('mcet_contributors', 'Number of MCET Contributors'),
        ]
    },

    'Skill Services': {
        'category': 'Research',
        'label': 'Skill Services',
        'fields': [
            text('service_name', 'Name of Service in Kind'),
            text('beneficiary', 'Organization / Beneficiary'),
            date('service_date', 'Date of Service Provided'),
            number('mcet_contributors', 'Number of MCET Contributors'),
        ]
    },

    'Conference Organization': {
        'category': 'Research',
        'label': 'Conference Organization',
        'fields': [
            text('conf_name', 'Name of Conference'),
            select('indexing', 'Indexing', ['Scopus', 'Other Indexing']),
            select('role', 'Your Role', ['Convener', 'Organising Secretary', 'Core Committee Member']),
            date('date_from', 'Date From'),
            date('date_to', 'Date To'),
            number('mcet_contributors', 'Number of MCET Contributors in Role'),
        ]
    },

    'PhD Completion': {
        'category': 'Research',
        'label': 'PhD Completion',
        'fields': [
            text('scholar_name', 'Name of Scholar'),
            select('scholar_type', 'Scholar Type', ['Full Time', 'Part Time Internal']),
            select('your_role', 'Your Role', ['Scholar', 'Supervisor']),
            date('completion_date', 'Date of Completion / Synopsis Submission'),
            number('mcet_contributors', 'Number of MCET Contributors (for Guide Sharing)'),
        ]
    },
    

    'Research-Submitted': {
        'category': 'Research',
        'label': 'Research Submission (Journal/Conference)',
        'fields': [
            select('type', 'Type', ['Journal', 'Conference']),
            text('authors', 'Authors'),
            text('paper_title', 'Title of Paper'),
            text('journal_name', 'Journal/Conf Name'),
            text('submission_id', 'Submission ID'),
            text('week_month', 'Week/Month of Submission'),
            select('status', 'Status', ['Submitted', 'Under Review', 'Revision Requested']),
            select('indexing', 'Indexing', ['Q1/AHCI', 'SCIE', 'Scopus', 'Google Scholar', 'UGC Care List', 'Other']),
        ]
    },

    'Research-Preparation': {
        'category': 'Research',
        'label': 'Research Under Preparation',
        'fields': [
            select('type', 'Type', ['Journal', 'Conference']),
            text('authors', 'Authors'),
            text('paper_title', 'Title of Paper'),
            text('journal_name', 'Journal/Conf Name'),
            text('week_month', 'Tentative Date'),
            text('status', 'Current Status'),
            number('completion_pct', 'Completion Percentage (%)'),
            select('indexing', 'Target Indexing', ['SCIE', 'Scopus', 'Other']),
        ]
    },

    'IPR-Preparation': {
        'category': 'Research',
        'label': 'IPR Under Preparation',
        'fields': [
            text('applicant', 'Applicant'),
            text('inventors', 'Inventors'),
            text('title', 'Tentative Title'),
            text('status', 'Current Status'),
            number('completion_pct', 'Completion Percentage (%)'),
            text('week_month', 'Tentative Date'),
        ]
    },

    'Research-Funding-Submitted': {
        'category': 'Research',
        'label': 'Research Funding (Submitted)',
        'fields': [
            text('agency', 'Agency'),
            text('scheme', 'Scheme'),
            text('file_no', 'File No'),
            text('title', 'Project Title'),
            text('investigators', 'Investigators'),
            number('amount', 'Amount (INR in Lakhs)'),
            date('submission_date', 'Submission Date'),
            text('status', 'Status'),
        ]
    },

    'Consultancy-Planning': {
        'category': 'Research',
        'label': 'Consultancy Planning',
        'fields': [
            text('client', 'Client'),
            text('project_name', 'Project Name'),
            text('investigators', 'Investigator(s)'),
            text('expected_date', 'Expected Date'),
            number('expected_revenue', 'Expected Revenue (INR in Lakhs)'),
        ]
    },

    # ═══════════════════════════════════════════
    # CATEGORY 3: STUDENT ACTIVITY
    # ═══════════════════════════════════════════

    'Online Course (Students)': {
        'category': 'Student Activity',
        'label': 'Online Course (Students)',
        'fields': [
            text('student_name', 'Name of Student'),
            text('roll_no', 'Roll No'),
            text('course_name', 'Course Name'),
            text('course_start', 'Month-Year of Course Started (MM-YYYY)'),
            number('duration_weeks', 'Duration in Weeks'),
            select('platform', 'Platform', ['NPTEL', 'Coursera', 'EdX', 'Udemy', 'Swayam', 'Other']),
            text('recognition', 'Recognition (Elite/Gold/Silver/% of Marks)', hide_on_od=True),
            text('course_mentor', 'Name of Course Mentor (if any)'),
            select('financial_support', 'Financial Support by Institution', ['Yes', 'No']),
            url('financial_support_link', 'Link for Financial Support Page'),
        ]
    },

    'Student Participation - Workshop': {
        'category': 'Student Activity',
        'label': 'Student Participation - Workshop',
        'fields': [
            text('student_name', 'Name of the Student'),
            text('roll_no', 'Roll No'),
            select('level', 'Level', ['Inter-university', 'State', 'National', 'International']),
            text('event_name', 'Name of the Event'),
            select('event_type', 'Type of Event', ['Seminar', 'Workshop']),
            select('internal_external', 'Internal / External', ['Internal', 'External']),
            text('participation_achievement', 'Participation / Achievement'),
            date('date', 'Date of Participation (DD-MM-YYYY)'),
            text('organising_institute', 'Name of Organising Institute / College'),
            text('club_cell', 'Name of Club/Cell (if applicable)'),
        ]
    },

    'Student Participation - Co-Curricular': {
        'category': 'Student Activity',
        'label': 'Student Participation - Co-Curricular',
        'fields': [
            text('student_name', 'Name of the Student'),
            text('roll_no', 'Roll No'),
            select('level', 'Level', ['Inter-university', 'State', 'National', 'International']),
            text('event_name', 'Name of the Event'),
            select('event_type', 'Type of Event', ['Hackathon', 'Training', 'Project Competition', 'Symposium', 'Other']),
            select('internal_external', 'Internal / External', ['Internal', 'External']),
            text('participation_achievement', 'Participation / Achievement'),
            date('date', 'Date of Participation (DD-MM-YYYY)'),
            text('organising_institute', 'Name of Organising Institute / College'),
            text('club_cell', 'Name of Club/Cell'),
            text('award_medal', 'Name of Award / Medal'),
            select('team_individual', 'Team / Individual', ['Team', 'Individual']),
        ]
    },

    'Student Participation - Extra-Curricular': {
        'category': 'Student Activity',
        'label': 'Student Participation - Extra-Curricular',
        'fields': [
            text('student_name', 'Name of the Student'),
            text('roll_no', 'Roll No'),
            select('level', 'Level', ['Inter-university', 'State', 'National', 'International']),
            text('event_name', 'Name of the Event'),
            select('event_type', 'Type of Event', ['Sports', 'Culturals', 'Other']),
            select('internal_external', 'Internal / External', ['Internal', 'External']),
            text('participation_achievement', 'Participation / Achievement'),
            date('date', 'Date of Participation (DD-MM-YYYY)'),
            text('organising_institute', 'Name of Organising Institute / College'),
            text('club_cell', 'Name of Club/Cell'),
            text('award_medal', 'Name of Award / Medal'),
            select('team_individual', 'Team / Individual', ['Team', 'Individual']),
        ]
    },

    'Student Conference Participation': {
        'category': 'Student Activity',
        'label': 'Student Conference Participation',
        'fields': [
            text('student_names', 'Name of Student(s)'),
            text('roll_no', 'Roll No'),
            text('guide_name', 'Name of the Guide'),
            select('publication_source', 'Publication through', ['Project', 'Internship', 'Training']),
            text('conference_title', 'Title of the Conference'),
            text('paper_title', 'Title of Paper Presented'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            select('participation_type', 'Participation Type', ['Attended', 'Presented']),
            select('level', 'Level of Conference', ['National', 'International']),
            text('venue', 'Venue'),
            text('organised_by', 'Organised By'),
            text('proceedings_title', 'Title of Conference Proceedings'),
            text('page_no', 'Page No in Proceedings'),
            text('isbn', 'ISBN of Conference Proceeding'),
            text('publication_month_year', 'Year and Month of Publication'),
            text('affiliating_institute', 'Affiliating Institute at Time of Publication'),
            text('publisher_name', 'Name of the Publisher'),
            select('project_outcome', 'Outcome of Project Work', ['Yes', 'No']),
            number('support_amount', 'Amount of Support (Rs)'),
        ]
    },

    'IKS Participation': {
        'category': 'Association',
        'label': 'IKS Participation',
        'fields': [
            text('roll_no', 'Roll No'),
            text('student_name', 'Name of the Student'),
            text('programme_title', 'Title of IKS Programme'),
            select('event_type', 'Type of Event', ['Workshop', 'Seminar', 'Guest Lecture', 'Certificate Program', 'Tour']),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            text('participation_achievement', 'Participation / Achievement'),
            select('level', 'Level', ['National', 'International']),
        ]
    },

    'Student Internship': {
        'category': 'Industrial Relationship',
        'label': 'Student Internship',
        'fields': [
            text('roll_no', 'Roll No'),
            text('student_name', 'Name of Student'),
            text('internship_title', 'Title of Internship'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            text('project_guide', 'Project Guide (Faculty Name)'),
            text('mou_details', 'Details of MoU Collaboration'),
            text('industry_details', 'Details of Industry Collaborated'),
            select('outcome', 'Outcome', ['Publication', 'Patent', 'Hackathon', 'Other Competition', 'None']),
            number('stipend', 'Stipend Amount (if any, in Rs)'),
            url('document_link', 'Link to Relevant Document'),
        ]
    },

    'Student Project': {
        'category': 'Student Activity',
        'label': 'Student Project',
        'fields': [
            text('roll_no', 'Roll No'),
            text('student_name', 'Name of Student'),
            text('project_title', 'Title of Project'),
            date('duration_from', 'Duration From (DD-MM-YYYY)'),
            date('duration_to', 'Duration To (DD-MM-YYYY)'),
            text('project_guide', 'Project Guide (Faculty Name)'),
            text('mou_details', 'Details of MoU Collaboration'),
            text('industry_details', 'Details of Industry Collaborated'),
            select('outcome', 'Outcome', ['Publication', 'Patent', 'Hackathon', 'Other Competition', 'None']),
            number('stipend', 'Stipend Amount (if any, in Rs)'),
            url('document_link', 'Link to Relevant Document'),
        ]
    },

    'Placement': {
        'category': 'Industrial Relationship',
        'label': 'Placement',
        'fields': [
            text('student_name', 'Name of Student'),
            text('company_name', 'Name of the Company'),
            text('company_contact', 'Company Contact Details'),
            text('program_graduated', 'Program Graduated From'),
            text('employer_name', 'Name of Employer with Contact Details'),
            number('pay_package', 'Pay Package at Appointment (INR per annum)'),
            date('offer_letter_date', 'Date of Receiving Offer Letter (DD-MM-YYYY)'),
        ]
    },

    'Higher Studies': {
        'category': 'Industrial Relationship',
        'label': 'Higher Studies',
        'fields': [
            text('student_name', 'Name of Student'),
            select('higher_ed_type', 'Higher Education Type', ['Higher Education', 'Entrepreneur', 'Self Employed', 'Research']),
            text('contact_details', 'Contact Details'),
            text('program_graduated', 'Program Graduated From'),
            text('institution_or_startup', 'Name of Institution/Start-up/Organization Joined'),
            text('program_admitted', 'Name of Program Admitted To'),
            date('joining_date', 'Date of Joining in Higher Education (DD-MM-YYYY)'),
        ]
    },

    'IV & Industrial Tour': {
        'category': 'Industrial Relationship',
        'label': 'IV & Industrial Tour',
        'fields': [
            text('class_details', 'Details of Class'),
            text('visit_place', 'Place of Industrial Visit/Tour'),
            number('total_students', 'Total Number of Students'),
            date('visit_date', 'Date of Visit (DD-MM-YYYY)'),
            select('mou_based', 'Visit Arranged Based on MoU', ['Yes', 'No']),
            text('industry_contact', 'Industry Contact Person Details'),
        ]
    },

    'Alumni': {
        'category': 'Association',
        'label': 'Alumni Interaction',
        'fields': [
            select('activity_type', 'Activity Type', ['Alumni Meeting', 'Alumni Interaction']),
            text('alumni_name', 'Name of the Alumni'),
            text('program_title', 'Title of Program'),
            number('num_participants', 'Number of Participants'),
            date('date_from', 'Date From (DD-MM-YYYY)'),
            date('date_to', 'Date To (DD-MM-YYYY)'),
            select('beneficiary_type', 'Type of Beneficiary', ['Placement', 'Higher Education', 'Project', 'Internship', 'Other']),
            number('students_benefited', 'Number of Students Benefited'),
            select('feedback_collected', 'Program Feedback Collected', ['Yes', 'No']),
        ]
    },

    'Tech Symposium': {
        'category': 'Association',
        'label': 'Tech Symposium',
        'fields': [
            text('association_club', 'Department Association / Club Name'),
            text('programme_title', 'Title of the Programme'),
            text('coordinator_name', 'Coordinator Name'),
            select('event_type', 'Event Type', ['Technical Symposium', 'Association Function']),
            number('internal_participants', 'Number of Internal Participants'),
            number('external_participants', 'Number of External Participants'),
            number('total_participants', 'Total Number of Participants'),
            select('level', 'Level', ['National', 'International']),
            date('date_from', 'Date From (DD-MM-YYYY)'),
            date('date_to', 'Date To (DD-MM-YYYY)'),
            text('guest_name', 'Guest Name'),
            select('in_association_iic', 'In Association with IIC', ['Yes', 'No']),
            select('feedback_collected', 'Program Feedback Collected', ['Yes', 'No']),
        ]
    },

    'Event Organised': {
        'category': 'Association',
        'label': 'Event Organised (for Students)',
        'fields': [
            text('dept_club_cell', 'Department / Club / Cell'),
            text('programme_title', 'Title of the Programme'),
            text('coordinator_name', 'Coordinator Name'),
            select('event_type', 'Event Type', ['Workshop', 'Seminar', 'Guest Lecture', 'Entrepreneurship', 'Skill Development', 'Other']),
            number('num_participants', 'Number of Participants'),
            date('date_from', 'Date From (DD-MM-YYYY)'),
            date('date_to', 'Date To (DD-MM-YYYY)'),
            select('level', 'Level', ['National', 'International', 'Institutional']),
            text('resource_persons', 'Name of Resource Person(s) / Agencies'),
            text('year_of_implementation', 'Year of Implementation (if via Clubs/Cells)'),
            select('feedback_collected', 'Program Feedback Collected', ['Yes', 'No']),
        ]
    },

    'MoU Collaboration Events': {
        'category': 'Industrial Relationship',
        'label': 'MoU Collaboration Events',
        'fields': [
            text('institution_industry', 'Name of Institution / Industry / Corporate House'),
            date('mou_date', 'Date of Signing MoU (DD-MM-YYYY)'),
            text('mou_duration', 'Duration of MoU'),
            textarea('mou_details', 'Details of MoU'),
            textarea('activities_list', 'List of Activities Under MoU'),
            text('spoc_faculty', 'Institute SPoC of MoU (Faculty Name)'),
            number('students_benefited', 'Number of Students/Faculty Benefited'),
            select('feedback_collected', 'Program Feedback Collected', ['Yes', 'No']),
        ]
    },

    'Extension and Outreach': {
        'category': 'Student Activity',
        'label': 'Extension and Outreach',
        'fields': [
            text('activity_name', 'Name of the Activity'),
            text('organising_unit', 'Organising Unit / Agency / Collaborating Agency'),
            text('scheme_name', 'Name of the Scheme'),
            date('activity_date', 'Date of the Activity (DD-MM-YYYY)'),
            text('venue', 'Venue'),
            number('students_participated', 'Number of Students Participated'),
        ]
    },

    'Student Scholarship': {
        'category': 'Student Activity',
        'label': 'Student Scholarship',
        'fields': [
            select('year_of_study', 'Year of Study', ['I Year', 'II Year', 'III Year', 'IV Year']),
            text('scheme_name', 'Name of the Scheme'),
            number('govt_students_count', 'No. of Students Benefited by Govt Scheme'),
            number('govt_amount', 'Amount from Govt Scheme (Rs)'),
            number('inst_students_count', 'No. of Students Benefited by Institution Scheme'),
            number('inst_amount', 'Amount from Institution Scheme (Rs)'),
            number('ngo_students_count', 'No. of Students Benefited by NGOs'),
            number('ngo_amount', 'Amount from NGOs (Rs)'),
            number('industry_students_count', 'No. of Students Benefited by Industries'),
            url('document_link', 'Link to Relevant Document'),
        ]
    },

    'Competitive Exams': {
        'category': 'Student Activity',
        'label': 'Competitive Exams',
        'fields': [
            text('student_name', 'Name of Student'),
            text('roll_no', 'Registration / Roll Number for Exam'),
            select('participated_qualified', 'Participated / Qualified', ['Participated', 'Qualified']),
            select('exam_name', 'Examination', ['GATE', 'CAT', 'GRE', 'GMAT', 'NET', 'SLET', 'JAM', 'IELTS', 'TOEFL', 'Civil Services', 'State Govt Exam', 'BEC', 'IIT', 'Other']),
            date('appearing_date', 'Date of Appearing'),
            date('qualifying_date', 'Date of Qualifying'),
            select('financial_aid', 'Financial Aid Received', ['Yes', 'No']),
        ]
    },

    'Skill Development & VAC': {
        'category': 'Industrial Relationship',
        'label': 'Skill Development & VAC',
        'fields': [
            text('course_name', 'Name of the Course'),
            text('course_code', 'Course Code (if any)'),
            select('course_type', 'Type of Course', ['Employability', 'Entrepreneurship', 'Skill Development', 'Value Added Course', 'OCC']),
            select('course_framework', 'Course Framework', ['NCrF', 'NSQF', 'NHEQF', 'Other']),
            textarea('activities_content', 'Activities/Content with Direct Bearing on Employability'),
            date('activity_date', 'Date of Activity (DD-MM-YYYY)'),
            number('duration_hours', 'Duration of the Course in Hours'),
            text('year_of_offering', 'Year of Offering'),
            number('times_offered', 'No. of Times Offered in Same Academic Year'),
            number('students_enrolled', 'No. of Students Enrolled'),
            number('students_completed', 'No. of Students Completed'),
            select('feedback_collected', 'Training Feedback Collected', ['Yes', 'No']),
        ]
    },

}

# Grouped sheets by category for UI rendering
SHEETS_BY_CATEGORY = {
    'Faculty Development': [k for k, v in SHEET_CONFIG.items() if v['category'] == 'Faculty Development'],
    'Research': [
        'Journal Publications', 'Book Publication', 'Conference', 'Patent', 
        'Research-Submitted', 'Research-Preparation', 'IPR-Preparation',
        'Research Project', 'Research-Funding-Submitted', 
        'Consultancy (Project)', 'Consultancy (Training)', 'Consultancy-Planning',
        'Students In-house Seed Money', 'Technology Transfer', 'Expert Certification', 
        'Skill Services', 'Conference Organization', 'PhD Completion'
    ],
    'Student Activity': [k for k, v in SHEET_CONFIG.items() if v['category'] == 'Student Activity'],
    'Industrial Relationship': [k for k, v in SHEET_CONFIG.items() if v['category'] == 'Industrial Relationship'],
    'Association': [k for k, v in SHEET_CONFIG.items() if v['category'] == 'Association'],
}
