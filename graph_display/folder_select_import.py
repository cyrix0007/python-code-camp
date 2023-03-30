import os
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# Prompt the user to select the parent folder
root = tk.Tk()
root.withdraw()
data_dir = filedialog.askdirectory(title="Select parent folder")

# Define a function to get a list of files with the specified name from the directory
def get_data_files():
    data_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file == "hoymiles_data.csv":
                data_files.append(os.path.join(root, file))
    # Sort the files by the date in the containing folder name
    data_files.sort(key=lambda x: os.path.dirname(x).split("/")[-1])
    # Extract only the folder name from the directory path and use it as the display value
    display_values = [os.path.basename(os.path.dirname(file)) for file in data_files]
    return data_files, display_values


# Define a function to handle file selection from the dropdown list
def select_file(event):
    file_path = file_list.get()
    print(f"Selected file: {file_path}")


# function to destroy the window and quit the interpreter
def close_window():
    root.destroy()
    root.quit()


# Create the main window and set its properties
root = tk.Tk()
root.title("Select data file")
root.geometry("300x100")

# Create a dropdown list to display the available data files
data_files, display_values = get_data_files()
file_list = ttk.Combobox(root, values=display_values, state="readonly")
file_list.current(0)
file_list.pack(pady=10)

# Bind the selection event to the select_file() function
file_list.bind("<<ComboboxSelected>>", select_file)

# Quit button
quit_app = Button(root, text="Quit", command=close_window)
quit_app.pack()

# Start the main event loop
root.mainloop()
