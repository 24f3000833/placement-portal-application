# Placement Portal System

## Overview

The Placement Portal System is a web-based application designed to streamline the campus recruitment process within an educational institution. The system provides a centralized platform where students can apply for job opportunities, companies can post placement drives, and administrators can manage and monitor the entire recruitment process efficiently.

The portal simplifies communication between students and recruiters and helps institutes manage placement activities digitally.



## Features

### Student Module

* Student registration and login
* Upload resume and personal details
* View available placement drives
* Apply for placement opportunities
* Track application status

### Company Module

* Company registration and login
* Upload company details and verification certificate
* Post placement drives
* View student applications for posted drives
* Manage recruitment process

### Admin Module

* Approve or reject company registrations
* Manage students and companies
* Monitor placement drives
* View all applications submitted by students
* Blacklist companies or students if required



## Technologies Used

### Frontend

* HTML
* CSS
* Jinja2 Template Engine

### Backend

* Python
* Flask Web Framework

### Database

* SQLite
* SQLAlchemy ORM

### Security

* Password hashing using Werkzeug


## Database Entities

The system consists of the following main entities:

* **Admin**
* **Student**
* **Company**
* **Placement Drive**
* **Application**

### Relationship Summary

* A company can create multiple placement drives.
* A student can apply to multiple placement drives.
* Each application connects a student with a placement drive.
* The Application table acts as a junction table to resolve the many-to-many relationship between students and placement drives.



## Project Structure

```
Placement_Portal/
│
├── app.py
├── models.py
├── init_db.py
├── requirements.txt
├── README.md
│
├── static/
│   ├── css/
│   │   ├── global.css
│   │   ├── auth.css
│   │   ├── home.css
│   │   
│   └── upload/
│
└── templates/
    ├── base.html
    ├── home.html
    ├── auth/
    │   ├── login.html
    │   ├── admin_login.html
    │   ├── register_student.html
    │   └── register_company.html
    ├── student/
    │   ├── dashboard.html
    │   ├── profile.html
    │   ├── applications.html
    │   └── drive_detail.html
    ├── company/
    │   ├── dashboard.html
    │   ├── create_drive.html
    │   ├── edit_drive.html
    │   ├── applicants.html
    │   └── review_application.html
    └── admin/
        ├── admin_dashboard.html
        ├── student_detail.html
        ├── company_detail.html
        ├── drive_detail.html
```

## Installation and Setup

### 1. Clone the Repository


git clone https://github.com/24f3000833/placement-portal-application.git


### 2. Install Dependencies

pip install -r requirements.txt

### 3. Initialize the Database

python init_db.py

### 4. Run the Application

python app.py

### 5. Open in Browser

http://127.0.0.1:5000



## Future Enhancements

* Email notification system for students
* Resume filtering based on eligibility
* Interview scheduling system
* Analytics dashboard for placement statistics
* Advanced search and filtering for placement drives


## Author

Developed by **Anshul Pandey**


## License

This project is developed for educational purposes as part of an academic submission.
