# Smart Den Management System 

## Overview

The **Smart Den Management System** is a web-based application designed to manage student access and indoor recreational activities within a college Den.

The system verifies students using their roll numbers and checks their department's timetable to determine whether they have an ongoing lecture. If a lecture is in progress, access is denied. Otherwise, the student can proceed to use the Den's indoor sports facilities or rent available equipment.

The application also maintains entry records, manages activity capacities, tracks active sessions and provides an administrative interface for managing college data and viewing usage reports.

## Objectives

- Prevent students from accessing the Den during their scheduled lectures.
- Automate student verification using roll numbers.
- Maintain records of accepted and denied entry attempts.
- Manage indoor sports activities and their occupancy limits.
- Track equipment rentals and student activity sessions.
- Provide administrators with tools to manage students, departments and timetables.
- Generate reports to monitor Den usage.

## Key Features

### Student Entry Verification
- Students enter their roll number to begin verification.
- The system retrieves their details and department.
- The department timetable is checked against the current day and time.
- Access is allowed or denied based on the timetable.
- Entry decisions are recorded in the database.

### Activity Management
- Students can select available indoor activities.
- Activity capacity is checked before confirming participation.
- Current occupancy is updated when an activity session starts.
- Occupancy is reduced when a student checks out.

### Equipment Rental
- Students can select equipment to rent.
- Rental duration can be specified.
- Rental sessions are recorded and tracked.

### Session Management
- Active activity and rental sessions are maintained.
- Students can view their active session information.
- Remaining session time is calculated.
- Sessions are marked as completed during checkout.

### Admin Dashboard
- View general entry logs.
- View detailed activity and rental records.
- Access monthly visitor statistics.
- View student-wise monthly visit statistics.
- Add, view, update and delete student records.
- Add, view and delete timetable entries.
- Add, view and delete department records.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language and application logic |
| Flask | Backend web framework and request handling |
| MySQL | Relational database management |
| HTML | Webpage structure |
| CSS | Styling and interface design |
| JavaScript | Frontend interactions and communication with Flask |

## Database Design

The system uses six main tables:

| Table | Description |
|---|---|
| `department` | Stores department IDs and department names. |
| `student` | Stores student roll numbers, names and department references. |
| `timetable` | Stores department-wise lecture schedules. |
| `den_entry_log` | Records student entry attempts, their status and timestamps. |
| `activity_limit` | Stores activity capacity limits and current occupancy. |
| `activity_session` | Records student activities and equipment rental sessions. |

The database uses primary keys and foreign keys to identify records and establish relationships between related tables.

The ER model primarily uses one-to-many relationships, such as Department–Student, Department–Timetable and Student–Entry Log.

## System Workflow

1. A student enters their roll number through the website.
2. Flask receives the request and retrieves the student's details from MySQL.
3. The system identifies the student's department.
4. The corresponding timetable is checked for an ongoing lecture.
5. Access is accepted or denied based on the timetable.
6. If access is permitted, the student can select an activity or rent equipment.
7. The system checks activity capacity where applicable and creates an activity or rental session.
8. Entry records and session details are maintained in the database.
9. Administrators can access logs, reports and data-management features through the admin interface.

## Conclusion

The Smart Den Management System provides a centralized and automated approach to managing student access and recreational activities within a college Den.

By combining timetable-based entry verification, activity capacity management, equipment rentals and administrative reporting, the system aims to improve the organization and monitoring of Den facilities.

The project also demonstrates the practical application of database concepts such as relational database design, primary keys, foreign keys, SQL queries, joins, constraints and data management through a web-based application.

## Future Enhancements

- QR code or RFID-based student identification.
- Integration with the college's official student information system.
- Real-time activity availability updates.
- More detailed occupancy and usage analytics.
- Improved authentication and role-based administrator access.
- Automated notifications for session expiry and activity availability.

---

**Project:** Smart Den Management System  
**Domain:** Database Management Systems / Web Development  
**Backend:** Python Flask  
**Database:** MySQL  
**Frontend:** HTML, CSS and JavaScript
