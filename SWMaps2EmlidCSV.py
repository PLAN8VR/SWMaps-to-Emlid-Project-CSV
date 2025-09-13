import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
from datetime import timedelta
import os
import subprocess

# Tkinter setup
root = tk.Tk()
root.withdraw()
root.lift()
root.attributes('-topmost', True)

# Select input CSV
input_file = filedialog.askopenfilename(
    title="Select GNSS CSV file",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
)
if not input_file:
    messagebox.showinfo("Cancelled", "No input file selected. Exiting.")
    sys.exit()

# Select output CSV
output_file = filedialog.asksaveasfilename(
    title="Save converted file as",
    defaultextension=".csv",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    initialfile="emlid.csv"
)
if not output_file:
    messagebox.showinfo("Cancelled", "No output file selected. Exiting.")
    sys.exit()

# Define required headers in exact order
emlid_headers = [
    "Name","Code","Easting","Northing","Elevation","Description","Longitude","Latitude",
    "Ellipsoidal height","Origin","Easting RMS","Northing RMS","Elevation RMS","Lateral RMS",
    "Antenna height","Antenna height units","Solution status","Correction type","Averaging start",
    "Averaging end","Samples","PDOP","GDOP","Base easting","Base northing","Base elevation",
    "Base longitude","Base latitude","Base ellipsoidal height","Baseline","Mount point",
    "CS name","GPS Satellites","GLONASS Satellites","Galileo Satellites","BeiDou Satellites",
    "QZSS Satellites"
]

try:
    # Read input and normalize columns
    df = pd.read_csv(input_file)
    df.columns = df.columns.str.lower()  # normalize

    # Detect possible columns
    name_col = next((c for c in df.columns if c.lower() in ["id", "track name", "name"]), None)
    time_col = next((c for c in df.columns if c in ["time","timestamp","date"]), None)
    lon_col = next((c for c in df.columns if c in ["longitude","lon"]), None)
    lat_col = next((c for c in df.columns if c in ["latitude","lat"]), None)
    elev_col = next((c for c in df.columns if c in ["elevation","ellipsoidal height","height"]), None)
    
    # Detect instrument/antenna height column robustly
    inst_height_col = next(
        (c for c in df.columns if any(k in c.lower() for k in [
            "instrument height", "instrument ht", "antenna height", "antenna ht"
        ])),
        None
    )

    n_rows = len(df)

    # Parse time including input offset
    if time_col:
        df[time_col] = pd.to_datetime(df[time_col], dayfirst=True, errors="coerce")

        def format_utc_with_ms(dt):
            if pd.isna(dt):
                return ""
            offset = dt.strftime("%z")  # e.g., +0100
            offset_formatted = offset[:3] + ":" + offset[3:] if offset else "+00:00"
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S") + f".{int(dt.microsecond/1000):03d}"
            return time_str + f" UTC{offset_formatted}"

        df["avg_time_start"] = df[time_col].apply(format_utc_with_ms)
        df["avg_time_end"] = (df[time_col] + timedelta(seconds=4)).apply(format_utc_with_ms)

    # Build mapped dataframe with correct length series for scalars
    mapped = pd.DataFrame({
        "Name": df[name_col].astype(str) if name_col else pd.Series([""] * n_rows),
        "Averaging start": df["avg_time_start"] if time_col else pd.Series([""] * n_rows),
        "Averaging end": df["avg_time_end"] if time_col else pd.Series([""] * n_rows),
        "Samples": pd.Series(1, index=df.index),
        "Longitude": df[lon_col] if lon_col else pd.Series([""] * n_rows),
        "Latitude": df[lat_col] if lat_col else pd.Series([""] * n_rows),
        "Elevation": df[elev_col] if elev_col else pd.Series([""] * n_rows),
        "Antenna height": df[inst_height_col] if inst_height_col else pd.Series([""] * n_rows),
        "Antenna height units": pd.Series(["m"] * n_rows)
    })

    # Fill missing headers with empty strings
    for col in emlid_headers:
        if col not in mapped.columns:
            mapped[col] = pd.Series([""] * n_rows)

    # Reorder columns exactly
    mapped = mapped[emlid_headers]

    # Save CSV
    mapped.to_csv(output_file, index=False)

    # Show popup confirmation
    messagebox.showinfo("Success", f"Conversion complete.\nSaved as:\n{output_file}")

    # Open containing folder
    folder = os.path.dirname(output_file)
    if sys.platform == "win32":
        os.startfile(folder)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", folder])
    else:
        subprocess.Popen(["xdg-open", folder])

except Exception as e:
    messagebox.showerror("Error", f"An error occurred: {e}")
