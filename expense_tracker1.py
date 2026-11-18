
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from pathlib import Path
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expenses.db"

BG = "#0B1220"
PANEL = "#131F33"
CARD = "#192942"
INPUT = "#22344D"
BLUE = "#38BDF8"
GREEN = "#22C55E"
RED = "#F87171"
WHITE = "#F8FAFC"
MUTED = "#94A3B8"

# ==========================================
# DATABASE
# ==========================================

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    type TEXT NOT NULL CHECK(type IN ('Income', 'Expense'))
)
""")
conn.commit()


# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()
root.title("YOUR PERSONAL FINANCE MANAGER ")
root.geometry("1200x780")
root.minsize(1000, 650)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=PANEL,
    foreground=WHITE,
    fieldbackground=PANEL,
    rowheight=36,
    borderwidth=0,
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    background=CARD,
    foreground=WHITE,
    font=("Arial", 10, "bold"),
    padding=10
)

style.map(
    "Treeview",
    background=[("selected", "#164E73")],
    foreground=[("selected", WHITE)]
)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def money(value):
    return f"₹{value:,.2f}"


def show_error(error):
    messagebox.showerror("FinancePro Error", str(error))


# ==========================================
# DASHBOARD HEADER
# ==========================================

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=28, pady=(22, 12))

tk.Label(
    header,
    text="FINANCEPRO",
    bg=BG,
    fg=BLUE,
    font=("Arial", 12, "bold")
).pack(anchor="w")

tk.Label(
    header,
    text="Personal Finance Dashboard",
    bg=BG,
    fg=WHITE,
    font=("Arial", 25, "bold")
).pack(anchor="w", pady=(5, 0))

tk.Label(
    header,
    text="Manage your money. Understand your spending.",
    bg=BG,
    fg=MUTED,
    font=("Arial", 10)
).pack(anchor="w", pady=(5, 0))


# ==========================================
# SUMMARY CARDS
# ==========================================

summary = tk.Frame(root, bg=BG)
summary.pack(fill="x", padx=20, pady=15)


def create_summary_card(title, color):
    card = tk.Frame(summary, bg=CARD, padx=20, pady=18)
    card.pack(side="left", expand=True, fill="x", padx=8)

    tk.Label(
        card,
        text=title,
        bg=CARD,
        fg=MUTED,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    value = tk.Label(
        card,
        text="₹0.00",
        bg=CARD,
        fg=color,
        font=("Arial", 23, "bold")
    )
    value.pack(anchor="w", pady=(12, 0))

    return value


balance_label = create_summary_card("TOTAL BALANCE", BLUE)
income_label = create_summary_card("TOTAL INCOME", GREEN)
expense_label = create_summary_card("TOTAL EXPENSES", RED)


# ==========================================
# MAIN CONTENT
# ==========================================

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=28, pady=12)

# LEFT PANEL

left = tk.Frame(main, bg=PANEL, padx=20, pady=20)
left.pack(side="left", fill="y", padx=(0, 18))

tk.Label(
    left,
    text="NEW TRANSACTION",
    bg=PANEL,
    fg=WHITE,
    font=("Arial", 14, "bold")
).pack(anchor="w", pady=(0, 15))


def create_entry(label):
    tk.Label(
        left,
        text=label,
        bg=PANEL,
        fg=MUTED,
        font=("Arial", 9, "bold")
    ).pack(anchor="w", pady=(10, 5))

    entry = tk.Entry(
        left,
        bg=INPUT,
        fg=WHITE,
        insertbackground=WHITE,
        relief="flat",
        font=("Arial", 11)
    )
    entry.pack(fill="x", ipady=9)

    return entry


title_entry = create_entry("TRANSACTION NAME")
amount_entry = create_entry("AMOUNT (₹)")

tk.Label(
    left,
    text="TRANSACTION TYPE",
    bg=PANEL,
    fg=MUTED,
    font=("Arial", 9, "bold")
).pack(anchor="w", pady=(12, 5))

type_var = tk.StringVar(value="Expense")

type_box = ttk.Combobox(
    left,
    textvariable=type_var,
    values=["Income", "Expense"],
    state="readonly"
)
type_box.pack(fill="x", ipady=5)

tk.Label(
    left,
    text="CATEGORY",
    bg=PANEL,
    fg=MUTED,
    font=("Arial", 9, "bold")
).pack(anchor="w", pady=(12, 5))

category_var = tk.StringVar(value="Food")

category_box = ttk.Combobox(
    left,
    textvariable=category_var,
    values=[
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Education",
        "Health",
        "Salary",
        "Business",
        "Investment",
        "Other"
    ],
    state="readonly"
)
category_box.pack(fill="x", ipady=5)

date_entry = create_entry("DATE (YYYY-MM-DD)")
date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

editing_id = None


# ==========================================
# BUTTON HELPER
# ==========================================

def make_button(parent, text, command, color=BLUE, fg=BG):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=fg,
        activebackground=color,
        activeforeground=fg,
        relief="flat",
        cursor="hand2",
        font=("Arial", 10, "bold"),
        padx=12,
        pady=10
    )


# ==========================================
# TRANSACTION TABLE
# ==========================================

right = tk.Frame(main, bg=BG)
right.pack(side="right", fill="both", expand=True)

top_bar = tk.Frame(right, bg=BG)
top_bar.pack(fill="x", pady=(0, 12))

tk.Label(
    top_bar,
    text="TRANSACTION HISTORY",
    bg=BG,
    fg=WHITE,
    font=("Arial", 15, "bold")
).pack(side="left")

search_var = tk.StringVar()

search_entry = tk.Entry(
    top_bar,
    textvariable=search_var,
    bg=INPUT,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat",
    font=("Arial", 10),
    width=24
)
search_entry.pack(side="right", ipady=8)

search_entry.insert(0, "Search transactions")


table_frame = tk.Frame(right, bg=PANEL)
table_frame.pack(fill="both", expand=True)

columns = ("ID", "Date", "Name", "Category", "Type", "Amount")

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

widths = {
    "ID": 45,
    "Date": 105,
    "Name": 145,
    "Category": 100,
    "Type": 90,
    "Amount": 120
}

for column in columns:
    tree.heading(column, text=column)
    tree.column(column, width=widths[column], anchor="center")

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

tree.tag_configure("Income", foreground=GREEN)
tree.tag_configure("Expense", foreground=RED)


# ==========================================
# DASHBOARD REFRESH
# ==========================================

def refresh_dashboard():
    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN type='Income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END), 0)
        FROM transactions
    """)

    income, expenses = cursor.fetchone()
    balance = income - expenses

    income_label.config(text=money(income))
    expense_label.config(text=money(expenses))
    balance_label.config(text=money(balance))

    load_transactions()


def load_transactions():
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
        SELECT id, date, title, category, type, amount
        FROM transactions
        ORDER BY date DESC, id DESC
    """)

    records = cursor.fetchall()

    search = search_var.get().strip().lower()

    if search == "search transactions":
        search = ""

    for record in records:
        record_text = " ".join(str(x).lower() for x in record)

        if search and search not in record_text:
            continue

        tree.insert(
            "",
            "end",
            values=(
                record[0],
                record[1],
                record[2],
                record[3],
                record[4],
                money(record[5])
            ),
            tags=(record[4],)
        )


# ==========================================
# ADD / UPDATE TRANSACTION
# ==========================================

def save_transaction():
    global editing_id

    title = title_entry.get().strip()
    amount_text = amount_entry.get().strip()
    category = category_var.get()
    transaction_type = type_var.get()
    date = date_entry.get().strip()

    if not title:
        messagebox.showwarning("Missing Information",
                               "Enter a transaction name.")
        return

    try:
        amount = float(amount_text)

        if amount <= 0:
            raise ValueError

        if not amount < 1e12:
            raise ValueError

    except ValueError:
        messagebox.showwarning(
            "Invalid Amount",
            "Enter a valid positive amount."
        )
        return

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        messagebox.showwarning(
            "Invalid Date",
            "Use the date format YYYY-MM-DD."
        )
        return

    try:
        if editing_id is None:
            cursor.execute("""
                INSERT INTO transactions
                (date, title, category, amount, type)
                VALUES (?, ?, ?, ?, ?)
            """, (date, title, category, amount, transaction_type))

        else:
            cursor.execute("""
                UPDATE transactions
                SET date=?, title=?, category=?, amount=?, type=?
                WHERE id=?
            """, (
                date,
                title,
                category,
                amount,
                transaction_type,
                editing_id
            ))

        conn.commit()

        clear_form()
        refresh_dashboard()

    except sqlite3.Error as error:
        conn.rollback()
        show_error(error)


def clear_form():
    global editing_id

    editing_id = None

    title_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)

    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    category_var.set("Food")
    type_var.set("Expense")

    save_button.config(text="ADD TRANSACTION", bg=BLUE)


save_button = make_button(
    left,
    "ADD TRANSACTION",
    save_transaction
)
save_button.pack(fill="x", pady=(20, 8))


# ==========================================
# EDIT TRANSACTION
# ==========================================

def edit_transaction():
    global editing_id

    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Select Transaction",
            "Select a transaction to edit."
        )
        return

    values = tree.item(selected[0], "values")
    editing_id = int(values[0])

    cursor.execute(
        "SELECT date, title, category, amount, type "
        "FROM transactions WHERE id=?",
        (editing_id,)
    )

    record = cursor.fetchone()

    if not record:
        messagebox.showerror("Not Found", "Transaction no longer exists.")
        refresh_dashboard()
        return

    date, title, category, amount, transaction_type = record

    clear_form()
    editing_id = int(values[0])

    date_entry.delete(0, tk.END)
    date_entry.insert(0, date)

    title_entry.insert(0, title)
    amount_entry.insert(0, str(amount))

    category_var.set(category)
    type_var.set(transaction_type)

    save_button.config(
        text="SAVE CHANGES",
        bg=GREEN
    )


# ==========================================
# DELETE SELECTED TRANSACTION
# ==========================================

def delete_transaction():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Select Transaction",
            "Select a transaction to delete."
        )
        return

    values = tree.item(selected[0], "values")
    transaction_id = int(values[0])

    confirm = messagebox.askyesno(
        "Confirm Deletion",
        f"Delete transaction '{values[2]}' for {values[5]}?"
    )

    if not confirm:
        return

    try:
        cursor.execute(
            "DELETE FROM transactions WHERE id=?",
            (transaction_id,)
        )

        conn.commit()
        refresh_dashboard()

    except sqlite3.Error as error:
        conn.rollback()
        show_error(error)


# ==========================================
# DELETE ALL TRANSACTIONS
# ==========================================

def delete_all_transactions():
    confirm = messagebox.askyesno(
        "Delete All Data",
        "WARNING!\n\n"
        "This will permanently delete ALL income and expense records.\n\n"
        "This action cannot be undone.\n\n"
        "Do you want to continue?"
    )

    if not confirm:
        return

    final_confirm = messagebox.askyesno(
        "Final Confirmation",
        "Are you absolutely sure you want to erase all transactions?"
    )

    if not final_confirm:
        return

    try:
        cursor.execute("DELETE FROM transactions")
        conn.commit()

        clear_form()
        refresh_dashboard()

        messagebox.showinfo(
            "Data Cleared",
            "All transaction records have been deleted."
        )

    except sqlite3.Error as error:
        conn.rollback()
        show_error(error)


# ==========================================
# EXPORT CSV
# ==========================================

def export_csv():
    try:
        cursor.execute("""
            SELECT date, title, category, type, amount
            FROM transactions
            ORDER BY date DESC, id DESC
        """)

        records = cursor.fetchall()

        if not records:
            messagebox.showinfo(
                "No Data",
                "There are no transactions to export."
            )
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="finance_report.csv"
        )

        if not filepath:
            return

        with open(filepath, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)

            writer.writerow([
                "Date",
                "Transaction",
                "Category",
                "Type",
                "Amount"
            ])

            writer.writerows(records)

        messagebox.showinfo(
            "Export Successful",
            f"Report saved successfully:\n{filepath}"
        )

    except (OSError, sqlite3.Error) as error:
        show_error(error)


# ==========================================
# ACTION BUTTONS
# ==========================================

actions = tk.Frame(right, bg=BG)
actions.pack(fill="x", pady=12)

make_button(
    actions,
    "EDIT",
    edit_transaction,
    color=BLUE
).pack(side="left", padx=(0, 8))

make_button(
    actions,
    "DELETE SELECTED",
    delete_transaction,
    color=RED,
    fg=WHITE
).pack(side="left", padx=8)

make_button(
    actions,
    "EXPORT CSV",
    export_csv,
    color=GREEN
).pack(side="left", padx=8)

make_button(
    actions,
    "DELETE ALL DATA",
    delete_all_transactions,
    color="#991B1B",
    fg=WHITE
).pack(side="right")


# ==========================================
# SEARCH
# ==========================================

search_var.trace_add(
    "write",
    lambda *args: load_transactions()
)


# ==========================================
# FOOTER
# ==========================================

footer = tk.Label(
    root,
    text="FINANCEPRO  |  Personal Financial Management System",
    bg=BG,
    fg=MUTED,
    font=("Arial", 9)
)

footer.pack(pady=(5, 15))


# ==========================================
# START APPLICATION
# ==========================================

def close_app():
    try:
        conn.close()
    finally:
        root.destroy()


refresh_dashboard()

root.protocol("WM_DELETE_WINDOW", close_app)

root.mainloop()
