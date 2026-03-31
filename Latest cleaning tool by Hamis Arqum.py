import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re
import time
from datetime import datetime

# === Precompiled Regex ===
cnic_re = re.compile(r"^\d{13}$")
phone_re = re.compile(r"^\d{10,11}$")
keyboard_mash_re = re.compile(r"(asdf|qwer|zxcv|hjkl|dfgh|tyui|ghjk)")
placeholders = {"unavailable", "un-available", "n/a", "none", "xxx", "-", ""}
helpline_variants = {"111362362", "0111362362", "01111362362"}

# === Validation Functions ===
def is_valid_name(series, min_len=2):
    s = series.str.lower().str.strip()
    letters = s.str.replace(r"[^a-z]", "", regex=True)
    vowels = letters.str.count(r"[aeiou]")
    ratio = vowels / letters.str.len().replace(0, np.nan)
    return (
        (letters.str.len() >= min_len) &
        (ratio >= 0.25) &
        ~s.isin(placeholders) &
        ~s.str.contains(keyboard_mash_re)
    )

def is_valid_cnic(series):
    s = series.str.replace(".", "", regex=False).str.strip()
    is_valid_length = s.str.fullmatch(r"\d{13}")
    is_not_uniform = s != s.str[0] * s.str.len()
    return is_valid_length & is_not_uniform

def is_valid_phone(series):
    s = series.str.replace(r"\D", "", regex=True)
    is_valid_format = s.str.fullmatch(r"\d{10,11}")
    is_not_helpline = ~s.isin(helpline_variants)
    is_not_uniform = s != s.str[0] * s.str.len()
    return is_valid_format & is_not_helpline & is_not_uniform

def is_valid_amount(series):
    s = pd.to_numeric(series.str.replace(r"[^\d]", "", regex=True), errors='coerce')
    return s >= 5000

def is_valid_number(series):
    s = pd.to_numeric(series.str.replace(r"[^\d]", "", regex=True), errors='coerce')
    return s > 0

def is_valid_date(series):
    return pd.to_datetime(series, errors='coerce', dayfirst=True).notna()

# === Main Validation Dispatcher ===
def validate_fields(df):
    rules = {
        'Customer Name': lambda s: is_valid_name(s, 3),
        'CNIC / ID': is_valid_cnic,
        'ID Exp. Date': None,  # handled separately
        'Contact Number - M': is_valid_phone,
        'Contact Number - LL': is_valid_phone,
        'KYC - Expected Debit Amount': is_valid_amount,
        'KYC - Expected Debit Number': is_valid_number,
        'KYC - Expected Credit Amount': is_valid_amount,
        'KYC - Expected Credit Number': is_valid_number,
        'NOK 01': lambda s: is_valid_name(s, 4),
        'NOK 01 - CNIC': is_valid_cnic,
        'NOK 01- Relationship': lambda s: is_valid_name(s, 2),
        'Mother/ Maiden Name': lambda s: is_valid_name(s, 2),
        'Father / Spouse Name': lambda s: is_valid_name(s, 2),
        'Purpose of Account': lambda s: is_valid_name(s, 4),
        'Current Address': lambda s: s.str.len() >= 10,
        'Permanent Address': lambda s: s.str.len() >= 10,
        'Account Address': lambda s: s.str.len() >= 10,
        'Account Number': lambda s: s.str.fullmatch(r"\d{16}"),
        'Customer ID': lambda s: s.str.fullmatch(r"\d{7}"),
        'Account Opened On': is_valid_date,
        'ID Type': lambda s: s.str.upper().isin(["CNIC", "SNIC", "NICOP", "POC", "CNIC/SNIC/NICOP/POC"]),
        'Customer Risk Category': lambda s: s.str.upper().isin(["LOW", "MEDIUM", "HIGH"]),
        'Risk Category - TMS': lambda s: s.str.upper().isin(["LOW", "MEDIUM", "HIGH"]),
        'Last Succ. Veri. Type': lambda s: s.str.upper().isin([
            "CUSTOMER LEVEL", "LOS", "BIOMETRIC WITHDRAWAL SUBSCRIPTION"])
    }

    issue_coords = []
    error_counts = {}
    error_rows = set()
    col_map = {col: idx for idx, col in enumerate(df.columns)}

    for col, func in rules.items():
        if col in df.columns:
            if col == 'ID Exp. Date':
                dates = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                valid = dates >= pd.Timestamp("2025-06-30")
            else:
                valid = func(df[col])
            invalid = ~valid.fillna(False)
            error_counts[col] = invalid.sum()
            error_rows.update(df.index[invalid].tolist())
            issue_coords.extend([(i, col_map[col]) for i in df.index[invalid]])

    return issue_coords, error_counts, error_rows

# === Core Processing ===
def clean_and_highlight(filepath):
    try:
        start = time.time()
        df = pd.read_csv(filepath, encoding='latin1', dtype=str).fillna("")
        df.columns = df.columns.str.strip()

        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].astype(str).str.strip()

        issue_coords, error_counts, error_rows = validate_fields(df)
        output_path = os.path.splitext(filepath)[0] + "_highlighted.xlsx"

        # Group errors by year
        error_by_year = {}
        if 'Account Opened On' in df.columns:
            opened_dates = pd.to_datetime(df['Account Opened On'], errors='coerce', dayfirst=True)
            for idx in error_rows:
                d = opened_dates.iloc[idx]
                if pd.notnull(d):
                    key = d.strftime("%Y")
                    error_by_year[key] = error_by_year.get(key, 0) + 1

        # Write Excel
        with pd.ExcelWriter(output_path, engine='xlsxwriter', datetime_format='yyyy-mm-dd') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            wb = writer.book
            ws = writer.sheets['Data']
            yellow = wb.add_format({'bg_color': '#FFFF00'})

            for row_idx, col_idx in issue_coords:
                ws.write(row_idx + 1, col_idx, df.iat[row_idx, col_idx], yellow)

            # Summary Sheet
            summary_ws = wb.add_worksheet("Summary")
            summary_ws.write(0, 0, "Field")
            summary_ws.write(0, 1, "Error Count")
            for idx, (field, count) in enumerate(error_counts.items(), start=1):
                summary_ws.write(idx, 0, field)
                summary_ws.write(idx, 1, count)

            if error_counts:
                pie = wb.add_chart({'type': 'pie'})
                pie.add_series({
                    'categories': ['Summary', 1, 0, len(error_counts), 0],
                    'values': ['Summary', 1, 1, len(error_counts), 1],
                    'data_labels': {'percentage': True}
                })
                pie.set_title({'name': 'Field Error Distribution'})
                summary_ws.insert_chart('D2', pie)

            if error_by_year:
                year_ws = wb.add_worksheet("Errors by Year")
                year_ws.write(0, 0, "Year")
                year_ws.write(0, 1, "Error Count")
                for idx, (year, count) in enumerate(sorted(error_by_year.items()), start=1):
                    year_ws.write(idx, 0, year)
                    year_ws.write(idx, 1, count)

                bar = wb.add_chart({'type': 'column'})
                bar.add_series({
                    'categories': ['Errors by Year', 1, 0, len(error_by_year), 0],
                    'values': ['Errors by Year', 1, 1, len(error_by_year), 1],
                    'data_labels': {'value': True}
                })
                bar.set_title({'name': 'Yearly Error Count'})
                bar.set_x_axis({'name': 'Year'})
                bar.set_y_axis({'name': 'Count'})
                year_ws.insert_chart('D2', bar)

        elapsed = round(time.time() - start, 2)
        messagebox.showinfo("Complete", f"Done in {elapsed} sec\nSaved to:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

# === GUI ===
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        clean_and_highlight(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("CSV Dirty Data Checker")
    root.geometry("400x150")
    tk.Label(root, text="Select a CSV file to check for dirty data").pack(pady=10)
    tk.Button(root, text="Select CSV", command=select_file).pack(pady=5)
    root.mainloop()
