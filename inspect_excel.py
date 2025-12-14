import pandas as pd
import os

import pandas as pd
import os

def inspect_input():
    f = "Excel_Logic_input_07-1 i-070936-67-T-0701-Type6-8x6-(For Education)-Ver. 1.05.xls"
    print(f"--- Inspecting Sheet1 07-1 ---")
    try:
        # Read Input
        df = pd.read_excel(f, sheet_name='Input', header=None, nrows=50)
        with open("excel_dump_07.txt", "w", encoding='utf-8') as f_out:
            f_out.write(df.to_string())
        print("Dumped Input to excel_dump_07.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_input()
