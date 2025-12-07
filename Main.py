import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add this function at the top
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Global variable to store the dataframe
df_global = None
sort_reverse = {}

def load_csv():
    global df_global
    try:
        # Use the new function to get the CSV path
        csv_path = get_resource_path('NotesDeTall.xlsx - Table 1.csv')
        df_global = pd.read_csv(csv_path)
        
        # ... rest of your code stays the same
        
        # Drop the Digit column if it exists
        df_global.drop(columns=["Digit"], inplace=True, errors="ignore")
        
        df = df_global
        
        # Populate filter dropdowns
        populate_filters()
        
        # Clear existing data in the table
        for item in tree.get_children():
            tree.delete(item)
        
        # Configure columns
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        
        # Set column headings
        for col in df.columns:
            tree.heading(col, text=col, command=lambda c=col: sort_column(c))
            
            # Set specific widths for certain columns
            if col == "Universitat":
                tree.column(col, width=80, anchor="w")
            elif col == "Nota":
                tree.column(col, width=50, anchor="center")
            else:
                # Calculate column width based on content for other columns
                max_width = len(str(col)) * 10  # Header width
                for value in df[col].astype(str):
                    max_width = max(max_width, len(value) * 8)
                # Set minimum and maximum width limits
                max_width = min(max(max_width, 80), 250)
                tree.column(col, width=max_width, anchor="w")
        
        # Insert data rows
        for idx, row in df.iterrows():
            tree.insert("", "end", values=list(row))
        
    except FileNotFoundError:
        messagebox.showerror("Error", "CSV file not found!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def populate_filters():
    """Populate the filter dropdowns with unique values"""
    global uni_filter, city_filter
    if df_global is None:
        return
    
    # Get unique values for filters
    if "Universitat" in df_global.columns:
        # Split multi-university entries and get all unique universities
        all_unis = set()
        for val in df_global["Universitat"].dropna():
            # Split by comma or slash
            unis = str(val).replace("/", ",").split(",")
            for uni in unis:
                uni = uni.strip()
                if uni:
                    all_unis.add(uni)
        unis = ["Totes"] + sorted(all_unis)
        uni_filter["values"] = unis
        uni_filter.set("Totes")
    
    if "Ciutat" in df_global.columns:
        # Split multi-city entries and get all unique cities
        all_cities = set()
        for val in df_global["Ciutat"].dropna():
            # Split by comma or slash only (not " i " to preserve city names)
            cities = str(val).replace("/", ",").split(",")
            for city in cities:
                city = city.strip()
                if city:
                    all_cities.add(city)
        cities = ["Totes"] + sorted(all_cities)
        city_filter["values"] = cities
        city_filter.set("Totes")

def apply_filters():
    """Apply all filters (search, university, city)"""
    global uni_filter, city_filter
    if df_global is None:
        return
    
    # Start with all data
    filtered_df = df_global.copy()
    
    # Apply university filter
    uni_value = uni_filter.get()
    if uni_value != "Totes" and "Universitat" in df_global.columns:
        # Check if the university name appears in the cell (supports multi-university entries)
        filtered_df = filtered_df[filtered_df["Universitat"].astype(str).str.contains(uni_value, case=False, na=False, regex=False)]
    
    # Apply city filter
    city_value = city_filter.get()
    if city_value != "Totes" and "Ciutat" in df_global.columns:
        # Check if the city name appears in the cell (supports multi-city entries)
        filtered_df = filtered_df[filtered_df["Ciutat"].astype(str).str.contains(city_value, case=False, na=False, regex=False)]
    
    # Apply search filter
    search_term = search_entry.get().lower()
    if search_term:
        mask = filtered_df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)
        filtered_df = filtered_df[mask]
    
    # Clear and repopulate table
    for item in tree.get_children():
        tree.delete(item)
    
    for idx, row in filtered_df.iterrows():
        tree.insert("", "end", values=list(row))

def search_data():
    apply_filters()

def clear_search():
    global uni_filter, city_filter
    search_entry.delete(0, "end")
    uni_filter.set("Totes")
    city_filter.set("Totes")
    apply_filters()

def sort_column(col):
    """Sort table by column when header is clicked"""
    global df_global, sort_reverse, uni_filter, city_filter
    
    if df_global is None:
        return
    
    # Toggle sort direction
    reverse = sort_reverse.get(col, False)
    sort_reverse[col] = not reverse
    
    # Start with all data
    display_df = df_global.copy()
    
    # Apply university filter
    uni_value = uni_filter.get()
    if uni_value != "Totes" and "Universitat" in df_global.columns:
        # Check if the university name appears in the cell (supports multi-university entries)
        display_df = display_df[display_df["Universitat"].astype(str).str.contains(uni_value, case=False, na=False, regex=False)]
    
    # Apply city filter
    city_value = city_filter.get()
    if city_value != "Totes" and "Ciutat" in df_global.columns:
        # Check if the city name appears in the cell (supports multi-city entries)
        display_df = display_df[display_df["Ciutat"].astype(str).str.contains(city_value, case=False, na=False, regex=False)]
    
    # Apply search filter
    search_term = search_entry.get().lower()
    if search_term:
        mask = display_df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)
        display_df = display_df[mask]
    
    # Sort the dataframe
    display_df = display_df.sort_values(by=col, ascending=not reverse)
    
    # Clear and repopulate table
    for item in tree.get_children():
        tree.delete(item)
    
    for idx, row in display_df.iterrows():
        tree.insert("", "end", values=list(row))

# Create main window
root = tk.Tk()
root.title("📊Cercador de Notes de Tall")
root.geometry("900x650")
root.configure(bg="#2c3e50")

# Configure fonts
button_font = ("Segoe UI", 10, "bold")
label_font = ("Segoe UI", 11, "bold")
entry_font = ("Segoe UI", 10)
tree_font = ("Segoe UI", 9)
status_font = ("Segoe UI", 9)

# Create header frame with title
header_frame = tk.Frame(root, bg="#2c3e50", height=60)
header_frame.pack(fill="x")
header_frame.pack_propagate(False)

title_label = tk.Label(header_frame, text="📊Cercador de Notes de Tall", 
                       font=("Segoe UI", 16, "bold"), 
                       bg="#2c3e50", fg="white")
title_label.pack(pady=15)

# Create frame for search bar
search_frame = tk.Frame(root, bg="#2c3e50")
search_frame.pack(pady=15)

# Filter frame (first row)
filter_frame = tk.Frame(search_frame, bg="#2c3e50")
filter_frame.pack(pady=(0, 10))

# University filter
uni_label = tk.Label(filter_frame, text="Universitat:", font=label_font, bg="#2c3e50", fg="white")
uni_label.pack(side="left", padx=5)

uni_filter = ttk.Combobox(filter_frame, width=25, font=entry_font, state="readonly")
uni_filter.pack(side="left", padx=5)
uni_filter.bind("<<ComboboxSelected>>", lambda e: apply_filters())

# City filter
city_label = tk.Label(filter_frame, text="Ciutat:", font=label_font, bg="#2c3e50", fg="white")
city_label.pack(side="left", padx=(15, 5))

city_filter = ttk.Combobox(filter_frame, width=25, font=entry_font, state="readonly")
city_filter.pack(side="left", padx=5)
city_filter.bind("<<ComboboxSelected>>", lambda e: apply_filters())

# Search bar frame (second row)
search_bar_frame = tk.Frame(search_frame, bg="#2c3e50")
search_bar_frame.pack()

# Search label
search_label = tk.Label(search_bar_frame, text="🔍 Buscar:", font=label_font, bg="#2c3e50", fg="white")
search_label.pack(side="left", padx=5)

# Search entry with styling
search_entry = tk.Entry(search_bar_frame, width=50, font=entry_font, 
                       relief="solid", bd=1, highlightthickness=1,
                       highlightbackground="#3498db", highlightcolor="#3498db")
search_entry.pack(side="left", padx=5, ipady=5)
search_entry.bind("<KeyRelease>", lambda e: search_data())

# Clear button (small X button)
clear_button = tk.Button(search_bar_frame, text="✕ Netejar tot", command=clear_search,
                        bg="#ecf0f1", fg="#7f8c8d", padx=10, pady=3, 
                        font=("Segoe UI", 10, "bold"), relief="flat",
                        cursor="hand2", bd=0)
clear_button.pack(side="left", padx=5)

# Create frame for treeview with scrollbars
tree_frame = tk.Frame(root, bg="#2c3e50")
tree_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

# Configure scrollbar style
style = ttk.Style()
style.theme_use("clam")

# Configure scrollbar colors
style.configure("Vertical.TScrollbar",
                background="#34495e",
                troughcolor="#34495e",
                bordercolor="#ecf0f1",
                arrowcolor="white")
style.map("Vertical.TScrollbar",
          background=[("active", "#2c3e50"), ("pressed", "#2c3e50")])

style.configure("Horizontal.TScrollbar",
                background="#34495e",
                troughcolor="#ecf0f1",
                bordercolor="#ecf0f1",
                arrowcolor="white")
style.map("Horizontal.TScrollbar",
          background=[("active", "#2c3e50"), ("pressed", "#2c3e50")])

# Create scrollbars with custom style
vsb = ttk.Scrollbar(tree_frame, orient="vertical", style="Vertical.TScrollbar")

# Configure style for Treeview
style.configure("Treeview", 
                font=tree_font, 
                rowheight=28,
                background="white",
                foreground="black",
                fieldbackground="white",
                borderwidth=0)
style.configure("Treeview.Heading", 
                font=("Segoe UI", 10, "bold"),
                background="#34495e",
                foreground="white",
                borderwidth=0)
style.map("Treeview.Heading",
          background=[("active", "#2c3e50")])
style.map("Treeview",
          background=[("selected", "#3498db")],
          foreground=[("selected", "white")])

# Create Treeview (table)
tree = ttk.Treeview(tree_frame, yscrollcommand=vsb.set)
vsb.config(command=tree.yview)

# Pack scrollbars and treeview
vsb.pack(side="right", fill="y")
tree.pack(fill="both", expand=True)

# Load CSV automatically on startup
root.after(100, load_csv)

# Start the GUI
root.mainloop()