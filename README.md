# Elderly & Disabled Helping System

A simple, accessible web application that connects elderly and disabled people with helpers who can assist them with daily needs. Built as a college-level academic project demonstrating frontend, backend, and database integration.

## Project Description

This system allows three types of users:

- **Elderly / Disabled Users** — Request help with daily activities
- **Helpers / Caregivers** — View and accept help requests
- **Administrators** — Manage users and requests

The interface is designed with accessibility in mind: large buttons, readable fonts, high contrast, and simple navigation.

## Features

- User registration and login with role-based access
- Create help requests with 8 assistance categories
- Emergency SOS button for urgent help requests
- Helper dashboard to accept and complete requests
- Admin panel with statistics and management tools
- Responsive design for desktop and mobile browsers
- Password hashing and session-based authentication
- Accessible UI with large text and keyboard-friendly controls

## Technologies Used

| Layer      | Technology                    |
| ---------- | ----------------------------- |
| Frontend   | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Backend    | Python 3, Flask               |
| Database   | SQLite, SQLAlchemy            |

## Folder Structure

```
elderly_helping_system/
│
├── app.py                  # Main Flask application and routes
├── models.py               # Database models (User, HelpRequest)
├── requirements.txt        # Python dependencies
├── database.db             # SQLite database (created on first run)
│
├── templates/
│   ├── base.html           # Base layout template
│   ├── index.html          # Home page
│   ├── about.html          # About page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── user_dashboard.html # User dashboard
│   ├── create_request.html # Create help request
│   ├── my_requests.html    # User's request list
│   ├── request_details.html# Request detail view
│   ├── helper_dashboard.html
│   ├── available_requests.html
│   ├── accepted_requests.html
│   ├── completed_requests.html
│   ├── admin_dashboard.html
│   ├── users.html          # Admin: manage users
│   └── requests.html       # Admin: manage requests
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom accessible styles
│   └── js/
│       └── script.js       # Client-side enhancements
│
└── README.md
```

## Installation Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Navigate to the project folder:**

   ```bash
   cd elderly_helping_system
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   ```bash
   python app.py
   ```

4. **Open in browser:**

   Go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

The database is created automatically on first run with sample data.

## Default Admin Credentials

> **For development and testing only. Do not use in production.**

| Role  | Email              | Password   |
| ----- | ------------------ | ---------- |
| Admin | admin@example.com  | admin123   |

## Sample Test Accounts

| Role   | Email              | Password   |
| ------ | ------------------ | ---------- |
| User   | user@example.com   | user123    |
| Helper | helper@example.com | helper123  |

## Example User Workflow

1. Register as an **Elderly / Disabled User** (or login with `user@example.com`)
2. On the dashboard, click **"I Need Help"**
3. Select help type, describe the need, and enter location
4. Submit the request
5. View request status on **My Requests**
6. When a helper accepts, see their name and phone number
7. Use the **SOS / EMERGENCY** button for urgent help

## Example Helper Workflow

1. Register as a **Helper** (or login with `helper@example.com`)
2. View available requests on the dashboard
3. Click **Accept Request** on a request
4. Go to **Accepted Requests** and help the person
5. Click **Help Completed** when done
6. View completed requests in **Completed Requests**

## Help Request Types

1. Walking Assistance
2. Food Assistance
3. Medicine Assistance
4. Hospital Assistance
5. Shopping Assistance
6. Household Assistance
7. Reading Assistance
8. General Assistance

## Request Status Flow

```
Pending → Accepted → Completed
   ↓
Cancelled (by user)
```

## Security Notes

This is an academic project with basic security:

- Passwords are hashed using Werkzeug
- Flask sessions for authentication
- Role-based route protection
- Form validation on backend

For production use, additional security measures would be needed.

## License

This project is created for educational purposes.
