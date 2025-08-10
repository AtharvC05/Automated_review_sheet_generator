-- Create the main database
CREATE DATABASE IF NOT EXISTS project_review;

USE project_review;

-- Drop existing tables in correct order (to handle foreign key constraints)
DROP TABLE IF EXISTS batch_assignments;
DROP TABLE IF EXISTS faculty_workload;
DROP TABLE IF EXISTS review_batches;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS faculty;

-- ================== MAIN PROJECT TABLES ==================

-- Create the projects table
CREATE TABLE projects (
    group_id VARCHAR(50) PRIMARY KEY,
    project_title TEXT,
    guide_name TEXT,
    mentor_name TEXT,
    mentor_email TEXT,
    mentor_mobile TEXT
);

-- Create the members table
CREATE TABLE members (
    group_id VARCHAR(50),
    roll_no VARCHAR(50),
    student_name TEXT,
    contact_details TEXT,
    FOREIGN KEY (group_id) REFERENCES projects(group_id) ON DELETE CASCADE,
    UNIQUE KEY unique_roll (roll_no)
);

-- ================== SCHEDULER TABLES ==================

-- Create faculty table for scheduler
CREATE TABLE faculty (
    faculty_id INT PRIMARY KEY AUTO_INCREMENT,
    faculty_name VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100),
    seniority_level ENUM('junior', 'senior') DEFAULT 'junior',
    max_groups_as_guide INT DEFAULT 1
);

-- Create review batches table
CREATE TABLE review_batches (
    batch_id INT PRIMARY KEY AUTO_INCREMENT,
    batch_name VARCHAR(50),
    review_date DATE,
    review_time TIME,
    location VARCHAR(100),
    room_no VARCHAR(100)
);

-- Create batch assignments table
CREATE TABLE batch_assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id INT,
    group_id VARCHAR(50),
    guide_faculty_id INT,
    evaluator1_faculty_id INT,
    evaluator2_faculty_id INT,
    FOREIGN KEY (batch_id) REFERENCES review_batches(batch_id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES projects(group_id) ON DELETE CASCADE,
    FOREIGN KEY (guide_faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    FOREIGN KEY (evaluator1_faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    FOREIGN KEY (evaluator2_faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL
);

-- Create faculty workload tracking table
CREATE TABLE faculty_workload (
    faculty_id INT,
    total_guide_assignments INT DEFAULT 0,
    total_evaluator_assignments INT DEFAULT 0,
    PRIMARY KEY (faculty_id),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
);

-- ================== SAMPLE DATA INSERTION ==================

-- Insert projects based on your corrected data
INSERT INTO projects (group_id, project_title, guide_name, mentor_name, mentor_email, mentor_mobile) 
VALUES 
('BIA-01', 'Advanced Dashboard for Crop Suitability and Plant Health Monitoring', 'Dr. Sonali Patil', 'Mr. Rajesh Kumar', 'rajesh@techcorp.com', '9876543210'),
('BIA-02', 'Comprehensive Compliance Management Platform', 'Prof. Saurabh Natu', 'Ms. Priya Sharma', 'priya@infosys.com', '9876543211'),
('BIA-03', 'Understanding Code With Sherlock', 'Prof. Monali Deshmukh', 'Mr. Amit Verma', 'amit@wipro.com', '9876543212'),
('BIA-04', 'GeoToll - GPS Based Toll Tracking System', 'Dr. Bhavana Kanawade', 'Ms. Sneha Patel', 'sneha@tcs.com', '9876543213'),
('BIA-05', 'LifeCraft : An Android Application for Women Safety', 'Prof. Sonal Kulkarni', 'Mr. Vikram Singh', 'vikram@accenture.com', '9876543214'),
('BIA-06', 'Novel Federated learning-based approach for detection and classification of Diabetic Retinopathy', 'Prof. Sarang Saoji', 'Dr. Meera Joshi', 'meera@healthcare.com', '9876543215'),
('BIA-07', 'Enhancing Product Lifecycle Sustainability with Reinforcement Learning for Optimal Decision Making', 'Prof. Prashant Mandale', 'Mr. Kiran Rao', 'kiran@manufacturing.com', '9876543216'),
('BIA-08', 'Deep Learning Techniques for Diagnosing Pediatric Pneumonia Using Chest Radiographs', 'Prof. Gaurav Malode', 'Dr. Suresh Kumar', 'suresh@medical.com', '9876543217'),
('BIA-09', 'Web development: Trip planning website with AI features.', 'Prof. Dipika Walanjkar', 'Ms. Kavya Nair', 'kavya@travel.com', '9876543218'),
('BIA-10', 'AI fitness coach', 'Prof. Kanchan Bhale', 'Mr. Rohit Gupta', 'rohit@fitness.com', '9876543219'),
('BIA-11', 'Document Storage and Retrieval with Efficient Clustering using the Vector Space Model', 'Prof. Jyoti Manoorkar', 'Ms. Anjali Shah', 'anjali@doctech.com', '9876543220'),
('BIA-12', 'Online bus ticket system using IOT', 'Prof. Sharda T.', 'Mr. Manoj Kumar', 'manoj@transport.com', '9876543221'),
('BIA-13', 'Music Recommendation System by Emotion For Multiple Faces', 'Prof. Priti Yampe', 'Ms. Riya Mehta', 'riya@music.com', '9876543222'),
('BIA-14', 'Automated Glaucoma Diagnosis System Using Deep Learning', 'Prof. Monali Bansode', 'Dr. Arjun Patel', 'arjun@eyecare.com', '9876543223'),
('BIA-15', 'Detection of Behavioural differences of underwater fish using Deep Learning', 'Dr. Jyoti Surve', 'Mr. Ocean Research', 'ocean@marine.com', '9876543224'),
('BIA-16', 'Android POS application for NFC', 'Dr. Jyoti Surve', 'Ms. Tech Solutions', 'tech@nfc.com', '9876543225'),
('BIA-17', 'Design and implementation of Vehicle Access Control using License Plate Recognition', 'Prof. Sukruti Dad', 'Mr. Auto Tech', 'auto@security.com', '9876543226'),
('BIA-18', 'Smart Fleet Fuel Tracker - Monitoring of mobile fuel tanks of Bus', 'Prof. Prachi Nilekar', 'Ms. Fleet Manager', 'fleet@logistics.com', '9876543227');

-- Insert members based on your corrected data (fixing duplicates)
INSERT INTO members (group_id, roll_no, student_name, contact_details) 
VALUES
-- BIA-01
('BIA-01', 'BIA06', 'Sahil Bhavsar', 'sahil.bhavsar@student.edu'),
('BIA-01', 'BIA26', 'Adwait Jadhav', 'adwait.jadhav@student.edu'),
('BIA-01', 'BIA30', 'Pradnya Kamble', 'pradnya.kamble@student.edu'),
('BIA-01', 'BIA33', 'Arya Tandale', 'arya.tandale@student.edu'),

-- BIA-02 (corrected roll numbers from Excel)
('BIA-02', 'BIA40', 'Abhishek Kulkarni', 'abhishek.kulkarni@student.edu'),
('BIA-02', 'BIA48', 'Om Nichal', 'om.nichal@student.edu'),
('BIA-02', 'BIB49', 'Dharmendra Pandit', 'dharmendra.pandit@student.edu'),
('BIA-02', 'BIB52', 'Anurag Patil', 'anurag.patil@student.edu'),

-- BIA-03
('BIA-03', 'BIA25', 'Deep Isane', 'deep.isane@student.edu'),
('BIA-03', 'BIA35', 'Dhanashri Ghadage', 'dhanashri.ghadage@student.edu'),
('BIA-03', 'BIA36', 'Mrunali Rangankar', 'mrunali.rangankar@student.edu'),
('BIA-03', 'BIA37', 'Prajakta Supugade', 'prajakta.supugade@student.edu'),

-- BIA-04
('BIA-04', 'BIA01', 'Omkar Aher', 'omkar.aher@student.edu'),
('BIA-04', 'BIA09', 'Srushti Bonde', 'srushti.bonde@student.edu'),
('BIA-04', 'BIA21', 'Dhruv Gidwani', 'dhruv.gidwani@student.edu'),
('BIA-04', 'BIA28', 'Pranav Jawale', 'pranav.jawale@student.edu'),

-- BIA-05 (corrected BIA68 to BIA73 from Excel)
('BIA-05', 'BIA17', 'Shubhange Dubey', 'shubhange.dubey@student.edu'),
('BIA-05', 'BIA23', 'Pranjal Gujjar', 'pranjal.gujjar@student.edu'),
('BIA-05', 'BIA27', 'Divya Jagtap', 'divya.jagtap@student.edu'),
('BIA-05', 'BIA73', 'Rucha Khankre', 'rucha.khankre@student.edu'),

-- BIA-06 (corrected BIA38 to BIA39 from Excel)
('BIA-06', 'BIA07', 'Mahadev Bhosale', 'mahadev.bhosale@student.edu'),
('BIA-06', 'BIA11', 'Om Chaudhary', 'om.chaudhary@student.edu'),
('BIA-06', 'BIA24', 'Tanvi Hardikar', 'tanvi.hardikar@student.edu'),
('BIA-06', 'BIA39', 'Avnish Kshirsagar', 'avnish.kshirsagar@student.edu'),

-- BIA-07 (corrected BIA50 to BIA52 from Excel)
('BIA-07', 'BIA52', 'Prathmesh Patil', 'prathmesh.patil@student.edu'),
('BIA-07', 'BIA18', 'Aditya Gade', 'aditya.gade@student.edu'),
('BIA-07', 'BIA29', 'Swanand Joshi', 'swanand.joshi@student.edu'),
('BIA-07', 'BIA13', 'Sudhanshu Deoghare', 'sudhanshu.deoghare@student.edu'),

-- BIA-08 (corrected roll numbers from Excel)
('BIA-08', 'BIA46', 'Aman Mujawar', 'aman.mujawar@student.edu'),
('BIA-08', 'BIA51', 'Aditya Patil', 'aditya.patil@student.edu'),
('BIA-08', 'BIA74', 'Divyanshu Giri', 'divyanshu.giri@student.edu'),
('BIA-08', 'BIA64', 'Sahil Solanke', 'sahil.solanke@student.edu'),

-- BIA-09 (corrected BIA66 to BIA70 from Excel)
('BIA-09', 'BIA43', 'Airaf Lohar', 'airaf.lohar@student.edu'),
('BIA-09', 'BIA70', 'Pooja Ukade', 'pooja.ukade@student.edu'),
('BIA-09', 'BIB20', 'Mayuri Ganore', 'mayuri.ganore@student.edu'),
('BIA-09', 'BIB30', 'Kesari Kadam', 'kesari.kadam@student.edu'),

-- BIA-10
('BIA-10', 'BIA04', 'Ruthvij Bendale', 'ruthvij.bendale@student.edu'),
('BIA-10', 'BIA20', 'Anish Gaware', 'anish.gaware@student.edu'),
('BIA-10', 'BIA16', 'Vidula Diwate', 'vidula.diwate@student.edu'),
('BIA-10', 'BIA53', 'Asmita Pawar', 'asmita.pawar@student.edu'),

-- BIA-11 (corrected roll numbers from Excel)
('BIA-11', 'BIA57', 'Siddhi Rawool', 'siddhi.rawool@student.edu'),
('BIA-11', 'BIA61', 'Nazaat Shaikh', 'nazaat.shaikh@student.edu'),
('BIA-11', 'BIA62', 'Shruti Shinde', 'shruti.shinde@student.edu'),
('BIA-11', 'BIA68', 'Devansh Thaliya', 'devansh.thaliya@student.edu'),

-- BIA-12 (Changed BIA06 to BIA76 for Yash Bhise to avoid duplicate)
('BIA-12', 'BIA03', 'Mandira Barve', 'mandira.barve@student.edu'),
('BIA-12', 'BIA76', 'Yash Bhise', 'yash.bhise@student.edu'),
('BIA-12', 'BIA15', 'Mithilesh Deshmukh', 'mithilesh.deshmukh@student.edu'),
('BIA-12', 'BIA22', 'Aniket Gite', 'aniket.gite@student.edu'),

-- BIA-13
('BIA-13', 'BIA32', 'Vishvajeet N. Khatal', 'vishvajeet.khatal@student.edu'),
('BIA-13', 'BIA12', 'Tejas Choudhari', 'tejas.choudhari@student.edu'),
('BIA-13', 'BIA19', 'Abhay Gangawane', 'abhay.gangawane@student.edu'),
('BIA-13', 'BIA08', 'Chinmay Boddawar', 'chinmay.boddawar@student.edu'),

-- BIA-14 (corrected roll numbers from Excel)
('BIA-14', 'BIA66', 'Aanchal Takhtar', 'aanchal.takhtar@student.edu'),
('BIA-14', 'BIA63', 'Somya Sikarwar', 'somya.sikarwar@student.edu'),
('BIA-14', 'BIA69', 'Manthan Titarmare', 'manthan.titarmare@student.edu'),
('BIA-14', 'BIA75', 'Abhishek Gaikwad', 'abhishek.gaikwad@student.edu'),

-- BIA-15
('BIA-15', 'BIA02', 'Atharva Awachare', 'atharva.awachare@student.edu'),
('BIA-15', 'BIA14', 'Ajinkya Deshmukh', 'ajinkya.deshmukh@student.edu'),
('BIA-15', 'BIA47', 'Aman Munjewar', 'aman.munjewar@student.edu'),
('BIA-15', 'BIA10', 'Deepak Chand', 'deepak.chand@student.edu'),

-- BIA-16 (corrected roll numbers from Excel, adding 4th member)
('BIA-16', 'BIA58', 'Kshipra Sakhare', 'kshipra.sakhare@student.edu'),
('BIA-16', 'BIA54', 'Krishna Pensalwar', 'krishna.pensalwar@student.edu'),
('BIA-16', 'BIB47', 'Neha Mundase', 'neha.mundase@student.edu'),
('BIA-16', 'BIA77', 'Additional Member', 'additional@student.edu'),

-- BIA-17 (corrected - changed BIB49 to BIB50 for Nameet Pandit to avoid duplicate)
('BIA-17', 'BIB50', 'Nameet Pandit', 'nameet.pandit@student.edu'),
('BIA-17', 'BIA50', 'Aniket Pardeshi', 'aniket.pardeshi@student.edu'),
('BIA-17', 'BIA60', 'Aman Shaikh', 'aman.shaikh@student.edu'),
('BIA-17', 'BIA65', 'Onkar Sumbe', 'onkar.sumbe@student.edu'),

-- BIA-18 (corrected roll numbers from Excel)
('BIA-18', 'BIA34', 'Krushna Sonawane', 'krushna.sonawane@student.edu'),
('BIA-18', 'BIA38', 'Sanika Almale', 'sanika.almale@student.edu'),
('BIA-18', 'BIA44', 'Smita Mane', 'smita.mane@student.edu'),
('BIA-18', 'BIA42', 'Akshada Kusalkar', 'akshada.kusalkar@student.edu');

-- ================== COMPLETE PROJECT LIST (UP TO 35 GROUPS) ==================

-- Add remaining groups to reach 35 total groups
INSERT INTO projects (group_id, project_title, guide_name, mentor_name, mentor_email, mentor_mobile) 
VALUES 
('BIA-19', 'Machine Learning for Predictive Analytics in Healthcare', 'Prof. Rahul Sharma', 'Dr. Healthcare Expert', 'health@expert.com', '9876543228'),
('BIA-20', 'Blockchain-based Supply Chain Management', 'Prof. Priya Mehta', 'Mr. Blockchain Dev', 'blockchain@dev.com', '9876543229'),
('BIA-21', 'IoT-based Smart Home Automation', 'Prof. Amit Patel', 'Ms. IoT Specialist', 'iot@smart.com', '9876543230'),
('BIA-22', 'Cybersecurity Framework for Small Businesses', 'Prof. Neha Singh', 'Mr. Security Expert', 'security@cyber.com', '9876543231'),
('BIA-23', 'AI-powered Chatbot for Customer Service', 'Prof. Vikash Kumar', 'Ms. AI Developer', 'ai@chatbot.com', '9876543232'),
('BIA-24', 'Mobile App for Mental Health Monitoring', 'Prof. Anjali Gupta', 'Dr. Mental Health', 'mental@health.com', '9876543233'),
('BIA-25', 'Cloud-based Document Management System', 'Prof. Rajesh Verma', 'Mr. Cloud Architect', 'cloud@docs.com', '9876543234'),
('BIA-26', 'E-commerce Platform with AI Recommendations', 'Prof. Pooja Shah', 'Ms. Ecommerce Expert', 'ecom@ai.com', '9876543235'),
('BIA-27', 'Virtual Reality Training Simulator', 'Prof. Manoj Yadav', 'Mr. VR Developer', 'vr@training.com', '9876543236'),
('BIA-28', 'Smart Traffic Management System', 'Prof. Deepika Jain', 'Ms. Traffic Engineer', 'traffic@smart.com', '9876543237'),
('BIA-29', 'Automated Testing Framework', 'Prof. Suresh Reddy', 'Mr. Test Automation', 'auto@testing.com', '9876543238'),
('BIA-30', 'Real-time Data Analytics Dashboard', 'Prof. Kavya Nair', 'Ms. Data Analyst', 'data@analytics.com', '9876543239'),
('BIA-31', 'Social Media Sentiment Analysis Tool', 'Prof. Rohit Agarwal', 'Mr. Social Media Expert', 'social@sentiment.com', '9876543240'),
('BIA-32', 'Online Learning Management System', 'Prof. Sunita Das', 'Ms. Education Tech', 'edu@lms.com', '9876543241'),
('BIA-33', 'Inventory Management with RFID', 'Prof. Arjun Malhotra', 'Mr. RFID Specialist', 'rfid@inventory.com', '9876543242'),
('BIA-34', 'Weather Prediction using Machine Learning', 'Prof. Ritu Sharma', 'Dr. Weather Expert', 'weather@prediction.com', '9876543243'),
('BIA-35', 'Smart Agriculture Monitoring System', 'Prof. Kiran Joshi', 'Ms. Agri Tech', 'agri@smart.com', '9876543244');


-- ================== SCHEDULER TABLES ==================

-- Faculty table - stores all faculty members
CREATE TABLE faculty (
    faculty_id INT PRIMARY KEY AUTO_INCREMENT,
    faculty_name VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100),
    seniority_level ENUM('junior', 'senior') DEFAULT 'junior',
    max_groups_as_guide INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Review batches table - represents the 7 batches/tracks
CREATE TABLE review_batches (
    batch_id INT PRIMARY KEY AUTO_INCREMENT,
    batch_name VARCHAR(50),                -- "Batch 1", "Batch 2", etc.
    review_date DATE,
    review_time TIME,
    location VARCHAR(100),                 -- "213", "214", "224", etc.
    room_no VARCHAR(20),                   -- "Room 1", "Room 2", etc.
    track_id INT,                          -- 1, 2, 3, 4, 5, 6, 7
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Batch assignments table - stores group-faculty assignments
CREATE TABLE batch_assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id INT,
    group_id VARCHAR(50),
    guide_faculty_id INT,                  -- 1 Guide per group
    evaluator1_faculty_id INT,             -- 1st Evaluator
    evaluator2_faculty_id INT,             -- 2nd Evaluator  
    row_position INT,                      -- Position within batch (0-4)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (batch_id) REFERENCES review_batches(batch_id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES projects(group_id) ON DELETE CASCADE,
    FOREIGN KEY (guide_faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    FOREIGN KEY (evaluator1_faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    FOREIGN KEY (evaluator2_faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    
    -- Ensure unique group assignment
    UNIQUE KEY unique_group_batch (batch_id, group_id)
);

-- Faculty workload tracking table
CREATE TABLE faculty_workload (
    faculty_id INT PRIMARY KEY,
    total_guide_assignments INT DEFAULT 0,
    total_evaluator_assignments INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
);

-- ================== BATCH PANEL CONFIGURATION (OPTIONAL) ==================

-- Optional: Store predefined panel members for each batch
CREATE TABLE batch_panels (
    panel_id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id INT,
    faculty_id INT,
    role ENUM('panel_member', 'chair') DEFAULT 'panel_member',
    
    FOREIGN KEY (batch_id) REFERENCES review_batches(batch_id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    UNIQUE KEY unique_faculty_batch (batch_id, faculty_id)
);

-- ================== INDEXES FOR PERFORMANCE ==================

-- Indexes for faster queries
CREATE INDEX idx_members_group ON members(group_id);
CREATE INDEX idx_assignments_batch ON batch_assignments(batch_id);
CREATE INDEX idx_assignments_group ON batch_assignments(group_id);
CREATE INDEX idx_faculty_name ON faculty(faculty_name);
CREATE INDEX idx_batches_date ON review_batches(review_date);

-- ================== SAMPLE DATA STRUCTURE ==================

-- Example of how the data flows:

-- 1. Faculty table contains all panel members:
INSERT INTO faculty (faculty_name, email) VALUES 
('Dr. Jyoti V. Surve', 'jyoti.surve@university.edu'),
('Prof. Monali P. Deshmukh', 'monali.deshmukh@university.edu'),
('Prof. Sourabh V. Natu', 'sourabh.natu@university.edu');

-- 2. Review batches represent the 7 tracks:
INSERT INTO review_batches (batch_name, review_date, review_time, location, room_no, track_id) VALUES
('Batch 1', '2025-08-15', '09:00:00', '213', 'Room 1', 1),
('Batch 2', '2025-08-15', '09:00:00', '214', 'Room 2', 2);

-- 3. Batch assignments link groups to faculty:
INSERT INTO batch_assignments (batch_id, group_id, guide_faculty_id, evaluator1_faculty_id, evaluator2_faculty_id, row_position) VALUES
(1, 'BIA-01', 1, 2, 3, 0),  -- Batch 1, Group BIA-01, Guide=Faculty1, Eval1=Faculty2, Eval2=Faculty3, Position 0
(1, 'BIB-01', 2, 1, 3, 1);  -- Batch 1, Group BIB-01, Guide=Faculty2, Eval1=Faculty1, Eval2=Faculty3, Position 1

-- ================== USEFUL VIEWS ==================

-- View to get complete schedule information
CREATE VIEW schedule_overview AS
SELECT 
    rb.batch_name,
    rb.location,
    rb.room_no,
    rb.review_date,
    rb.review_time,
    ba.group_id,
    ba.row_position,
    p.project_title,
    g.faculty_name as guide_name,
    e1.faculty_name as evaluator1_name,
    e2.faculty_name as evaluator2_name
FROM review_batches rb
JOIN batch_assignments ba ON rb.batch_id = ba.batch_id
JOIN projects p ON ba.group_id = p.group_id
LEFT JOIN faculty g ON ba.guide_faculty_id = g.faculty_id
LEFT JOIN faculty e1 ON ba.evaluator1_faculty_id = e1.faculty_id
LEFT JOIN faculty e2 ON ba.evaluator2_faculty_id = e2.faculty_id
ORDER BY rb.batch_name, ba.row_position;

-- View to get faculty workload summary
CREATE VIEW faculty_workload_summary AS
SELECT 
    f.faculty_name,
    f.email,
    fw.total_guide_assignments,
    fw.total_evaluator_assignments,
    (fw.total_guide_assignments + fw.total_evaluator_assignments) as total_assignments
FROM faculty f
LEFT JOIN faculty_workload fw ON f.faculty_id = fw.faculty_id
ORDER BY total_assignments DESC, f.faculty_name;

select * from schedule_overview;
select * from projects;


SET SQL_SAFE_UPDATES = 0;
UPDATE projects
SET group_id = REPLACE(TRIM(group_id), ' ', '')
WHERE group_id LIKE '% %';
SET SQL_SAFE_UPDATES = 1;


-- Trim whitespace/newlines in guide_name
UPDATE projects
SET guide_name = TRIM(REPLACE(REPLACE(guide_name, '\r', ''), '\n', ' '))
WHERE guide_name LIKE '%\n%' OR guide_name LIKE '%\r%' OR guide_name LIKE ' %' OR guide_name LIKE '% ';

-- Clean any remaining data issues
UPDATE projects 
SET group_id = REPLACE(REPLACE(group_id, ' ', ''), '--', '-')
WHERE group_id LIKE '% %' OR group_id LIKE '%-%-%';

-- Standardize guide names
UPDATE projects SET guide_name = 'Prof. Monali P. Deshmukh' WHERE guide_name LIKE '%Monali%Deshmukh%';
UPDATE projects SET guide_name = 'Prof. Deepika D. Walanjkar' WHERE guide_name LIKE '%Deepika%Walanjkar%';
UPDATE projects SET guide_name = 'Prof. Asawari Y. Bhalerao' WHERE guide_name LIKE '%Asawari%Bhalerao%';
UPDATE projects SET guide_name = 'Dr. Sonali S. Patil' WHERE guide_name LIKE '%Sonali%Patil%';
UPDATE projects SET guide_name = 'Prof. Priti V. Yampe' WHERE guide_name LIKE '%Priti%Yampe%';

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- Clean the group_id in projects table
UPDATE projects 
SET group_id = REPLACE(REPLACE(group_id, ' ', ''), '--', '-')
WHERE group_id LIKE '% %' OR group_id LIKE '%-%-%';

-- Update corresponding group_id in members table to match
UPDATE members 
SET group_id = REPLACE(REPLACE(group_id, ' ', ''), '--', '-')
WHERE group_id LIKE '% %' OR group_id LIKE '%-%-%';

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;
-- Add evaluator name columns to projects table
ALTER TABLE projects 
ADD COLUMN evaluator1_name TEXT,
ADD COLUMN evaluator2_name TEXT;

select * from projects;

-- Add schedule configuration table
CREATE TABLE schedule_config (
    config_id INT PRIMARY KEY AUTO_INCREMENT,
    batch_number INT,
    batch_name VARCHAR(50),
    group_ids JSON,
    panel_faculty JSON,
    location VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from projects;

-- Update projects table to include all fields
ALTER TABLE projects 
ADD COLUMN division VARCHAR(10),
ADD COLUMN project_domain TEXT,
ADD COLUMN sponsor_company TEXT;

-- Create panel_assignments table if it doesn't exist
CREATE TABLE IF NOT EXISTS panel_assignments (
    group_id VARCHAR(50) PRIMARY KEY,
    track INT,
    panel_professors TEXT,
    location VARCHAR(255),
    guide VARCHAR(255),
    reviewer1 VARCHAR(255),
    reviewer2 VARCHAR(255),
    reviewer3 VARCHAR(255),
    FOREIGN KEY (group_id) REFERENCES projects(group_id) ON DELETE CASCADE
);
SELECT * FROM projects;
-- Check projects table
SELECT COUNT(*) FROM projects;
SELECT group_id, division FROM projects ORDER BY group_id;

-- Check panel_assignments table  
SELECT COUNT(*) FROM panel_assignments;
SELECT track, COUNT(*) as count FROM panel_assignments GROUP BY track ORDER BY track;
SELECT group_id, track FROM panel_assignments ORDER BY track, group_id;

SELECT track, COUNT(*) as group_count 
FROM panel_assignments 
GROUP BY track 
ORDER BY track;

-- Find projects with missing evaluator assignments
SELECT 
    group_id, 
    division, 
    project_title,
    evaluator1_name,
    evaluator2_name,
    CASE WHEN evaluator1_name IS NULL OR TRIM(evaluator1_name) = '' THEN 'MISSING' ELSE 'OK' END as eval1_status,
    CASE WHEN evaluator2_name IS NULL OR TRIM(evaluator2_name) = '' THEN 'MISSING' ELSE 'OK' END as eval2_status
FROM projects 
WHERE evaluator1_name IS NULL OR TRIM(evaluator1_name) = '' 
   OR evaluator2_name IS NULL OR TRIM(evaluator2_name) = ''
ORDER BY division, group_id;

-- Get comprehensive evaluator assignment statistics
SELECT 
    division,
    COUNT(*) as total_projects,
    COUNT(CASE WHEN evaluator1_name IS NOT NULL AND TRIM(evaluator1_name) != '' THEN 1 END) as with_evaluator1,
    COUNT(CASE WHEN evaluator2_name IS NOT NULL AND TRIM(evaluator2_name) != '' THEN 1 END) as with_evaluator2,
    COUNT(CASE WHEN (evaluator1_name IS NOT NULL AND TRIM(evaluator1_name) != '') 
               AND (evaluator2_name IS NOT NULL AND TRIM(evaluator2_name) != '') THEN 1 END) as with_both_evaluators,
    ROUND((COUNT(CASE WHEN (evaluator1_name IS NOT NULL AND TRIM(evaluator1_name) != '') 
                          AND (evaluator2_name IS NOT NULL AND TRIM(evaluator2_name) != '') THEN 1 END) * 100.0 / COUNT(*)), 2) as completion_percentage
FROM projects
GROUP BY division
ORDER BY division;

SELECT
    p.group_id,
    p.division,
    p.project_title,
    p.guide_name,
    -- CRITICAL: Fetch evaluators from projects table (where data_manager.py stores them)
    p.evaluator1_name as evaluator1,
    p.evaluator2_name as evaluator2,
    -- Panel assignment data
    COALESCE(pa.track, 'Unassigned') as track,
    COALESCE(pa.panel_professors, '') as panel_professors,
    COALESCE(pa.location, 'TBD') as location,
    COALESCE(pa.guide, p.guide_name, 'TBD') as assigned_guide,
    -- Debug fields to verify data
    CASE 
        WHEN p.evaluator1_name IS NOT NULL AND TRIM(p.evaluator1_name) != '' THEN 1
        ELSE 0
    END as has_evaluator1,
    CASE 
        WHEN p.evaluator2_name IS NOT NULL AND TRIM(p.evaluator2_name) != '' THEN 1
        ELSE 0
    END as has_evaluator2,
    -- Additional fields for completeness
    p.project_domain,
    p.sponsor_company
FROM projects p
LEFT JOIN panel_assignments pa ON p.group_id = pa.group_id
ORDER BY
    CASE
        WHEN pa.track IS NULL THEN 999
        WHEN pa.track = '' THEN 999
        ELSE CAST(pa.track AS UNSIGNED)
    END,
    p.division,
    p.group_id;

use project_review;
show tables;

