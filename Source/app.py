import tkinter as tk
from student import LibraryLoanApp


if __name__ == "__main__":
   root = tk.Tk()
   app = LibraryLoanApp(root)
   root.mainloop()