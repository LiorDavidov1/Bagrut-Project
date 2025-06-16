import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import tkinter.ttk as ttk
from client_handler import ClientHandler

class AdminDashboard:
   def __init__(self, master):
       self.master = master
       self.master.title("Admin Dashboard")
       self.master.geometry("800x600")
       self.client = ClientHandler()
       self.admin_page()


   def admin_page(self):
       tk.Label(self.master, text="Admin Dashboard", font=("Arial", 16, "bold")).pack(pady=10)
       tk.Button(self.master, text="Edit Books & Due Date", width=30, command=self.edit_loans).pack(pady=5)
       tk.Button(self.master, text="View All Registered Students", width=30, command=self.view_students).pack(pady=5)
       tk.Button(self.master, text="Exit", command=self.master.destroy).pack(pady=10)


   def edit_loans(self):
       edit_window = tk.Toplevel(self.master)
       edit_window.title("Edit Books & Due Date")
       edit_window.geometry("800x600")


       response = self.client.send_request({"command": "get_all_students"})
       if "error" in response:
           messagebox.showerror("Error", response["error"])
           return
       students = response["students"]


       tk.Label(edit_window, text="Select Student:", font=("Arial", 12)).pack(pady=5)
       student_var = tk.StringVar()
       student_dropdown = tk.OptionMenu(edit_window, student_var,
                                        *[f"{s['id']}: {s['firstname']} {s['lastname']}" for s in students])
       student_dropdown.pack(pady=5)


       form_frame = tk.Frame(edit_window, bg="white", bd=2, relief=tk.SOLID)
       form_frame.pack(padx=10, pady=10, fill="both", expand=True)


       entries = []
       for i in range(4):
           row = tk.Frame(form_frame, bg="white")
           row.pack(pady=5)
           tk.Label(row, text=f"Book {i + 1}:", bg="white").pack(side="left", padx=5)
           book_entry = tk.Entry(row, width=30)
           book_entry.pack(side="left", padx=5)
           author_entry = tk.Entry(row, width=30)
           author_entry.pack(side="left", padx=5)
           entries.append((book_entry, author_entry))


       tk.Label(form_frame, text="Due Date (DD-MM-YYYY):", bg="white").pack(pady=5)
       due_date_entry = tk.Entry(form_frame, width=20)
       due_date_entry.pack(pady=5)


       def load_loans():
           selected = student_var.get()
           if not selected:
               return
           student_id = int(selected.split(":")[0])
           response = self.client.send_request({"command": "get_loans", "student_id": student_id})
           if "error" in response:
               messagebox.showerror("Error", response["error"])
               return
           loans = response["loans"]
           for book_entry, author_entry in entries:
               book_entry.delete(0, tk.END)
               author_entry.delete(0, tk.END)
           due_date = None
           for i, loan in enumerate(loans):
               book_entry, author_entry = entries[i]
               book_entry.insert(0, loan["book"])
               author_entry.insert(0, loan["author"])
               due_date = loan["due_date"].split(" ")[0] if loan["due_date"] else ""
           if due_date:
               due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
               due_date_formatted = due_date_obj.strftime("%d-%m-%Y")
               due_date_entry.delete(0, tk.END)
               due_date_entry.insert(0, due_date_formatted)


       def save_changes():
           selected = student_var.get()
           if not selected:
               messagebox.showerror("Error", "Please select a student.")
               return
           student_id = int(selected.split(":")[0])
           try:
               due_date = datetime.strptime(due_date_entry.get(), "%d-%m-%Y").strftime("%Y-%m-%d")
           except:
               messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYY.")
               return
           books_authors = [{"book": be.get().strip(), "author": ae.get().strip()} for be, ae in entries]
           response = self.client.send_request({
               "command": "update_loans",
               "student_id": student_id,
               "books_authors": books_authors,
               "due_date": due_date
           })
           if "error" in response:
               messagebox.showerror("Error", response["error"])
           else:
               messagebox.showinfo("Success", "Books and due date updated.")


       tk.Button(edit_window, text="Load Student's Loans", command=load_loans).pack(pady=5)
       tk.Button(edit_window, text="Save Changes", command=save_changes).pack(pady=5)
       tk.Button(edit_window, text="Back", command=edit_window.destroy).pack(pady=10)


   def view_students(self):
       view_window = tk.Toplevel(self.master)
       view_window.title("All Registered Students")
       view_window.geometry("1000x500")


       response = self.client.send_request({"command": "get_all_students"})
       if "error" in response:
           messagebox.showerror("Error", response["error"])
           return


       students = response["students"]


       columns = ("ID", "First Name", "Last Name", "Email", "Phone", "Due Date")
       tree = ttk.Treeview(view_window, columns=columns, show="headings")
       for col in columns:
           tree.heading(col, text=col)
           tree.column(col, width=160)


       for student in students:
           loans_response = self.client.send_request({
               "command": "get_loans",
               "student_id": student["id"]
           })
           if "error" in loans_response:
               due_date = "Error"
           else:
               loans = loans_response["loans"]
               if loans:
                   due_date_str = loans[0]["due_date"].split(" ")[0] if loans[0]["due_date"] else "N/A"
                   if due_date_str != "N/A":
                       # Format the date as DD-MM-YYYY
                       due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d")
                       due_date = due_date_obj.strftime("%d-%m-%Y")
                   else:
                       due_date = "N/A"
               else:
                   due_date = "N/A"


           tree.insert("", tk.END, values=(
               student["id"],
               student["firstname"],
               student["lastname"],
               student["email"],
               student["phone"],
               due_date
           ))


       tree.pack(fill="both", expand=True, padx=10, pady=10)
       tk.Button(view_window, text="Back", bg="#dc3545", fg="white", command=view_window.destroy).pack(pady=10)