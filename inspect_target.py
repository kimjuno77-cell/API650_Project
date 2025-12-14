import pandas as pd
import os

def inspect_target_sample(file_path):
    print(f"--- Inspecting Target Sample: {os.path.basename(file_path)} ---")
    try:
        xls = pd.ExcelFile(file_path, engine='xlrd')
        print(f"Sheet Names: {xls.sheet_names}")
        
        # 'Shell' or 'CalShell' seems like a likely sheet name for results
        sheets_to_check = ['Shell', 'CalShell', 'Output', 'Report']
        
        found_sheet = None
        for s in xls.sheet_names:
            if any(x in s for x in sheets_to_check):
                found_sheet = s
                break
        
        if not found_sheet and len(xls.sheet_names) > 0:
            found_sheet = xls.sheet_names[0] # Fallback
            
        if found_sheet:
            print(f"\n[Sheet: {found_sheet}]")
            df = pd.read_excel(xls, sheet_name=found_sheet, header=None, nrows=50)
            print(df.to_string())
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

import pandas as pd
import os

def inspect_target_sample(file_path):
    print(f"--- Inspecting Target Sample: {os.path.basename(file_path)} ---")
    try:
        xls = pd.ExcelFile(file_path, engine='xlrd')
        print(f"Sheet Names: {xls.sheet_names}")
        
        # 'Shell' or 'CalShell' seems like a likely sheet name for results
        sheets_to_check = ['Shell', 'CalShell', 'Output', 'Report']
        
        found_sheet = None
        for s in xls.sheet_names:
            if any(x in s for x in sheets_to_check):
                found_sheet = s
                break
        
        if not found_sheet and len(xls.sheet_names) > 0:
            found_sheet = xls.sheet_names[0] # Fallback
            
        if found_sheet:
            print(f"\n[Sheet: {found_sheet}]")
            df = pd.read_excel(xls, sheet_name=found_sheet, header=None, nrows=50)
            print(df.to_string())
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    f = "Target_Sample_output_03-2 o-070936-67-T-0319-0327-Type4-78x18-(For_Education)-Ver. 1.05.xls"
    if os.path.exists(f):
        try:
            xls = pd.ExcelFile(f, engine='xlrd')
            print(f"Sheet Names (first 20): {xls.sheet_names[:20]}")
            
            # Inspect Ch_3 rows 60-120
            if 'Ch_3' in xls.sheet_names:
                print(f"--- Inspecting Ch_3 (Rows 60-120) ---")
                df = pd.read_excel(xls, sheet_name='Ch_3', header=None, skiprows=60, nrows=60)
                print(df.to_string())
                print("="*40)

            # Check Ch_2
            if 'Ch_2' in xls.sheet_names:
                print(f"--- Inspecting Target Sample Ch_2 (Design Data) ---")
                df = pd.read_excel(xls, sheet_name='Ch_2', header=None, nrows=60)
                print(df.to_string())
                print("="*40)

        except Exception as e:
            print(e)
