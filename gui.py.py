import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime

class FinanceTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.transactions = self.load_transactions("Your_transactions.json")
        self.create_widgets()
        self.display_transactions(self.transactions)

    def create_widgets(self):
        # Create and Naming the label as Your transactions list
        self.transactions_label = tk.Label(self.root, text="Your Transactions List", font=("Arial", 15, "bold"))
        self.transactions_label.pack(pady=(10, 5))

        # Frame for search bar and buttons
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Enter a Transaction to find:").grid(row=0, column=0)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, padx=8)
        tk.Button(search_frame, text="Search", command=self.search_transactions).grid(row=0, column=2)

        # Frame for Sort 
        sort_frame = tk.Frame(self.root)
        sort_frame.pack(pady=5)

        tk.Label(sort_frame, text="Sort by:").grid(row=0, column=0, padx=5)

        self.sort_options = ["Category (A-Z)", "Date (Oldest to Newest)", "Date (Newest to Oldest)",
                             "Amount (Highest to Lowest)", "Amount (Lowest to Highest)"]
        self.sort_variable = tk.StringVar(sort_frame)
        self.sort_variable.set(self.sort_options[0]) 

        self.sort_dropdown = ttk.Combobox(sort_frame, textvariable=self.sort_variable, values=self.sort_options, state="readonly")
        self.sort_dropdown.grid(row=0, column=1, padx=5)
        self.sort_dropdown.bind("<<ComboboxSelected>>", self.sort_by_selected)

        # Frame for the table and scrollbar
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        self.scroll_bar = tk.Scrollbar(table_frame)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview for transactions
        self.tree_view = ttk.Treeview(table_frame, columns=("Category", "Amount", "Date"), show="headings", yscrollcommand=self.scroll_bar.set)
        self.tree_view.pack(fill=tk.BOTH, expand=True)

        # Set headings for the Treeview columns
        self.tree_view.heading("Category", text="Category", anchor=tk.W)
        self.tree_view.heading("Amount", text="Amount", anchor=tk.E)
        self.tree_view.heading("Date", text="Date", anchor=tk.CENTER)

        # Configure column widths
        self.tree_view.column("#0", width=0)  
        self.tree_view.column("Category", width=150)
        self.tree_view.column("Amount", width=120)
        self.tree_view.column("Date", width=120)

        # Configure scrollbar
        self.scroll_bar.config(command=self.tree_view.yview)

    def load_transactions(self, filename):
        try:
            with open(filename, 'r') as file:
                return json.loads(file.read())  
        except FileNotFoundError:
            print("Error: File 'transactions.json' not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: Invalid JSON data in 'transactions.json'")
            return {}

    def display_transactions(self, transactions):
        # Clear existing Treeview entries
        self.tree_view.delete(*self.tree_view.get_children())

        for category, transactions_list in transactions.items():
            for transaction in transactions_list:
                self.tree_view.insert('', tk.END, values=(category, transaction['amount'], transaction['date']))

    def search_transactions(self):
        search_term = self.search_entry.get().lower()  

        if search_term:
            filtered_transactions = {}
            for category, transactions_list in self.transactions.items():
                filtered_list = [txn for txn in transactions_list if search_term in category.lower() or search_term in str(txn['amount'])]
                if filtered_list:
                    filtered_transactions[category] = filtered_list
            self.display_transactions(filtered_transactions)
        else:
            self.display_transactions(self.transactions)  # Display all

    def sort_by_column(self, col, reverse):
        col_index = -1  # Initialize to a default value
        if col == "Category":
            col_index = 0
        elif col == "Amount":
            col_index = 1
        elif col == "Date":
            col_index = 2

        # Ensure col_index has a valid value 
        if col_index == -1:
            print(f"Error: Invalid column name '{col}'")
            return  

        data = [(self.tree_view.item(child)['values'][col_index], child) for child in self.tree_view.get_children('')]

        if col == 'Category':
            data.sort(key=lambda t: t[0], reverse=reverse) 
        elif col == 'Amount':
            data.sort(key=lambda t: float(t[0]), reverse=reverse) 
        elif col == 'Date':  
            def try_parsing_date(text):
                try:
                    return datetime.strptime(text, '%Y-%m-%d')
                except ValueError:
                    return None  

            data.sort(key=lambda t: try_parsing_date(t[0]), reverse=reverse)  

        for index, (val, child) in enumerate(data):
            self.tree_view.move(child, '', index)
        self.tree_view.heading(col, command=lambda _col=col: self.sort_by_column(_col, not reverse))

    def sort_by_selected(self, event):
        selected_option = self.sort_variable.get()

        if selected_option == "Category (A-Z)":
            self.sort_by_column("Category", False)
        elif selected_option == "Date (Oldest to Newest)":
            self.sort_by_column("Date", False) 
        elif selected_option == "Date (Newest to Oldest)":
            self.sort_by_column("Date", True)  
        elif selected_option == "Amount (Highest to Lowest)":
            self.sort_by_column("Amount", True)  
        elif selected_option == "Amount (Lowest to Highest)": 
            self.sort_by_column("Amount", False) 

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTrackerGUI(root)
    root.mainloop()
