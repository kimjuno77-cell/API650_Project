
import pandas as pd
import sys

def dump_excel(filename):
    print(f"--- Inspecting {filename} ---")
    try:
        xl = pd.ExcelFile(filename)
        print(f"Sheet Names: {xl.sheet_names}")
        
        # Dump 'Input' sheet if exists, otherwise first sheet
        target_sheet = 'Input' if 'Input' in xl.sheet_names else xl.sheet_names[0]
        
        print(f"Reading sheet: '{target_sheet}'")
        df = pd.read_excel(filename, sheet_name=target_sheet, header=None, nrows=60)
        
        out_name = "dump_" + filename.replace(" ", "_").replace(".xls", ".txt")
        with open(out_name, "w", encoding="utf-8") as f_out:
            f_out.write(df.to_string())
        print(f"Dumped to {out_name}")
        
        # Also dump 'CalRafter' or 'Summary' if they exist
        for special in ['CalRafter', 'Summary', 'Pontoon', 'Deck', 'Floating roof ']:
             if special in xl.sheet_names:
                 print(f"Reading sheet: '{special}'")
                 df_s = pd.read_excel(filename, sheet_name=special, header=None, nrows=60)
                 out_name_s = f"dump_{special}_{filename.replace(' ', '_').replace('.xls', '.txt')}"
                 with open(out_name_s, "w", encoding="utf-8") as f_out_s:
                    f_out_s.write(df_s.to_string())
                 print(f"Dumped to {out_name_s}")

    except Exception as e:
        print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    files = ["EFRT Calculation.xls", "Excel_Logic_Pontoon for 154-TK-005 to 007(0).xls"]
    for f in files:
        dump_excel(f)
