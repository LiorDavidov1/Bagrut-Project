# Project: Library Loan System

## Developer: Lior Davidov

### Introduction

This project was developed as a final project to manage a school library loan system. It supports book loan tracking, extension requests, and user interaction with a librarian. The system integrates user (admin or student) authentication, secure password hashing, role-based dashboards, and communication with a centralized database that stores student information, loan records, and book details.

## Import the Project

- You can import the project by downloading it or using those commands:
```
cd <directory_you_want>
git clone https://github.com/LiorDavidov1/Bagrut-Project.git
```

## Getting Started

### Step 1: Launch the Login System

Start the login GUI by running:
```
app.py
```
Enter an existing user's login details.

Based on your role (student/admin), the appropriate dashboard will open.

### Step 2: Use Admin Functionalities (if logged in as an admin)

#### Admins can:

Manage loans details for each student:

- Accessible using the dashboard (button: "Edit Books & Due Date")

View all registered students data:

- Accessible using the dashboard (button: "View All Registered Students")

### Step 3: Student Functionalities

#### Students can:

View their profile, view loaned books details, and request extension.

Click “Request Extension” to:

- Add notes to your request

- Request extension to the librarian (If you have the right to do that)

## Security Notes

The system includes a set of measures to ensure safety of user data and authentication:

- Password protection: All user passwords are securely hashed with bcrypt before being saved to the Access database.

- Brute Force defense: The system introduces a 10-second delay after each failed login attempt, making repeated guessing attempts significantly slower.

- SQL injection prevention: The system is using parameterized queries, ensuring that user input is safely handled and not directly executed as part of SQL commands.

- Network Communication: While the current system uses basic TCP sockets for communication between client and server, this can be extended to include TLS encryption for enhanced security in production environments.

## Libraries

This project uses several standard and third-party Python libraries:

| Library        | Purpose                                                                            |
|----------------|------------------------------------------------------------------------------------|
| `socket`       | Communicates between the server and clients using the TCP/IP protocol.     |
| `threading`       | Multi-process management, allowing the server to handle multiple requests simultaneously in an efficient manner.                     |
| `tkinter`      | GUI framework for login, menus, and admin dashboard     |
| `PIL` (Pillow) | Load and display user photos                            |
| `bcrypt`       | Hash and verify passwords securely                      |
| `requests`     | API requests to the Nutritionix service                 |
| `googletrans`  | Translate API food data into Hebrew                     |
| `googletrans`  | Translate API food data into Hebrew                     |
| `googletrans`  | Translate API food data into Hebrew                     |
| `googletrans`  | Translate API food data into Hebrew                     |
| `googletrans`  | Translate API food data into Hebrew                     |
| `googletrans`  | Translate API food data into Hebrew                     |
| `googletrans`  | Translate API food data into Hebrew                     |
| `googletrans`  | Translate API food data into Hebrew                     |
| `googletrans`  | Translate API food data into Hebrew                     |

