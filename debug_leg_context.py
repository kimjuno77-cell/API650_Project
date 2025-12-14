
import pandas as pd

def inspect_ranges():
    f = "EFRT Calculation.xls"
    sheet = "Floating roof "
    print(f"--- Inspecting Context in '{sheet}' ---")
    
    try:
        df = pd.read_excel(f, sheet_name=sheet, header=None)
        
        print("\n--- Rows 60-70 ---")
        print(df.iloc[60:70].to_string())
        
        print("\n--- Rows 545-555 ---")
        print(df.iloc[545:555].to_string())
        
    except Exception as e:
        print(e)

if __name__ == "__main__":
    inspect_ranges()
