import pyodbc
from datetime import *
import smtplib
import ssl
from email.message import EmailMessage
import bcrypt
import time
import re
import logging


def is_strong_password(password):
   if len(password) < 8:
       return False
   if not re.search(r"[A-Z]", password):
       return False
   if not re.search(r"[a-z]", password):
       return False
   if not re.search(r"[0-9]", password):
       return False
   if not re.search(r"[\W_]", password):
       return False
   return True


class ServerHandler:
   def __init__(self, dsn=r'DSN=MyAccessDB;'):
       self.dsn = dsn
       # Email sender credentials
       self.email_sender = "librarianhava@gmail.com"
       self.email_password = "hxxelnjrnzxlkcfd"


   def send_email(self, to_email, subject, message):
       try:
           logging.info(f"Sending email to {to_email} with subject '{subject}'")
           em = EmailMessage()
           em['From'] = self.email_sender
           em['To'] = to_email
           em['Subject'] = subject
           em.set_content(message)


           context = ssl.create_default_context()
           with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
               smtp.login(self.email_sender, self.email_password)
               smtp.send_message(em)
           logging.info("Email sent successfully!")
           return {"success": True}
       except Exception as e:
           logging.info(f"Failed to send email: {str(e)}")
           return {"error": f"Email failed: {str(e)}"}


   def request_extension(self, student_id, message):
       if not message.strip():
           return {"error": "Extension notes cannot be empty."}


       try:
           conn = pyodbc.connect(self.dsn)
           cursor = conn.cursor()


           cursor.execute("SELECT COUNT(*) FROM Loans WHERE ID = ?", (student_id,))
           loan_count = cursor.fetchone()[0]
           if loan_count == 0:
               return {"error": "You have no loaned books, so you cannot request an extension."}


           # Get student info
           cursor.execute('SELECT FirstName, LastName, ID, PhoneNumber, EmailAddress FROM students WHERE ID = ?', (student_id,))
           row = cursor.fetchone()
           if not row:
               return {"error": "Student not found"}


           full_name = f"{row[0]} {row[1]}"
           user_id = row[2]
           phone = row[3]
           email = row[4]


           full_message = (
               f"Extension request from: {full_name}\n"
               f"ID: {user_id}\n"
               f"Email: {email}\n"
               f"Phone Number: {phone}\n\n"
               f"Notes:\n{message}"
           )


           # Update DB
           cursor.execute("UPDATE Loans SET ExtensionRequested = True WHERE ID = ?", (student_id,))
           conn.commit()


           # Send email
           email_result = self.send_email(
               "librarianhava@gmail.com",
               "Library Extension Request",
               full_message
           )
           if "error" in email_result:
               return email_result
           return {"success": True}
       except pyodbc.Error as e:
           return {"error": str(e)}


   def check_login(self, user_id, password):
       try:
           conn = pyodbc.connect(self.dsn)
           cursor = conn.cursor()
           cursor.execute('SELECT Password, IsAdmin FROM students WHERE ID = ?', (user_id,))
           row = cursor.fetchone()
           if row:
               stored_hashed_pw, is_admin = row
               if bcrypt.checkpw(password.encode(), stored_hashed_pw.encode()):
                   return {"success": True, "is_admin": is_admin}
               else:
                   # Delay to slow down brute-force attacks
                   time.sleep(10)
                   return {"success": False, "error": "Incorrect password."}
           else:
               # Delay if user ID not found
               time.sleep(10)
               return {"success": False, "error": "User not found."}
       except pyodbc.Error as e:
           return {"error": str(e)}


   def get_loans(self, student_id):
       try:
           conn = pyodbc.connect(self.dsn)
           cursor = conn.cursor()
           cursor.execute("SELECT BookName, Author, DueDate, ExtensionRequested FROM Loans WHERE ID = ?",
                          (student_id,))
           rows = cursor.fetchall()
           loans = [{
               "book": r[0],
               "author": r[1],
               "due_date": str(r[2]),
               "extension_requested": bool(r[3])
           } for r in rows]
           return {"loans": loans}
       except pyodbc.Error as e:
           return {"error": str(e)}


   def get_user_info(self, user_id):
       try:
           conn = pyodbc.connect(self.dsn)
           cursor = conn.cursor()
           cursor.execute('SELECT FirstName, LastName, ID FROM students WHERE ID = ?', (user_id,))
           row = cursor.fetchone()
           if row:
               return {"firstname": row[0], "lastname": row[1], "id": row[2]}
           else:
               return {"error": "User not found"}
       except pyodbc.Error as e:
           return {"error": str(e)}


   def register_student(self, student_data):
       # Basic validation
       if not all(student_data.values()):
           return {"error": "All fields are required!"}
       if not student_data["id"].isdigit():
           return {"error": "ID must be numeric."}
       if not student_data["phone"].isdigit():
           return {"error": "Phone must be numeric."}
       if not re.match(r"[^@]+@[^@]+\.[^@]+", student_data["email"]):
           return {"error": "Invalid email format."}
       if not is_strong_password(student_data["password"]):
           return {
               "error": "Password too weak. Use at least 8 characters, including uppercase, lowercase, number, and special character."
           }




       hashed_pw = bcrypt.hashpw(student_data["password"].encode(), bcrypt.gensalt()).decode()


       # Insert to DB
       try:
           conn = pyodbc.connect(self.dsn)
           cursor = conn.cursor()
           cursor.execute("SELECT ID FROM students WHERE ID = ?", (student_data["id"],))
           if cursor.fetchone() is not None:
               return {"error": "A user with this ID already exists. Please use a different ID."}
           cursor.execute(
               'INSERT INTO students (FirstName, LastName, ID, PhoneNumber, EmailAddress, Password) VALUES (?, ?, ?, ?, ?, ?)',
               (
                   student_data["firstname"],
                   student_data["lastname"],
                   student_data["id"],
                   student_data["phone"],
                   student_data["email"],
                   hashed_pw
               )
           )
           conn.commit()
           return {"success": True}
       except pyodbc.Error as e:
           return {"error": str(e)}


   def get_all_students(self):
       try:
           conn = pyodbc.connect(self.dsn)
           cursor = conn.cursor()
           cursor.execute("SELECT ID, FirstName, LastName, EmailAddress, PhoneNumber FROM students WHERE IsAdmin = False")
           rows = cursor.fetchall()
           students = [
               {
                   "id": r[0],
                   "firstname": r[1],
                   "lastname": r[2],
                   "email": r[3],
                   "phone": r[4]
               }
               for r in rows
           ]
           return {"students": students}
       except pyodbc.Error as e:
           return {"error": str(e)}


   def update_loans(self, student_id, books_authors, due_date):
       try:
           datetime.strptime(due_date, "%Y-%m-%d")
       except ValueError:
           return {"error": "Invalid date format. Use YYYY-MM-DD."}


       try:
           conn = pyodbc.connect(self.dsn)
           cursor = conn.cursor()
           cursor.execute("DELETE FROM Loans WHERE ID = ?", (student_id,))
           for item in books_authors:
               book = item["book"]
               author = item["author"]
               if book.strip() == "" and author.strip() == "":
                   continue
               cursor.execute(
                   "INSERT INTO Loans (ID, BookName, Author, DueDate, ExtensionRequested) VALUES (?, ?, ?, ?, False)",
                   (student_id, book, author, due_date)
               )
           conn.commit()
           return {"success": True}
       except pyodbc.Error as e:
           return {"error": str(e)}