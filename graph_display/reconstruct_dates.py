# -*- coding: utf-8 -*-
"""
Script to reconstruct invalid/missing dates from recorded power gen + consump
@author: Frans Boning (with help from Chase Meredith)
"""
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np

# Define a class that encapsulates the functionality of the script
class Reconstruct:
    def __init__(self):
        # Initialize any state or resources needed by the script
        pass

    def correct_hoymiles_csv():
        # Prompt the user to select the parent folder
        root = tk.Tk()
        root.withdraw()
        data_dir = filedialog.askdirectory(
            title="Select Folder Contaning 'hoymiles_data.csv:'"
        )

        # define the filename and keys
        filename = data_dir + "/hoymiles_data.csv"
        corrected_filename = data_dir + "/corrected_hoymiles_data.csv"
        keys = [
            "current_date_time",
            "current_power_generated",
            "current_power_consumed",
        ]

        # setup expected data types for DataFrame (speed up processing?)
        dtype = {
            "current_date_time": "object",
            "current_power_generated": "float",
            "current_power_consumed": "float",
        }
        # Read csv file with above params
        df = pd.read_csv(filename, names=keys, header=0, dtype=dtype)

        # replace invalid dates with NaN using 'replace'
        df["current_date_time"] = df["current_date_time"].replace(
            "2000-00-00 00:00:00", np.nan
        )

        # convert dates to datetime objects
        df["current_date_time"] = pd.to_datetime(df["current_date_time"])

        # Get the indices of all the invalid dates
        nan_indices = np.where(np.isnan(df["current_date_time"]))[0]

        # If there are NaN values in the list
        if len(nan_indices) > 0:
            # Get the start and end indices of the ranges that contain NaN
            nan_ranges = np.split(
                nan_indices, np.where(np.diff(nan_indices) != 1)[0] + 1
            )
            nan_ranges = [(i[0], i[-1]) for i in nan_ranges]

            """ print("The NaN ranges are:")
            for start, end in nan_ranges:
                print(f"{start}-{end}") """
        else:
            print("There are no NaN values in the list.")

        nan_ranges_rest = nan_ranges[1:]
        new_nan_ranges = tuple(nan_ranges_rest) + (nan_ranges[0],)

        # print(range(len(nan_ranges)))
        time_ave = []
        df_len = len(df)

        for x in range(len(new_nan_ranges)):
            start_index = new_nan_ranges[x][0]
            end_index = new_nan_ranges[x][1]
            dif = end_index - start_index

            if dif == 0 and df_len != end_index + 1 and start_index != 0:
                time_add = (
                    df["current_date_time"][end_index + 1]
                    - df["current_date_time"][start_index - 1]
                ) / 2
                time_ave.append((time_add))

            # if at the end of the data set without a valid end date:
            elif df_len == end_index + 1:
                pass

            elif start_index == 0:
                pass
            else:
                time_add = (
                    df["current_date_time"][end_index + 1]
                    - df["current_date_time"][start_index - 1]
                ) / dif
                time_ave.append((time_add))

            if start_index != 0:
                for i in range(0, dif + 1):
                    df.loc[(start_index + i), "current_date_time"] = (
                        df["current_date_time"][start_index - 1 + i] + time_add
                    )

            # Normal condition for wrong block data:
            else:
                for i in range(end_index, -1, -1):
                    df.loc[(i), "current_date_time"] = (
                        df["current_date_time"][i + 1] - time_add
                    )
            # find data gap >= 2 min
            timediff = df["current_date_time"].diff()
            filtered_df = df[timediff >= pd.Timedelta(minutes=2)].index
            for i in range(len(filtered_df)):
                df.loc[(filtered_df[i]), "current_power_generated"] = 0
                df.loc[(filtered_df[i] - 1), "current_power_generated"] = 0
                df.loc[(filtered_df[i]), "current_power_consumed"] = 0
                df.loc[(filtered_df[i] - 1), "current_power_consumed"] = 0

        # Convert dates to drop micro seconds after corrected:
        # Convert the column to datetime dtype
        df["current_date_time"] = pd.to_datetime(df["current_date_time"])

        # Truncate the datetime values to the second
        df["current_date_time"] = df["current_date_time"].dt.floor("1s")

        # Store new data in CSV file
        try:
            df.to_csv(corrected_filename, index=False)
            print("Successfully created corrected log data file!")
        except EOFError:
            print("Something wrong with file or data!")

        except Exception:
            print("Other error or exception occured!")
