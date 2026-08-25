SET SQL_SAFE_UPDATES = 0;

CREATE DATABASE IF NOT EXISTS den_sys;
USE den_sys;

-- 1. Departments Table
CREATE TABLE IF NOT EXISTS department (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Students Table
CREATE TABLE IF NOT EXISTS student (
    roll_no VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

-- 3. Timetable Table
CREATE TABLE IF NOT EXISTS timetable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    day_of_week ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    subject VARCHAR(100) NOT NULL,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

-- 4. Entry Logs Table
CREATE TABLE IF NOT EXISTS den_entry_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL,
    status VARCHAR(10) NOT NULL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (roll_no) REFERENCES student(roll_no)
);

-- 5. Activity Limit Table
CREATE TABLE IF NOT EXISTS activity_limit (
    activity_name VARCHAR(50) PRIMARY KEY,
    max_capacity INT NOT NULL,
    current_count INT NOT NULL DEFAULT 0
);

-- 6. Activity and Equipment Rental Session Table
CREATE TABLE IF NOT EXISTS activity_session (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL,
    action_type ENUM('ACTIVITY', 'RENTAL') NOT NULL,
    activity_name VARCHAR(50),
    equipment_item VARCHAR(50),
    duration_hours INT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ACTIVE', 'COMPLETED') DEFAULT 'ACTIVE',
    FOREIGN KEY (roll_no) REFERENCES student(roll_no)
);

-- Seed Data: Departments
INSERT IGNORE INTO department (department_id, department_name) VALUES
    (1, 'Computer Engineering'),
    (2, 'Mechanical Engineering'),
    (3, 'Electronics Engineering');

-- Seed Data: Students
INSERT IGNORE INTO student (roll_no, name, department_id) VALUES
    ('CS2024001', 'Yash Latkar', 1),
    ('ME2024001', 'Rohan Patil', 2),
    ('EC2024001', 'Sanika Joshi', 3),
    ('CS2024006', 'Tanmay Gurram', 1),
    ('CS2024007', 'Atharva Atal', 1),
    ('CS2024008', 'Ayush Sohani', 1);

-- Seed Data: Timetable Schedule
INSERT INTO timetable (department_id, day_of_week, start_time, end_time, subject) VALUES
    (1, 'Monday',    '09:00:00', '10:00:00', 'Data Structures'),
    (1, 'Monday',    '10:00:00', '11:00:00', 'Microprocessors'), 
    (1, 'Monday',    '16:00:00', '18:00:00', 'MDM'),
    (2, 'Monday',    '09:00:00', '10:30:00', 'Thermodynamics'),
    (3, 'Monday',    '11:00:00', '12:00:00', 'Digital Circuits'),
    (1, 'Tuesday',   '11:00:00', '13:15:00', 'DBMS_lab'),
    (1, 'Tuesday',   '13:45:00', '15:45:00', 'DT'),
    (1, 'Wednesday', '09:00:00', '11:00:00', 'MP'),
    (1, 'Wednesday', '11:00:00', '13:15:00', 'AOA'),
    (1, 'Wednesday', '13:45:00', '14:45:00', 'EM3'),
    (1, 'Wednesday', '14:45:00', '15:45:00', 'DT'),
    (1, 'Thursday',  '09:00:00', '11:00:00', 'PS'),
    (1, 'Thursday',  '11:00:00', '13:15:00', 'AOA_lab'),
    (1, 'Thursday',  '13:45:00', '15:45:00', 'EM3'),
    (1, 'Friday',    '09:00:00', '15:45:00', 'MDM');

-- Seed Data: Activity Limits
INSERT INTO activity_limit (activity_name, max_capacity, current_count) VALUES
    ('Table Tennis', 2, 0),
    ('Carrom', 12, 0),
    ('Chess', 4, 0),
    ('PC Gaming', 6, 0),
    ('PS5 Gaming', 4, 0),
    ('Air Hockey', 2, 0)
ON DUPLICATE KEY UPDATE max_capacity = VALUES(max_capacity);

USE den_sys;

UPDATE activity_session 
SET status = 'COMPLETED' 
WHERE status = 'ACTIVE';

UPDATE activity_limit 
SET current_count = 0;


INSERT INTO student (roll_no, name, department_id) VALUES
    ('CS2024002', 'Prathamesh Guram', 1),
    ('CS2024003', 'Ashutosh Sharma', 1),
    ('CS2024004', 'Aditya Sigh', 1),
    ('CS2024005', 'Taha Gorme', 1),
    ('CS2024009', 'Raghav Vyas', 1),
    ('CS20240010', 'Ankur Kennedy', 1),
    ('CS20240011', 'Akash Parab', 1),
    ('CS20240012', 'Sahil Asawale', 1),
    ('CS20240013', 'Saujas Sawant', 1);
    
