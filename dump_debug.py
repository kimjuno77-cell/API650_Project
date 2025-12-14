
import pandas as pd

def dump_debug():
    f = "EFRT Calculation.xls"
    try:
        xl = pd.ExcelFile(f)
        print(f"Sheet Names: {xl.sheet_names}")
        
        sheet = xl.sheet_names[0] # Pick first one
        print(f"Reading first sheet: '{sheet}'")
        df = pd.read_excel(f, sheet_name=sheet, header=None, nrows=20)
        print(df.to_string())
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_debug()
