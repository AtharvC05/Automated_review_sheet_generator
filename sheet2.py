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
        "r2_name": project.get("evaluator2_name", ""), # Reviewer 2
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
                    
                elif field_type == 3:  # Button field
                    try:
                        widget.button_value = val.strip()
                        widget.set_checked(val.strip())
                        filled_count += 1
                    except:
                        val_upper = val.strip().upper()
                        if val_upper in ("Y", "YES", "TRUE", "1"):
                            try:
                                widget.check(True)
                            except:
                                widget.field_value = "Y"
                        elif val_upper in ("N", "NO", "FALSE", "0"):
                            try:
                                widget.check(False)
                            except:
                                widget.field_value = "N"
                        else:
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

def generate_2_pdf(form_data, template_path="Review-II-Sheet.pdf"):
    """Generate PDF with filled form fields for Review II Sheet."""
    if not form_data:
        raise ValueError("form_data cannot be empty")
        
    group_id = form_data.get("group_id")
    if not group_id:
        raise ValueError("group_id is required")

    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"PDF template not found: {template_path}")

    # This will raise an error if group_id is not found
    project_info = fetch_project_details(group_id)
    
    # Build field values dictionary
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

    # Add student information
    members = project_info.get("members", [])
    for idx, member in enumerate(members, start=1):
        if idx > 4:
            break
        
        if isinstance(member, (list, tuple)) and len(member) >= 3:
            field_values[f"roll_{idx}"] = str(member[0] or "")
            field_values[f"student_{idx}"] = str(member[1] or "")
            field_values[f"contact_{idx}"] = str(member[2] or "")

    # Map form responses for Review II questions
    que_to_pdf_field_map = {
        # Section 2.1 questions (ID fields for checkboxes/radio buttons)
        'que_2.1.1': '2.1.1id', 'que_2.1.2': '2.1.2id', 'que_2.1.3': '2.1.3id',
        'que_2.1.4': '2.1.4id', 'que_2.1.5': '2.1.5id', 'que_2.1.6': '2.1.6id',
        'que_2.1.7': '2.1.7id', 'que_2.1.8': '2.1.8id', 'que_2.1.9': '2.1.9id',
        'que_2.1.10': '2.1.10id', 'que_2.1.11': '2.1.11id', 'que_2.1.12': '2.1.12id',
        'que_2.1.13': '2.1.13id', 'que_2.1.14': '2.1.14id', 'que_2.1.15': '2.1.15id',
        'que_2.1.16': '2.1.16id',
        
        
        # Summary fields
        'sum_2.1': '2.1.s1', 'sum_2.2': '2.2.s1', 'sum_2.3': '2.3.s1', 'sum_2.4': '2.4.s1',
        
        # Comments
        'c2': '2.c',
    }
    
    for key, val in form_data.items():
        val_str = str(val or "")
        pdf_key = que_to_pdf_field_map.get(key, key)
        field_values[pdf_key] = val_str

    # Process PDF
    doc = fitz.open(template_path)
    filled_count = process_fields(doc, field_values)

    # Save PDF
    out_dir = "generated_pdfs"
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Review_2_Group_{group_id}_{timestamp}.pdf"
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
        "group_id": "BIA-01",  # Must exist in database
        "date": "2025-08-06",
        
        # Section 2.1 - ID questions (Yes/No/NA)
        "que_2.1.1": "Y", "que_2.1.2": "N", "que_2.1.3": "Y",
        "que_2.1.4": "Y", "que_2.1.5": "N", "que_2.1.6": "Y",
        "que_2.1.7": "Y", "que_2.1.8": "N", "que_2.1.9": "Y",
        "que_2.1.10": "Y", "que_2.1.11": "N", "que_2.1.12": "Y",
        "que_2.1.13": "Y", "que_2.1.14": "N", "que_2.1.15": "Y",
        "que_2.1.16": "Y",
        
        # Section 2.2 - Marks (0-10)
        "que_2.2.1": "8", "que_2.2.2": "7", "que_2.2.3": "9",
        "que_2.2.4": "8", "que_2.2.5": "7", "que_2.2.6": "8",
        "que_2.2.7": "9", "que_2.2.8": "8",
        
        # Section 2.3 - Marks (0-10)
        "que_2.3.1": "7", "que_2.3.2": "8", "que_2.3.3": "9",
        "que_2.3.4": "8", "que_2.3.5": "7", "que_2.3.6": "8",
        "que_2.3.7": "9", "que_2.3.8": "7",
        
        # Section 2.4 - Marks (0-10)  
        "que_2.4.1": "8", "que_2.4.2": "9", "que_2.4.3": "7",
        "que_2.4.4": "8", "que_2.4.5": "8", "que_2.4.6": "9",
        "que_2.4.7": "7", "que_2.4.8": "8",
        
        # Summary scores
        "sum_2.1": "15", "sum_2.2": "64", "sum_2.3": "63", "sum_2.4": "64",
        
        # Comments
        "comments": "Excellent progress in Review II. Good implementation and documentation."
    }

    try:
        pdf_path = generate_2_pdf(sample_data)
        print(f"PDF generated: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")
