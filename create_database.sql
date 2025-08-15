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
