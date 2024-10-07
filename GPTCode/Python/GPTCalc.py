import tkinter as tk
from tkinter import messagebox

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Dark Theme Calculator")
        master.configure(bg="#2E2E2E")  # Set the window background to dark gray

        # Entry widget to display expressions and results
        self.display = tk.Entry(master, width=35, borderwidth=5, font=('Arial', 18), bg="#1E1E1E", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=20, ipady=10)

        # Define button properties
        button_properties = {
            'bg': '#3C3C3C',          # Button background color
            'fg': '#FFFFFF',          # Button text color
            'activebackground': '#555555',  # Button background when clicked
            'activeforeground': '#FFFFFF',  # Button text when clicked
            'font': ('Arial', 14),
            'borderwidth': 0,
            'highlightthickness': 0,
        }

        # Define buttons with their respective texts and commands
        buttons = [
            {'text': '7', 'row': 1, 'column': 0, 'command': self.add_to_expression},
            {'text': '8', 'row': 1, 'column': 1, 'command': self.add_to_expression},
            {'text': '9', 'row': 1, 'column': 2, 'command': self.add_to_expression},
            {'text': '/', 'row': 1, 'column': 3, 'command': self.add_to_expression, 'bg': '#FF9500'},  # Orange for operators

            {'text': '4', 'row': 2, 'column': 0, 'command': self.add_to_expression},
            {'text': '5', 'row': 2, 'column': 1, 'command': self.add_to_expression},
            {'text': '6', 'row': 2, 'column': 2, 'command': self.add_to_expression},
            {'text': '*', 'row': 2, 'column': 3, 'command': self.add_to_expression, 'bg': '#FF9500'},

            {'text': '1', 'row': 3, 'column': 0, 'command': self.add_to_expression},
            {'text': '2', 'row': 3, 'column': 1, 'command': self.add_to_expression},
            {'text': '3', 'row': 3, 'column': 2, 'command': self.add_to_expression},
            {'text': '-', 'row': 3, 'column': 3, 'command': self.add_to_expression, 'bg': '#FF9500'},

            {'text': '0', 'row': 4, 'column': 0, 'command': self.add_to_expression, 'columnspan': 2},
            {'text': 'C', 'row': 4, 'column': 2, 'command': self.clear_display, 'bg': '#FF3B30'},  # Red for clear
            {'text': '+', 'row': 4, 'column': 3, 'command': self.add_to_expression, 'bg': '#FF9500'},

            {'text': '=', 'row': 5, 'column': 0, 'command': self.calculate_result, 'bg': '#34C759', 'columnspan': 4},
        ]

        # Create and place buttons on the grid
        for btn in buttons:
            btn_bg = btn.get('bg', button_properties['bg'])
            btn_fg = btn.get('fg', button_properties['fg'])
            button = tk.Button(master, text=btn['text'], command=lambda x=btn['command']: x(btn['text']),
                               bg=btn_bg, fg=btn_fg,
                               activebackground=btn.get('activebackground', button_properties['activebackground']),
                               activeforeground=btn.get('activeforeground', button_properties['activeforeground']),
                               font=button_properties['font'],
                               borderwidth=button_properties['borderwidth'],
                               highlightthickness=button_properties['highlightthickness'])
            colspan = btn.get('columnspan', 1)
            button.grid(row=btn['row'], column=btn['column'], columnspan=colspan, padx=5, pady=5, sticky="nsew")

        # Make the buttons expand when window is resized
        for i in range(4):
            master.grid_columnconfigure(i, weight=1)
        for i in range(6):
            master.grid_rowconfigure(i, weight=1)

    def add_to_expression(self, value):
        """Add the pressed button's value to the expression."""
        current = self.display.get()
        self.display.delete(0, tk.END)
        self.display.insert(0, current + value)

    def clear_display(self, _=None):
        """Clear the display."""
        self.display.delete(0, tk.END)

    def calculate_result(self, _=None):
        """Evaluate the expression and display the result."""
        expression = self.display.get()
        try:
            # Evaluate the expression
            result = eval(expression)
            self.display.delete(0, tk.END)
            self.display.insert(0, str(result))
        except ZeroDivisionError:
            messagebox.showerror("Error", "Cannot divide by zero.")
            self.display.delete(0, tk.END)
        except Exception:
            messagebox.showerror("Error", "Invalid input.")
            self.display.delete(0, tk.END)

def main():
    root = tk.Tk()
    calculator = Calculator(root)
    root.geometry("350x500")
    root.resizable(True, True)
    root.mainloop()

if __name__ == "__main__":
    main()
