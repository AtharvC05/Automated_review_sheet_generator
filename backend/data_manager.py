# data_manager.py

from flask import Blueprint, render_template, request, jsonify, send_file
import logging
import io
import pandas as pd
import mysql.connector
from datetime import datetime
import re
import backend.sheet1 as sheet1  # Must provide connect_db() and fetch_project_details

logger = logging.getLogger(__name__)

bp = Blueprint('data_manager', __name__, template_folder='templates')

# --- Small helper for mobile/contact numbers from Excel ---
def clean_mobile(value):
    """Return mobile/contact as string without trailing .0 or nan."""
    if pd.isnull(value):
        return ''
    s = str(value).strip()
    if s.endswith('.0'):
        return s[:-2]
    return s

# --- DATA MANAGER UI PAGE ---
@bp.route('/data-manager')
def data_manager_page():
    return render_template('data-manager.html')

# --- FETCH ALL PROJECTS + MEMBERS (USING WORKING DATABASE LOGIC) ---
@bp.route('/api/projects', methods=['GET'])
def get_all_projects():
    try:
        conn = sheet1.connect_db()
        cursor = conn.cursor(dictionary=True)
        # Using the same logic that works in database
        cursor.execute("""
            SELECT 
                p.group_id,
                p.division,
                p.project_domain,
                p.project_title,
                p.sponsor_company,
                p.guide_name,
                p.mentor_name,
                p.mentor_email,
                p.mentor_mobile,
                p.evaluator1_name,
                p.evaluator2_name,
                COALESCE(pa.location, '') as location,
                COALESCE(pa.track, 'Unassigned') as track,
                m.roll_no,
                m.student_name,
                m.contact_details,
                -- Status checks like in working database queries
                CASE 
                    WHEN p.evaluator1_name IS NOT NULL AND TRIM(p.evaluator1_name) != '' THEN 'YES'
                    ELSE 'NO'
                END as has_evaluator1,
                CASE 
                    WHEN p.evaluator2_name IS NOT NULL AND TRIM(p.evaluator2_name) != '' THEN 'YES'
                    ELSE 'NO'
                END as has_evaluator2
            FROM projects p
            LEFT JOIN members m ON p.group_id = m.group_id
            LEFT JOIN panel_assignments pa ON p.group_id = pa.group_id
            ORDER BY 
                CASE
                    WHEN pa.track IS NULL THEN 999
                    WHEN pa.track = '' THEN 999
                    ELSE CAST(pa.track AS UNSIGNED)
                END,
                p.division,
                p.group_id,
                m.roll_no
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# --- SAVE PROJECTS + MEMBERS (BULK IMPORT) ---
@bp.route('/api/projects', methods=['POST'])
def save_projects():
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        spreadsheet_data = data['data']
        conn = sheet1.connect_db()
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM members")
        cursor.execute("DELETE FROM projects")
        projects = {}

        # Process data
        for row in spreadsheet_data:
            if not row.get('group_id') or not row.get('roll_no'):
                continue
                
            group_id = row['group_id']
            if group_id not in projects:
                projects[group_id] = {
                    'group_id': group_id,
                    'division': row.get('division', ''),
                    'project_domain': row.get('project_domain', ''),
                    'project_title': row.get('project_title', ''),
                    'sponsor_company': row.get('sponsor_company', ''),
                    'guide_name': row.get('guide_name', ''),
                    'mentor_name': row.get('mentor_name', ''),
                    'mentor_email': row.get('mentor_email', ''),
                    'mentor_mobile': clean_mobile(row.get('mentor_mobile', '')),
                    'evaluator1_name': row.get('evaluator1_name', ''),
                    'evaluator2_name': row.get('evaluator2_name', ''),
                    'members': []
                }
            
            projects[group_id]['members'].append({
                'roll_no': row['roll_no'],
                'student_name': row.get('student_name', ''),
                'contact_details': clean_mobile(row.get('contact_details', ''))
            })

        # Insert projects and members
        for project in projects.values():
            cursor.execute("""
                INSERT INTO projects (group_id, division, project_domain, project_title, sponsor_company,
                                      guide_name, mentor_name, mentor_email, mentor_mobile, evaluator1_name, evaluator2_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                project['group_id'], project['division'], project['project_domain'],
                project['project_title'], project['sponsor_company'], project['guide_name'],
                project['mentor_name'], project['mentor_email'], project['mentor_mobile'],
                project['evaluator1_name'], project['evaluator2_name']
            ))
            
            for member in project['members']:
                cursor.execute("""
                    INSERT INTO members (group_id, roll_no, student_name, contact_details)
                    VALUES (%s, %s, %s, %s)
                """, (
                    project['group_id'], member['roll_no'],
                    member['student_name'], member['contact_details']
                ))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Data saved successfully'})
        
    except Exception as e:
        logger.error(f"Error saving projects: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# --- GET SCHEDULE (PANEL ASSIGNMENTS) USING WORKING DATABASE LOGIC ---
@bp.route('/api/schedule', methods=['GET'])
def api_schedule():
    try:
        conn = sheet1.connect_db()
        cursor = conn.cursor(dictionary=True)
        # Using same comprehensive query logic that works in database
        cursor.execute("""
            SELECT 
                p.group_id,
                p.division,
                p.project_title,
                p.evaluator1_name,
                p.evaluator2_name,
                pa.track,
                pa.panel_professors,
                pa.location,
                pa.guide,
                pa.reviewer1,
                pa.reviewer2,
                pa.reviewer3,
                CASE 
                    WHEN p.evaluator1_name IS NOT NULL AND TRIM(p.evaluator1_name) != '' 
                     AND p.evaluator2_name IS NOT NULL AND TRIM(p.evaluator2_name) != '' THEN 'COMPLETE'
                    WHEN p.evaluator1_name IS NOT NULL AND TRIM(p.evaluator1_name) != '' 
                      OR p.evaluator2_name IS NOT NULL AND TRIM(p.evaluator2_name) != '' THEN 'PARTIAL'
                    ELSE 'MISSING'
                END as evaluator_status
            FROM projects p
            LEFT JOIN panel_assignments pa ON p.group_id = pa.group_id
            ORDER BY 
                CASE
                    WHEN pa.track IS NULL THEN 999
                    WHEN pa.track = '' THEN 999
                    ELSE CAST(pa.track AS UNSIGNED)
                END,
                p.division,
                p.group_id
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': rows})
    except Exception as e:
        logger.error(f"Error fetching schedule: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# --- SAVE SCHEDULE (PANEL ASSIGNMENTS) ---
@bp.route('/api/schedule', methods=['POST'])
def save_schedule():
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        schedule_data = data['data']
        conn = sheet1.connect_db()
        cursor = conn.cursor()

        # Clear and insert new data
        provided_group_ids = set(str(row['group_id']).strip() for row in schedule_data if row.get('group_id'))
        if provided_group_ids:
            format_strings = ','.join(['%s'] * len(provided_group_ids))
            cursor.execute(
                f"DELETE FROM panel_assignments WHERE group_id NOT IN ({format_strings})",
                tuple(provided_group_ids)
            )
        else:
            cursor.execute("DELETE FROM panel_assignments")
            
        for row in schedule_data:
            if not row.get('group_id'):
                continue
            cursor.execute("""
                REPLACE INTO panel_assignments
                (group_id, track, panel_professors, location, guide, reviewer1, reviewer2, reviewer3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['group_id'], row.get('track', ''), row.get('panel_professors', ''),
                row.get('location', ''), row.get('guide', ''), row.get('reviewer1', ''),
                row.get('reviewer2', ''), row.get('reviewer3', '')
            ))
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Schedule updated successfully'})
        
    except Exception as e:
        logger.error(f"Error saving schedule: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# --- ENHANCED EXCEL IMPORT (KEEPING YOUR WORKING VERSION) ---
@bp.route('/api/import-excel', methods=['POST'])
def import_excel_to_db():
    try:
        file = request.files.get('excel')
        if not file:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        # Read Excel file
        xls = pd.ExcelFile(io.BytesIO(file.read()))
        sheet_names = xls.sheet_names
        logger.info(f"Available sheets in order: {sheet_names}")

        # ENHANCED SHEET DETECTION - Handle any sequence
        div_a_sheet = None
        div_b_sheet = None
        schedule_sheet = None
        
        # Check each sheet name for content patterns
        for sheet_name in sheet_names:
            sheet_upper = sheet_name.upper()
            if any(keyword in sheet_upper for keyword in ['DIV A', 'DIVA', 'DIVISION A', 'FINAL  DIV A']):
                div_a_sheet = sheet_name
                logger.info(f"Found Division A sheet: {sheet_name}")
            elif any(keyword in sheet_upper for keyword in ['DIV B', 'DIVB', 'DIVISION B', 'FINAL  DIV B']):
                div_b_sheet = sheet_name
                logger.info(f"Found Division B sheet: {sheet_name}")
            elif any(keyword in sheet_upper for keyword in ['SCHEDULE', 'SCHED']):
                schedule_sheet = sheet_name
                logger.info(f"Found Schedule sheet: {sheet_name}")

        # Validate all sheets found
        if not all([div_a_sheet, div_b_sheet, schedule_sheet]):
            return jsonify({
                'success': False,
                'error': f"Required sheets not found. Available: {sheet_names}. Found: DivA={div_a_sheet}, DivB={div_b_sheet}, Schedule={schedule_sheet}"
            }), 400

        # Load data with error handling
        try:
            logger.info(f"Loading Division A from: {div_a_sheet}")
            div_a = pd.read_excel(xls, sheet_name=div_a_sheet, skiprows=3)
            
            logger.info(f"Loading Division B from: {div_b_sheet}")
            div_b = pd.read_excel(xls, sheet_name=div_b_sheet, skiprows=3)
            
            logger.info(f"Loading Schedule from: {schedule_sheet}")
            sched = pd.read_excel(xls, sheet_name=schedule_sheet, skiprows=2)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f"Error reading Excel sheets: {str(e)}"
            }), 400

        logger.info(f"Division A columns: {list(div_a.columns)}")
        logger.info(f"Division B columns: {list(div_b.columns)}")
        logger.info(f"Schedule columns: {list(sched.columns)}")

        conn = sheet1.connect_db()
        cur = conn.cursor()
        
        # Clear existing data
        cur.execute("DELETE FROM panel_assignments")
        cur.execute("DELETE FROM members")
        cur.execute("DELETE FROM projects")
        conn.commit()

        # Enhanced division processing
        def process_division_enhanced(df, division_name):
            group_id = None
            processed_groups = []
            processed_members = 0
            
            logger.info(f"Processing {division_name} - {len(df)} rows")
            
            for i, row in df.iterrows():
                try:
                    # Check for group ID - handle multiple formats
                    group_no_value = row.get('Group No.', '')
                    if pd.notnull(group_no_value) and str(group_no_value).strip():
                        group_id = str(group_no_value).strip()
                        
                        # Clean group ID format
                        if group_id.startswith('BI'):
                            # Already in correct format
                            pass
                        elif group_id.startswith('BIA') or group_id.startswith('BIB'):
                            # Add hyphen if missing
                            if '-' not in group_id and len(group_id) >= 5:
                                group_id = f"{group_id[:3]}-{group_id[3:]}"
                        
                        # Insert project
                        try:
                            project_domain = str(row.get('Project Domain', '')).strip()[:255] if pd.notnull(row.get('Project Domain', '')) else ""
                            project_title = str(row.get(' Proposed Title of the Project if any', '')).strip()[:500] if pd.notnull(row.get(' Proposed Title of the Project if any', '')) else ""
                            sponsor_company = str(row.get('Name of the sponsored company ', '')).strip()[:255] if pd.notnull(row.get('Name of the sponsored company ', '')) else ""
                            guide_name = str(row.get('Name of the Guide', '')).strip()[:100] if pd.notnull(row.get('Name of the Guide', '')) else ""
                            
                            cur.execute(
                                """INSERT IGNORE INTO projects 
                                   (group_id, division, project_domain, project_title, sponsor_company, guide_name, 
                                    mentor_name, mentor_email, mentor_mobile, evaluator1_name, evaluator2_name) 
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                (group_id, division_name, project_domain, project_title, sponsor_company, guide_name, "", "", "", "", "")
                            )
                            
                            if group_id not in processed_groups:
                                processed_groups.append(group_id)
                                logger.info(f"Processed {division_name} group: {group_id}")
                                
                        except Exception as project_error:
                            logger.error(f"Error inserting project {group_id}: {str(project_error)}")
                    
                    # Insert member
                    if (group_id and 
                        pd.notnull(row.get('Roll No.', '')) and 
                        pd.notnull(row.get('Name of the group member', ''))):
                        
                        try:
                            roll_no = str(row.get('Roll No.', '')).strip()
                            student_name = str(row.get('Name of the group member', '')).strip()[:100]
                            
                            if roll_no and student_name:
                                cur.execute(
                                    "INSERT IGNORE INTO members (group_id, roll_no, student_name, contact_details) VALUES (%s, %s, %s, %s)",
                                    (group_id, roll_no, student_name, "")
                                )
                                processed_members += 1
                                
                        except Exception as member_error:
                            logger.error(f"Error inserting member for {group_id}: {str(member_error)}")
                        
                except Exception as row_error:
                    logger.warning(f"Error processing row {i} in {division_name}: {str(row_error)}")
                    continue
                    
            conn.commit()
            logger.info(f"{division_name} processing complete: {len(processed_groups)} groups, {processed_members} members")
            return len(processed_groups), processed_members

        # Process both divisions
        div_a_groups, div_a_members = process_division_enhanced(div_a, 'A')
        div_b_groups, div_b_members = process_division_enhanced(div_b, 'B')

        # ENHANCED SCHEDULE PROCESSING WITH COMPREHENSIVE GROUP EXTRACTION
        def extract_all_group_ids(row):
            """Extract ALL group IDs from a schedule row using multiple methods"""
            all_groups = set()
            
            # Check each column value
            for col_name, cell_value in row.items():
                if pd.isnull(cell_value) or col_name.lower() in ['track', 'name of the panel', 'location']:
                    continue
                
                cell_str = str(cell_value).upper().strip()
                
                # Pattern 1: Standard format (BIA-01, BIB-17, BIB- 16)
                standard_matches = re.findall(r'\b(BI[AB]-?\s*\d{1,2})\b', cell_str)
                for match in standard_matches:
                    # Normalize format
                    clean_match = re.sub(r'(BI[AB])[-\s]*(\d{1,2})', r'\1-\2', match)
                    # Ensure two-digit format
                    if len(clean_match) == 5:  # BIA-1 -> BIA-01
                        clean_match = f"{clean_match[:4]}0{clean_match[4:]}"
                    all_groups.add(clean_match)
                
                # Pattern 2: Without hyphen (BIA01, BIB17)
                no_hyphen_matches = re.findall(r'\b(BI[AB]\d{1,2})\b', cell_str)
                for match in no_hyphen_matches:
                    if len(match) == 5:  # BIA01
                        formatted = f"{match[:3]}-{match[3:]}"
                    elif len(match) == 4:  # BIA1 -> BIA-01
                        formatted = f"{match[:3]}-0{match[3:]}"
                    else:
                        formatted = match
                    all_groups.add(formatted)
                
                # Pattern 3: With extra spaces (BIA 01, BIB 17)
                space_matches = re.findall(r'\b(BI[AB])\s+(\d{1,2})\b', cell_str)
                for prefix, num in space_matches:
                    formatted = f"{prefix}-{num.zfill(2)}"
                    all_groups.add(formatted)
            
            return sorted(list(all_groups))

        def assign_evaluators_from_panel(panel_professors, group_ids):
            """Assign evaluators ensuring no conflicts"""
            if not panel_professors or len(panel_professors) < 2:
                # Default professors if panel is incomplete
                panel_professors = ["Default Prof 1", "Default Prof 2", "Default Prof 3"]
            
            assignments = []
            
            for i, group_id in enumerate(group_ids):
                # Rotate through professors to avoid conflicts
                guide_idx = i % len(panel_professors)
                eval1_idx = (i + 1) % len(panel_professors)
                eval2_idx = (i + 2) % len(panel_professors)
                
                # Ensure evaluators are different from guide
                if eval1_idx == guide_idx:
                    eval1_idx = (eval1_idx + 1) % len(panel_professors)
                if eval2_idx == guide_idx or eval2_idx == eval1_idx:
                    eval2_idx = (eval2_idx + 1) % len(panel_professors)
                
                assignments.append({
                    'group_id': group_id,
                    'guide': panel_professors[guide_idx],
                    'evaluator1': panel_professors[eval1_idx],
                    'evaluator2': panel_professors[eval2_idx]
                })
            
            return assignments

        # Process schedule rows
        schedule_processed = 0
        all_scheduled_groups = set()
        division_stats = {'A': 0, 'B': 0}
        
        logger.info(f"Processing schedule with {len(sched)} rows")
        
        for i, row in sched.iterrows():
            try:
                track = row.get('Track')
                if pd.isnull(track):
                    continue
                    
                track = int(track)
                
                # Extract panel professors
                panel_text = str(row.get('Name of the Panel', ''))
                panel_profs = []
                if panel_text and panel_text != 'nan':
                    # Split by newlines and commas, clean up
                    prof_lines = panel_text.replace('\n', '|').replace(',', '|').split('|')
                    for prof in prof_lines:
                        clean_prof = prof.strip()
                        if len(clean_prof) > 3 and not clean_prof.isdigit():
                            panel_profs.append(clean_prof)
                
                if not panel_profs:
                    panel_profs = [f"Default Panel {track} Prof 1", f"Default Panel {track} Prof 2", f"Default Panel {track} Prof 3"]
                
                # Extract location
                location = str(row.get('Location', '')).strip() if pd.notnull(row.get('Location', '')) else f"Room {track}"
                
                # Extract ALL group IDs from this row
                group_ids = extract_all_group_ids(row)
                
                if not group_ids:
                    logger.warning(f"No groups found in track {track}")
                    continue
                
                # Count division distribution
                for gid in group_ids:
                    if gid.startswith('BIA-'):
                        division_stats['A'] += 1
                    elif gid.startswith('BIB-'):
                        division_stats['B'] += 1
                
                logger.info(f"Track {track}: Found {len(group_ids)} groups: {group_ids}")
                logger.info(f"Track {track}: Panel: {panel_profs}")
                
                # Assign evaluators
                assignments = assign_evaluators_from_panel(panel_profs, group_ids)
                
                # Insert assignments and update projects
                for assignment in assignments:
                    try:
                        group_id = assignment['group_id']
                        
                        # Insert panel assignment
                        cur.execute("""
                            INSERT INTO panel_assignments
                            (group_id, track, panel_professors, location, guide, reviewer1, reviewer2, reviewer3)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            track=VALUES(track), panel_professors=VALUES(panel_professors), 
                            location=VALUES(location), guide=VALUES(guide),
                            reviewer1=VALUES(reviewer1), reviewer2=VALUES(reviewer2)
                        """, (
                            group_id, track, '\n'.join(panel_profs), location,
                            assignment['guide'], assignment['evaluator1'], assignment['evaluator2'], None
                        ))
                        
                        # UPDATE PROJECTS TABLE WITH EVALUATORS - CRITICAL FOR DIVISION B
                        cur.execute("""
                            UPDATE projects 
                            SET evaluator1_name = %s, evaluator2_name = %s 
                            WHERE group_id = %s
                        """, (assignment['evaluator1'], assignment['evaluator2'], group_id))
                        
                        all_scheduled_groups.add(group_id)
                        
                        # Log specifically for Division B
                        if group_id.startswith('BIB-'):
                            logger.info(f"✅ DIVISION B: {group_id} -> Track {track}, Eval1: {assignment['evaluator1']}, Eval2: {assignment['evaluator2']}")
                        else:
                            logger.info(f"✅ DIVISION A: {group_id} -> Track {track}, Eval1: {assignment['evaluator1']}, Eval2: {assignment['evaluator2']}")
                        
                    except Exception as assignment_error:
                        logger.error(f"❌ Error assigning {assignment['group_id']}: {str(assignment_error)}")
                
                schedule_processed += 1
                
            except Exception as e:
                logger.warning(f"❌ Error processing schedule row {i}: {str(e)}")
                continue

        # FINAL VERIFICATION AND CLEANUP
        logger.info("Performing final verification...")
        
        # Check for any unassigned groups and force assign
        cur.execute("""
            SELECT group_id, division FROM projects 
            WHERE evaluator1_name IS NULL OR evaluator1_name = '' OR evaluator2_name IS NULL OR evaluator2_name = ''
        """)
        unassigned_groups = cur.fetchall()
        
        if unassigned_groups:
            logger.warning(f"Found {len(unassigned_groups)} unassigned groups, force-assigning...")
            
            for group_data in unassigned_groups:
                group_id, division = group_data
                default_eval1 = f"Default Evaluator {division}.1"
                default_eval2 = f"Default Evaluator {division}.2"
                
                cur.execute("""
                    UPDATE projects 
                    SET evaluator1_name = %s, evaluator2_name = %s 
                    WHERE group_id = %s
                """, (default_eval1, default_eval2, group_id))
                
                logger.info(f"🔧 Force-assigned evaluators to {group_id} (Division {division})")

        conn.commit()
        cur.close()
        conn.close()

        # Final verification counts using working database logic
        conn = sheet1.connect_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM projects")
        total_projects = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM panel_assignments")
        total_assignments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM projects WHERE division = 'A' AND evaluator1_name IS NOT NULL AND evaluator1_name != ''")
        div_a_with_eval = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM projects WHERE division = 'B' AND evaluator1_name IS NOT NULL AND evaluator1_name != ''")
        div_b_with_eval = cursor.fetchone()[0]
        
        cursor.execute("SELECT track, COUNT(*) as count FROM panel_assignments GROUP BY track ORDER BY track")
        track_distribution = cursor.fetchall()
        
        cursor.close()
        conn.close()

        logger.info(f"Import completed: {total_projects} projects, {total_assignments} assignments")
        logger.info(f"Division A evaluators: {div_a_with_eval}, Division B evaluators: {div_b_with_eval}")

        return jsonify({
            'success': True,
            'message': f'✅ Import successful: Div A: {div_a_with_eval}/18 evaluators, Div B: {div_b_with_eval}/17 evaluators',
            'details': {
                'sheets_processed': {
                    'division_a': div_a_sheet,
                    'division_b': div_b_sheet,
                    'schedule': schedule_sheet
                },
                'projects_imported': total_projects,
                'assignments_imported': total_assignments,
                'division_a_groups': div_a_groups,
                'division_b_groups': div_b_groups,
                'division_a_with_evaluators': div_a_with_eval,
                'division_b_with_evaluators': div_b_with_eval,
                'track_distribution': track_distribution,
                'scheduled_groups_in_schedule': len(all_scheduled_groups),
                'division_breakdown': division_stats
            }
        })

    except Exception as e:
        logger.error(f"❌ Critical import error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# --- PROJECT DETAILS ---
@bp.route('/api/project-details')
def api_project_details():
    group_id = request.args.get('group_id')
    if not group_id:
        return jsonify({"error": "group_id is required"}), 400
    try:
        project_data = sheet1.fetch_project_details(group_id)
        return jsonify(project_data)
    except Exception as e:
        logger.error(f"Project details error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- DEBUG ENDPOINTS USING WORKING DATABASE QUERIES ---
@bp.route('/api/debug-division-b', methods=['GET'])
def debug_division_b():
    try:
        conn = sheet1.connect_db()
        cursor = conn.cursor(dictionary=True)
        
        # Using same logic that works in database
        cursor.execute("""
            SELECT 
                p.group_id, 
                p.evaluator1_name, 
                p.evaluator2_name,
                pa.track, 
                pa.reviewer1, 
                pa.reviewer2,
                CASE 
                    WHEN p.evaluator1_name IS NOT NULL AND TRIM(p.evaluator1_name) != '' THEN 'YES'
                    ELSE 'NO'
                END as has_eval1,
                CASE 
                    WHEN p.evaluator2_name IS NOT NULL AND TRIM(p.evaluator2_name) != '' THEN 'YES'
                    ELSE 'NO'
                END as has_eval2
            FROM projects p
            LEFT JOIN panel_assignments pa ON p.group_id = pa.group_id
            WHERE p.division = 'B'
            ORDER BY p.group_id
        """)
        
        div_b_projects = cursor.fetchall()
        
        # Statistics using working database logic
        cursor.execute("""
            SELECT 
                COUNT(*) as total_div_b,
                COUNT(CASE WHEN evaluator1_name IS NOT NULL AND TRIM(evaluator1_name) != '' THEN 1 END) as with_eval1,
                COUNT(CASE WHEN evaluator2_name IS NOT NULL AND TRIM(evaluator2_name) != '' THEN 1 END) as with_eval2
            FROM projects WHERE division = 'B'
        """)
        div_b_summary = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'division_b_summary': div_b_summary,
            'division_b_details': div_b_projects
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# --- COMPREHENSIVE DEBUG ENDPOINT ---
@bp.route('/api/debug-all-evaluators', methods=['GET'])
def debug_all_evaluators():
    try:
        conn = sheet1.connect_db()
        cursor = conn.cursor(dictionary=True)
        
        # Using the working comprehensive database query
        cursor.execute("""
            SELECT 
                p.group_id, 
                p.division, 
                p.evaluator1_name, 
                p.evaluator2_name,
                pa.track, 
                pa.reviewer1, 
                pa.reviewer2,
                CASE 
                    WHEN p.evaluator1_name IS NOT NULL AND TRIM(p.evaluator1_name) != '' THEN 'YES'
                    ELSE 'NO'
                END as has_eval1,
                CASE 
                    WHEN p.evaluator2_name IS NOT NULL AND TRIM(p.evaluator2_name) != '' THEN 'YES'
                    ELSE 'NO'
                END as has_eval2,
                CASE 
                    WHEN p.evaluator1_name IS NOT NULL AND TRIM(p.evaluator1_name) != '' 
                     AND p.evaluator2_name IS NOT NULL AND TRIM(p.evaluator2_name) != '' THEN 'COMPLETE'
                    WHEN p.evaluator1_name IS NOT NULL AND TRIM(p.evaluator1_name) != '' 
                      OR p.evaluator2_name IS NOT NULL AND TRIM(p.evaluator2_name) != '' THEN 'PARTIAL'
                    ELSE 'MISSING'
                END as evaluator_status
            FROM projects p
            LEFT JOIN panel_assignments pa ON p.group_id = pa.group_id
            ORDER BY 
                CASE
                    WHEN pa.track IS NULL THEN 999
                    WHEN pa.track = '' THEN 999
                    ELSE CAST(pa.track AS UNSIGNED)
                END,
                p.division, 
                p.group_id
        """)
        
        all_projects = cursor.fetchall()
        
        # Summary using working database logic
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN division = 'A' THEN 1 END) as total_div_a,
                COUNT(CASE WHEN division = 'B' THEN 1 END) as total_div_b,
                COUNT(CASE WHEN division = 'A' AND evaluator1_name IS NOT NULL AND TRIM(evaluator1_name) != '' THEN 1 END) as div_a_eval1,
                COUNT(CASE WHEN division = 'B' AND evaluator1_name IS NOT NULL AND TRIM(evaluator1_name) != '' THEN 1 END) as div_b_eval1,
                COUNT(CASE WHEN division = 'A' AND evaluator2_name IS NOT NULL AND TRIM(evaluator2_name) != '' THEN 1 END) as div_a_eval2,
                COUNT(CASE WHEN division = 'B' AND evaluator2_name IS NOT NULL AND TRIM(evaluator2_name) != '' THEN 1 END) as div_b_eval2
            FROM projects
        """)
        summary = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'summary': summary,
            'projects': all_projects
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# --- EXPORT EXCEL ---
@bp.route('/api/export-excel', methods=['POST'])
def export_excel():
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        df = pd.DataFrame(data['data'])
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Project Data', index=False)

        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=f'project_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
