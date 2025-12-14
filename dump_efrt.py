
import pandas as pd

def dump_efrt():
    f = "EFRT Calculation.xls"
    print(f"--- Inspecting {f} ---")
    
    try:
        # Dump Input
        print("Reading Input...")
        df_in = pd.read_excel(f, sheet_name='Input', header=None, nrows=60)
        with open("efrt_dump_input.txt", "w", encoding="utf-8") as f_out:
            f_out.write(df_in.to_string())
            
        print("Reading CalRafter...")
        df_cal = pd.read_excel(f, sheet_name='CalRafter', header=None, nrows=60)
        with open("efrt_dump_cal.txt", "w", encoding="utf-8") as f_out:
            f_out.write(df_cal.to_string())
            
        print("Success.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_efrt()
