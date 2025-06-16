import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from admin import AdminDashboard
from client_handler import ClientHandler

class LibraryLoanApp:
   def __init__(self, root):
       self.root = root
       self.root.title("Library Loan System")
       self.root.geometry("700x600")
       self.root.configure(bg="#f4f4f4")


       self.client = ClientHandler()
       self.current_user = None


       self.login_screen()


   def login_screen(self):
       for widget in self.root.winfo_children():
           widget.destroy()


       tk.Label(self.root, text="Library Login", font=("Arial", 14, "bold"), bg="#f4f4f4").pack(pady=10)
       tk.Label(self.root, text="ID:", bg="#f4f4f4").pack()
       self.id_entry = tk.Entry(self.root)
       self.id_entry.pack()


       tk.Label(self.root, text="Password:", bg="#f4f4f4").pack()
       self.password_entry = tk.Entry(self.root, show="*")
       self.password_entry.pack()


       tk.Button(self.root, text="Login", command=self.login, bg="green", fg="white", padx=10, pady=5).pack(pady=10)
       tk.Button(self.root, text="Sign Up", command=self.signup_screen, bg="cyan", fg="white", padx=10, pady=5).pack()
       tk.Button(self.root, text="Exit", command=self.root.destroy, bg="red", fg="white", padx=10, pady=5).pack(pady=10)


   def login(self):
       try:
           user_id = int(self.id_entry.get())
       except ValueError:
           messagebox.showerror("Error", "ID must be a number")
           return


       password = self.password_entry.get()
       response = self.client.send_request({
           "command": "check_login",
           "user_id": user_id,
           "password": password
       })
       if response.get("success"):
           self.current_user = user_id
           is_admin = response.get("is_admin")
           if str(is_admin).lower() in ["yes", "true"]:
               self.root.destroy()
               admin_root = tk.Tk()
               AdminDashboard(admin_root)
               admin_root.mainloop()
           else:
               self.main_page()
       else:
           error_msg = response.get("error") or "ID and Password do not match."
           messagebox.showerror("Error", error_msg)


   def signup_screen(self):
       for widget in self.root.winfo_children():
           widget.destroy()


       tk.Label(self.root, text="Library Signup", font=("Arial", 14, "bold"), bg="#f4f4f4").pack(pady=10)
       fields = ["First Name", "Last Name", "ID", "Phone Number", "Email", "Password", "Confirm Password"]
       self.signup_entries = {}


       for field in fields:
           tk.Label(self.root, text=field + ":", bg="#f4f4f4").pack()
           entry = tk.Entry(self.root, show="*" if "Password" in field else None)
           entry.pack()
           self.signup_entries[field.lower().replace(" ", "_")] = entry


       tk.Button(self.root, text="Register", command=self.register, bg="cyan", fg="white").pack(pady=10)
       tk.Button(self.root, text="Back to Login", command=self.login_screen, bg="green", fg="white").pack()
   def register(self):
       pw = self.signup_entries["password"].get()
       confirm_pw = self.signup_entries["confirm_password"].get()
       if pw != confirm_pw:
           messagebox.showerror("Error", "Passwords do not match!")
           return


       student_data = {
           "firstname": self.signup_entries["first_name"].get(),
           "lastname": self.signup_entries["last_name"].get(),
           "id": self.signup_entries["id"].get(),
           "phone": self.signup_entries["phone_number"].get(),
           "email": self.signup_entries["email"].get(),
           "password": pw
       }


       response = self.client.send_request({
           "command": "register_student",
           "student_data": student_data
       })
       if response.get("success"):
           messagebox.showinfo("Success", "Account created successfully!")
           self.login_screen()
       else:
           messagebox.showerror("Error", response.get("error", "Unknown error"))


   def main_page(self):
       for widget in self.root.winfo_children():
           widget.destroy()


       response = self.client.send_request({
           "command": "get_user_info",
           "user_id": self.current_user
       })
       if "error" in response:
           messagebox.showerror("Error", response["error"])
           return
       user_info = response


       welcome_name = user_info["firstname"] if user_info else self.current_user


       tk.Label(self.root, text=f"Welcome {welcome_name}", font=("Arial", 14, "bold"), bg="#f4f4f4").pack(pady=10)
       self.frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief=tk.GROOVE)
       self.frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)


       response = self.client.send_request({
           "command": "get_loans",
           "student_id": self.current_user
       })
       if "error" in response:
           messagebox.showerror("Error", response["error"])
           return
       loans = response["loans"]
       for loan in reversed(loans):
           due_date_str = loan["due_date"].split(" ")[0]
           due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d")
           due_date_formatted = due_date_obj.strftime("%d-%m-%Y")
           title, author, due_date = loan["book"], loan["author"], loan["due_date"].split(" ")[0]
           tk.Label(self.frame, text=f"{title} by {author} - Due: {due_date_formatted}", font=("Arial", 10),
                    bg="#ffffff", pady=5).pack(anchor="w", padx=10, pady=2)


       self.request_extension_button = tk.Button(self.root, text="Request Extension", font=("Arial", 12, "bold"),
                                                 bg="#007BFF", fg="white", command=self.show_extension_box)
       self.request_extension_button.pack(pady=10)


   def show_extension_box(self):
       # Disable the button to prevent multiple clicks
       if hasattr(self, "request_extension_button"):
           self.request_extension_button.config(state="disabled")


       # Check if extension already requested
       response = self.client.send_request({
           "command": "get_loans",
           "student_id": self.current_user
       })
       if "error" in response:
           messagebox.showerror("Error", response["error"])
           return


       extension_already_requested = any(
           loan.get("extension_requested", False)
           for loan in response["loans"]
       )


       if extension_already_requested:
           messagebox.showwarning("Extension Already Requested",
                                  "You have already requested an extension for your loan(s).")
           return


       # Show the notes textbox
       self.notes_label = tk.Label(self.root, text="Notes:", bg="#f4f4f4", font=("Arial", 10, "bold"))
       self.notes_label.pack()
       self.extension_textbox = tk.Text(self.root, height=4, width=40)
       self.extension_textbox.pack(pady=5)
       self.submit_button = tk.Button(self.root, text="Submit Request", bg="#28a745", fg="white",
                                      command=self.send_extension_request)
       self.submit_button.pack(pady=5)


   def send_extension_request(self):
       if not hasattr(self, "extension_textbox") or not self.extension_textbox.winfo_exists():
           messagebox.showerror("Error", "Extension request textbox does not exist.")
           return


       message = self.extension_textbox.get("1.0", tk.END).strip()
       if not message:
           messagebox.showerror("Empty", "Please enter a message for the extension request.")
           return


       response = self.client.send_request({
           "command": "request_extension",
           "student_id": self.current_user,
           "message": message
       })


       if "error" in response:
           messagebox.showerror("Error", response["error"])
       else:
           messagebox.showinfo("Request Sent", "Your extension request has been sent.")
           self.extension_textbox.delete("1.0", tk.END)
           self.submit_button.config(state="disabled")
