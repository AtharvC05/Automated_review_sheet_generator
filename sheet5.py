import fitz  # PyMuPDF
import os
import mysql.connector
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def connect_db():
    """Database connection with error handling."""
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root", 
            password="1234",
            database="project_review",
            autocommit=True,
        )
    except mysql.connector.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def fetch_project_details(group_id):
    """Fetch project and members info from DB; raise error if not found."""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Fetch project details
        cursor.execute("SELECT * FROM projects WHERE group_id=%s", (group_id,))
        project_row = cursor.fetchone()
        
        if not project_row:
            raise ValueError(f"Project not found for group_id: {group_id}")
        
        project_desc = [desc[0] for desc in cursor.description]
        project = dict(zip(project_desc, project_row))
        
        # Fetch member details
        cursor.execute(
            "SELECT roll_no, student_name, contact_details FROM members WHERE group_id=%s", (group_id,)
        )
        members = cursor.fetchall()
        
        if not members:
            raise ValueError(f"No members found for group_id: {group_id}")
        
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

    return {
        "group_id": project.get("group_id", group_id),
        "project_title": project.get("project_title", ""),
        "guide_name": project.get("guide_name", ""),
        "mentor_name": project.get("mentor_name", ""),
        "mentor_email": project.get("mentor_email", ""),
        "mentor_mobile": project.get("mentor_mobile", ""),
        "r1_name": project.get("evaluator1_name", ""),  # Reviewer 1
        "r2_name": project.get("evaluator2_name", ""),  # Reviewer 2
        "members": members,
    }

def process_fields(doc, data):
    """Fill all form fields with data, make transparent and read-only."""
    filled_count = 0
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        widgets = list(page.widgets())
        
        for widget in widgets:
            field_name = getattr(widget, "field_name", None)
            if not field_name:
                continue

            # Make transparent
            try:
                widget.border_width = 0
                widget.fill_color = None
                widget.border_color = None
                widget.border_style = "none"
            except:
                pass
            
            val = data.get(field_name, "")
            val = "" if val is None else str(val)

            if val.strip():
                field_type = getattr(widget, 'field_type', 0)
                
                if field_type == 2:  # Text field
                    widget.field_value = val.strip()
                    filled_count += 1
                    
                elif field_type == 3:  # Button field (not used since no radio buttons)
                    widget.field_value = val.strip()
                    filled_count += 1
                else:
                    # Unknown field type - try as text
                    widget.field_value = val.strip()
                    filled_count += 1

            # Make read-only
            try:
                widget.field_flags |= 1
            except:
                pass
                
            try:
                widget.update()
            except:
                pass

    return filled_count

def generate_5_pdf(form_data, template_path="Review-V-Sheet.pdf"):
    """Generate PDF with filled form fields for Sheet 5."""
    if not form_data:
        raise ValueError("form_data cannot be empty")
        
    group_id = form_data.get('group_id')
    if not group_id:
        raise ValueError("group_id is required")

    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"PDF template not found: {template_path}")

    # This will raise an error if group_id is not found
    project_info = fetch_project_details(group_id)
    
    # Build field values dictionary with all the placeholders
    field_values = {
        "group_id": str(project_info.get("group_id") or ""),
        "date": str(form_data.get("date") or ""),
        "project_title": str(project_info.get("project_title") or ""),
        "guide_name": str(project_info.get("guide_name") or ""),
        "mentor_name": str(project_info.get("mentor_name") or ""),
        "mentor_email": str(project_info.get("mentor_email") or ""),
        "mentor_mobile": str(project_info.get("mentor_mobile") or ""),
        "r1_name": str(project_info.get("r1_name") or ""),
        "r2_name": str(project_info.get("r2_name") or ""),
    }

    # Add student information (roll_1 to roll_4, student_1 to student_4)
    members = project_info.get('members', [])
    for idx, member in enumerate(members, start=1):
        if idx > 4:
            break
        
        if isinstance(member, (list, tuple)) and len(member) >= 2:
            field_values[f'roll_{idx}'] = str(member[0] or '')
            field_values[f'student_{idx}'] = str(member[1] or '')

    # Map form responses for Sheet 5 fields based on HTML form names
    sheet5_field_map = {
        # Review I scores (maps to PDF fields 1.1, 1.2, 1.3, 1.4)
        'review1_1': '1.1', 'review1_2': '1.2', 
        'review1_3': '1.3', 'review1_4': '1.4',
        
        # Review II scores (maps to PDF fields 2.1, 2.2, 2.3, 2.4)
        'review2_1': '2.1', 'review2_2': '2.2',
        'review2_3': '2.3', 'review2_4': '2.4',
        
        # Review III scores (maps to PDF fields 3.1, 3.2, 3.3, 3.4)
        'review3_1': '3.1', 'review3_2': '3.2',
        'review3_3': '3.3', 'review3_4': '3.4',
        
        # Review IV scores (maps to PDF fields 4.1, 4.2, 4.3, 4.4)
        'review4_1': '4.1', 'review4_2': '4.2',
        'review4_3': '4.3', 'review4_4': '4.4',
        
        # Final Total scores (maps to PDF fields 5.1, 5.2, 5.3, 5.4)
        'final_1': '5.1', 'final_2': '5.2',
        'final_3': '5.3', 'final_4': '5.4',
        
        # Final Comments (maps to PDF field 5.c)
        'c5': '5.c',
    }
    
    # Add form data to field values using the mapping
    for key, val in form_data.items():
        val_str = str(val or '')
        pdf_key = sheet5_field_map.get(key, key)
        field_values[pdf_key] = val_str

    # Process PDF
    doc = fitz.open(template_path)
    filled_count = process_fields(doc, field_values)

    # Save PDF
    out_dir = "generated_pdfs"
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Sheet5_Group_{group_id}_{timestamp}.pdf"
    output_path = os.path.join(out_dir, output_file)

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

    if not os.path.isfile(output_path):
        raise IOError(f"PDF generation failed: output file missing: {output_path}")

    logger.info(f"PDF generated: {output_path} with {filled_count} fields filled")
    return output_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    sample_data = {
        'group_id': 'BIA-01',  # Must exist in database
        'date': '2025-08-06',
        
        # Review I scores for 4 students
        'review1_1': '18', 'review1_2': '17', 
        'review1_3': '19', 'review1_4': '18',
        
        # Review II scores for 4 students
        'review2_1': '19', 'review2_2': '18',
        'review2_3': '17', 'review2_4': '18',
        
        # Review III scores for 4 students
        'review3_1': '18', 'review3_2': '19',
        'review3_3': '17', 'review3_4': '18',
        
        # Review IV scores for 4 students
        'review4_1': '19', 'review4_2': '18',
        'review4_3': '18', 'review4_4': '19',
        
        # Final Total scores for 4 students (out of 100)
        'final_1': '74', 'final_2': '72',
        'final_3': '71', 'final_4': '73',
        
        # Final Comments
        'c5': 'All students have performed consistently well across all review phases. The project demonstrates strong technical implementation and good presentation skills.',
    }

    try:
        pdf_path = generate_5_pdf(sample_data)
        print(f"PDF generated: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")