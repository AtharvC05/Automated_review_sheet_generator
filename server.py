from flask import Flask, render_template, redirect, request, jsonify, send_file
from flask_cors import CORS
import os
import threading
import functools
import logging
import pandas as pd
import json
from datetime import datetime

# Import blueprints only
import data_manager
import scheduler

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.WARNING)  # Reduced logging level
logger = logging.getLogger(__name__)

# Register blueprints
app.register_blueprint(data_manager.bp)
app.register_blueprint(scheduler.bp)

# Import database functions
try:
    from sheet1 import fetch_project_details, connect_db
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Import PDF generation functions
try:
    from sheet1 import generate_fillable_pdf as generate_review1_pdf
except ImportError:
    generate_review1_pdf = None

try:
    from sheet2 import generate_2_pdf as generate_review2_pdf
except ImportError:
    generate_review2_pdf = None

try:
    from sheet3 import generate_3_pdf as generate_review3_pdf
except ImportError:
    generate_review3_pdf = None

try:
    from sheet4 import generate_review4_pdf
except ImportError:
    generate_review4_pdf = None

try:
    from sheet5 import generate_5_pdf as generate_review5_pdf
except ImportError:
    generate_review5_pdf = None

class SafeThread(threading.Thread):
    def __init__(self, target, args=(), kwargs=None):
        super().__init__(target=target, args=args, kwargs=kwargs or {})
        self.result = None
        self.exception = None
    
    def run(self):
        try:
            self.result = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.exception = e

# ================== MAIN ROUTES ==================

@app.route('/')
def index():
    return render_template('review-1.html')

@app.route('/review<int:review_num>')
def review_page(review_num):
    if 1 <= review_num <= 5:
        return render_template(f'review-{review_num}.html')
    return redirect("/")

# ================== API ROUTES ==================

@app.route('/api/project-details')
def api_project_details():
    group_id = request.args.get('group_id')
    if not group_id:
        return jsonify({"error": "group_id is required"}), 400
    try:
        if DATABASE_AVAILABLE:
            project_details = fetch_project_details(group_id)
            return jsonify(project_details)
        else:
            return jsonify({"error": "Database not available"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/review-totals')
def api_review_totals():
    group_id = request.args.get('group_id')
    if not group_id:
        return jsonify({"error": "group_id is required"}), 400
    try:
        return jsonify({"error": "Not implemented"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================== PDF GENERATION ==================

def handle_pdf_generation(generate_function):
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON data"}), 400

        group_id = data.get('group_id')
        if not group_id:
            return jsonify({"error": "Group ID is required"}), 400

        if generate_function == generate_review1_pdf:
            template_path = data.get('template_path', 'Review-I-Sheet.pdf')
            thread = SafeThread(target=generate_function, args=(data, template_path))
        else:
            thread = SafeThread(target=generate_function, args=(data,))
        
        thread.start()
        thread.join()

        if thread.exception:
            return jsonify({"error": f"PDF generation failed: {str(thread.exception)}"}), 500

        if not thread.result or not os.path.exists(thread.result):
            return jsonify({"error": "PDF generation failed - no output file"}), 500

        return send_file(
            thread.result,
            as_attachment=True,
            download_name=os.path.basename(thread.result),
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================== PDF ROUTES ==================

pdf_functions = {
    1: generate_review1_pdf,
    2: generate_review2_pdf,
    3: generate_review3_pdf,
    4: generate_review4_pdf,
    5: generate_review5_pdf
}

for i in range(1, 6):
    pdf_function = pdf_functions.get(i)
    if pdf_function:
        app.add_url_rule(
            f'/generate-pdf-review{i}',
            f'generate_review{i}',
            functools.partial(handle_pdf_generation, pdf_function),
            methods=['POST', 'OPTIONS']
        )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 PROJECT REVIEW MANAGEMENT SYSTEM STARTED")
    print(f"📊 Server running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)


#Hello there this is main server file