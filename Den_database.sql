

USE den_sys;

CREATE TABLE department (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE student (
    roll_no VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

CREATE TABLE timetable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    day_of_week ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    subject VARCHAR(100) NOT NULL,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

CREATE TABLE den_entry_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL,
    status VARCHAR(10) NOT NULL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (roll_no) REFERENCES student(roll_no)
);

INSERT INTO department (department_name) VALUES
    ('Computer Engineering'),
    ('Mechanical Engineering'),
    ('Electronics Engineering');

INSERT INTO student (roll_no, name, department_id) VALUES
    ('CS2024001', 'Aarav Shah', 1),
    ('ME2024001', 'Rohan Patil', 2),
    ('EC2024001', 'Sanika Joshi', 3);

INSERT INTO timetable (department_id, day_of_week, start_time, end_time, subject) VALUES
    (1, 'Monday',    '09:00:00', '10:00:00', 'Data Structures'),
    (1, 'Monday',    '10:00:00', '11:00:00', 'Operating Systems'),
    (2, 'Monday',    '09:00:00', '10:30:00', 'Thermodynamics'),
    (3, 'Monday',    '11:00:00', '12:00:00', 'Digital Circuits');
    
select * from timetable;

insert into timetable (department_id, day_of_week, start_time, end_time, subject) VALUES
    (1,'Monday', '16:00:00', '17:00:00', 'MDM');
    

    
