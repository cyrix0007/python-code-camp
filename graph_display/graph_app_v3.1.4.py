import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import datetime as dt
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import time
import sys
from reconstruct_dates import Reconstruct

# create function to display graph
def show_graph(*args):
    # get selected date from dropdown list
    selected_date = pd.to_datetime(date_dropdown.get())
    time_interval = time_interval_var.get()

    # Filter the dataframe based on the time interval
    if time_interval == "day":
        filtered_df = df[df["date_only"] == selected_date.date().strftime("%Y-%m-%d")]
    elif time_interval == "week":
        filtered_df = filter_week(selected_date.date().strftime("%Y-%m-%d"))
    else:
        filtered_df = df[
            df["current_date_time"].dt.to_period("M") == selected_date.to_period("M")
        ]

    # create figure and axis objects
    fig = Figure(figsize=(7, 7), dpi=100)
    ax = fig.add_subplot(111)
    ax.clear()
    ax.plot(
        filtered_df["current_date_time"],
        filtered_df["current_power_consumed"] * -1,
        label="Power Consumed",
        color="salmon",
        # alpha=0.5,
    )
    ax.plot(
        filtered_df["current_date_time"],
        filtered_df["current_power_generated"],
        label="Power Generated",
        color="teal",
    )
    if tickbox_state.get() == True:
        # define the start and end dates
        start_date = (selected_date.replace(hour=6, minute=0)).strftime(
            "%Y-%m-%d %H:%M"
        )
        print(f'start_date{type(start_date)}')
        end_date = (selected_date.replace(hour=18, minute=0)).strftime("%Y-%m-%d %H:%M")

        # create a boolean mask that selects the rows with dates between start and end dates
        mask = (filtered_df["date_only"] >= start_date) & (
            filtered_df["date_only"] <= end_date
        )

        # filter out the rows that meet the condition using the boolean mask
        solar_production_times = filtered_df #df.loc[mask]
        #print(f"{solar_production_times}")
        ax.plot(
            solar_production_times["current_date_time"],
            solar_production_times["current_power_consumed"]
            - solar_production_times["current_power_generated"],
            label="Excessive Consumption",
            color="green",
            alpha=0.5,
        )

    # set x-axis and y-axis labels
    # ax.set_xlabel("TIME")
    ax.set_ylabel("POWER in kW")
    # Format the x-axis labels as dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    ax.tick_params(axis="x", labelrotation=90)
    fig.subplots_adjust(bottom=0.2)

    # add legend to graph
    ax.legend()
    # set the grid on
    ax.grid("on")

    # creating the Tkinter canvas containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=root)
    toolbar_frame = Frame(root)
    toolbar_frame.grid(row=21, column=1, columnspan=2)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().grid(
        row=1, column=1, columnspan=2, rowspan=20, padx=2, pady=2
    )


# create function to display highest consumption
def show_highest_consumption():
    # create flattened list of all current_power_consumed values
    all_power_consumed = []
    for date, data in df.items():
        all_power_consumed.extend(df["current_power_consumed"])

    # get top 5 highest current_power_generated values for the selected time frame
    highest_power_generated = sorted(all_power_consumed, reverse=True)[:5]

    # display highest current_power_generated values in text field
    highest_consumption_text.delete("1.0", END)
    highest_consumption_text.insert("1.0", "Highest consumption:\n")
    for power in highest_power_generated:
        highest_consumption_text.insert(END, f"{power:.2f} kW\n")


# create function to display plots for selected timeframes
def plot_per_timeframe(theselection):
    time_interval_var.set(value=theselection)


# print(theselection)

# Define a function to filter the dataframe to include only dates within the next 7 days starting with the selected date
def filter_week(date):
    end_date = pd.to_datetime(date) + pd.DateOffset(days=7)
    filtered_week_df = df[
        (df["current_date_time"] >= date) & (df["current_date_time"] <= end_date)
    ]
    return filtered_week_df


# function to destroy the window and quit the interpreter
def close_window():
    root.destroy()
    root.quit()


def refresh_data():
    # Prompt the user to select the parent folder
    global df
    df = pd.DataFrame()
    root = tk.Tk()
    root.withdraw()
    data_dir = filedialog.askdirectory(
        title="Select Folder Containing 'corrected_hoymiles_data.csv'"
    )
    csv_file = data_dir + "/corrected_hoymiles_data.csv"
    keys = ["current_date_time", "current_power_generated", "current_power_consumed"]

    # setup expected data types for DataFrame (speed up processing?)
    dtype = {
        "current_date_time": "object",
        "current_power_generated": "float",
        "current_power_consumed": "float",
    }

    # Clear the df before populating with new datas
    # df.iloc[0:0]
    df = pd.read_csv(csv_file, names=keys, header=0, dtype=dtype)

    # First convert the column to datetime dtype
    df["current_date_time"] = pd.to_datetime(df["current_date_time"])
    # Extract the dates (without the time) from the datetime values
    df["date_only"] = df["current_date_time"].dt.date.astype(str)
    date_list = sorted(list(set(df["date_only"])))
    date_dropdown.configure(values=date_list)


def repair_dates(*args):
    repair_csv = Reconstruct()
    print("Running...")
    Reconstruct.correct_hoymiles_csv()
    print("Done...")


########################################################################################
# UI for displaying graph
########################################################################################
root = Tk()
root.title("Power Usage Graph")
# dimensions of the main window
root.geometry("1024x800")

########################################################################################
# Placeholder on UI for plots
########################################################################################
fig = Figure(figsize=(7, 7), dpi=100)
# create figure and axis objects
ax = fig.add_subplot(111)

# set y-axis labels
ax.set_ylabel("POWER in kW")

# creating the Tkinter canvas containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master=root)
toolbar_frame = Frame(root)
toolbar_frame.grid(row=21, column=1, columnspan=2)
toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
toolbar.update()
canvas.draw()

# placing the canvas on the Tkinter window
canvas.get_tk_widget().grid(
    row=1, column=1, columnspan=2, rowspan=20
)  # , padx=2, pady=2)
########################################################################################

########################################################################################
# Combobox list for selecting date
########################################################################################
# Define variables for combobox
date_var = tk.StringVar(value="Select Date")
date_list = []
date_dropdown = ttk.Combobox(
    root, textvariable=date_var, values=date_list, state="readonly"
)

# Initialise the first dataset
refresh_data()

# First convert the column to datetime dtype
df["current_date_time"] = pd.to_datetime(df["current_date_time"])
# Extract the dates (without the time) from the datetime values
df["date_only"] = df["current_date_time"].dt.date.astype(str)
date_list = sorted(list(set(df["date_only"])))
# date_dropdown.current(0)
date_dropdown.grid(row=2, column=6)
# Bind the selection event to the show_graph() function
date_dropdown.bind("<<ComboboxSelected>>", show_graph)
########################################################################################

########################################################################################
# Radio buttons for selecting time interval
########################################################################################
time_interval_var = tk.StringVar(None)
day_radio = Radiobutton(
    root,
    text="Day",
    variable=time_interval_var,
    value="day",
    command=lambda: plot_per_timeframe("day"),
)
week_radio = Radiobutton(
    root,
    text="Week",
    variable=time_interval_var,
    value="week",
    command=lambda: plot_per_timeframe("week"),
)
month_radio = Radiobutton(
    root,
    text="Month",
    variable=time_interval_var,
    value="month",
    command=lambda: plot_per_timeframe("month"),
)
day_radio.grid(row=5, column=5)
week_radio.grid(row=5, column=6)
month_radio.grid(row=5, column=7, sticky=E)

# create a boolean variable to track the state of the tickbox
tickbox_state = tk.BooleanVar(value=False)
# create the tickbox and associate it with the variable
tickbox = tk.Checkbutton(root, text="Plot", variable=tickbox_state)
# set the initial state of the tickbox
# tickbox_state.set(False)
tickbox.grid(row=6, column=5)

########################################################################################
# Buttons
########################################################################################

# create button for displaying highest consumption
repair_button = Button(root, text="Repair CSV file", command=repair_dates)
repair_button.grid(row=8, column=6, sticky=E)

# create button for displaying highest consumption
reload_button = Button(root, text="Open file", command=refresh_data)
reload_button.grid(row=7, column=6, sticky=E)

# create button for displaying highest consumption
highest_consumption_button = Button(
    root, text="Show Highest Consumption", command=show_highest_consumption
)
highest_consumption_button.grid(row=11, column=6, sticky=E)

# Quit button
quit_app = Button(root, text="Quit", command=close_window)
quit_app.grid(row=9, column=6, sticky=SE)
########################################################################################

########################################################################################
# Text field
########################################################################################
# create text field for displaying highest consumption
highest_consumption_text = Text(root, height=6, width=20)
highest_consumption_text.grid(row=12, column=6, rowspan=6, sticky=E)

# run UI
root.mainloop()
