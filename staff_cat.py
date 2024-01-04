import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

# Create SQLite database and table
conn = sqlite3.connect("phone_numbers.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS phone_numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        inzone TINYINT,
        CONSTRAINT check_inzone CHECK (inzone IN (0, 1))
    )
''')
conn.commit()

def save_to_database(name, phone, inzone):
    try:
        cursor.execute("INSERT INTO phone_numbers (name, phone, inzone) VALUES (?, ?, ?)", (name, phone, inzone))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error saving to database: {e}")

def save_to_file(phone, inzone):
    filename = "innie.txt" if inzone else "outie.txt"
    try:
        with open(filename, "a") as file:
            file.write(f"{phone}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving to {filename}: {e}")

def update_database(id, name, phone, inzone):
    try:
        cursor.execute("UPDATE phone_numbers SET name=?, phone=?, inzone=? WHERE id=?", (name, phone, inzone, id))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error updating database: {e}")

def submit(inzone):
    name = name_entry.get()
    phone = phone_entry.get()

    try:
        if phone:
            save_to_database(name, phone, inzone)
            save_to_file(phone, inzone)

            if inzone:
                result_label.config(text="Phone number saved to innie.txt and database!")
            else:
                result_label.config(text="Phone number saved to outie.txt and database!")

            name_entry.delete(0, tk.END)
            phone_entry.delete(0, tk.END)
        else:
            result_label.config(text="Please enter a phone number.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def get_all_data():
    cursor.execute("SELECT * FROM phone_numbers")
    return cursor.fetchall()

def on_item_click(event):
    col_id = tree.identify_column(event.x)

    if col_id:
        col_id = int(col_id.split("#")[-1]) - 1

        # Prompt the user to edit the values
        item = tree.identify_row(event.y)
        edited_value = simpledialog.askstring("Edit", f"Edit {tree.heading(col_id)['text']} (currently {tree.item(item, 'values')[col_id]}):", initialvalue=tree.item(item, 'values')[col_id])
        values = ()  #[tree.item(item, 'values')[0], edited_value, tree.item(item, 'values')[2], tree.item(item, 'values')[3]]
        for i, x in enumerate(tree.item(item, 'values')):
            print(i, x, col_id, edited_value)
            values += (x if i != col_id else edited_value,)
        print(values)
        # Update the tree view with the edited value
        tree.item(item, values=values)

def display_edit_window():
    edit_window = tk.Toplevel(app)
    edit_window.title("Edit Data")

    global tree
    tree = ttk.Treeview(edit_window, columns=("ID", "Name", "Phone", "Inzone"), show="headings", selectmode="browse")

    # Add column headings
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Phone", text="Phone")
    tree.heading("Inzone", text="Inzone")

    # Add data from the database
    data = get_all_data()
    for row in data:
        tree.insert("", "end", values=row)

    tree.pack(fill="both", expand=True)

    # Bind the click event to enable editing
    tree.bind("<ButtonRelease-1>", on_item_click)

    def save_changes():
        # Update the database with the edited values
        for item_id in tree.get_children():
            id = tree.item(item_id, "values")[0]
            name = tree.item(item_id, "values")[1]
            phone = tree.item(item_id, "values")[2]
            inzone = tree.item(item_id, "values")[3]

            update_database(id, name, phone, inzone)

        messagebox.showinfo("Success", "Changes saved to the database!")

    save_button = tk.Button(edit_window, text="Save Changes", command=save_changes)
    save_button.pack(pady=10)

# Create main window
app = tk.Tk()
app.title("Phone Number Saver")
app.geometry("400x200")  # Set initial window size
app.resizable(False, False)  # Prevent window resizing

# Add some styles
style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=(5, 5, 5, 5), borderwidth=0, relief="flat", background="purple", foreground="black")
style.map("TButton", background=[("active", "green")])

# Create and place widgets using grid with responsiveness
tk.Label(app, text="Name:").grid(row=0, column=0, pady=5, padx=5, sticky="e")
name_entry = tk.Entry(app)
name_entry.grid(row=0, column=1, pady=5, padx=5, sticky="we", columnspan=2)

tk.Label(app, text="Phone Number:").grid(row=1, column=0, pady=5, padx=5, sticky="e")
phone_entry = tk.Entry(app)
phone_entry.grid(row=1, column=1, pady=5, padx=5, sticky="we", columnspan=2)

# Buttons for "in" and "out" with radius
in_button = ttk.Button(app, text="In", command=lambda: submit(1), style="TButton")
in_button.grid(row=2, column=1, pady=10, padx=(5, 5), sticky="we")

out_button = ttk.Button(app, text="Out", command=lambda: submit(0), style="TButton")
out_button.grid(row=2, column=2, pady=10, padx=(5, 5), sticky="we")

result_label = tk.Label(app, text="", anchor="w")
result_label.grid(row=3, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

# Create a menu bar
menu_bar = tk.Menu(app)
app.config(menu=menu_bar)

# Create "Options" menu
options_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Options", menu=options_menu)

# Add sub-items to "Options" menu
options_menu.add_command(label="Edit", command=display_edit_window)
options_menu.add_separator()
options_menu.add_command(label="Exit", command=app.quit)

# Start the main loop
app.mainloop()

# Close the SQLite connection when the program exits
conn.close()
