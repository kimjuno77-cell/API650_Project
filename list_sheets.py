
import pandas as pd

f = "Excel_Logic_input_03-1 i-070936-67-T-0319-0327-Type4-78x18-(For_Education)-Ver. 1.05.xls"
try:
    xl = pd.ExcelFile(f)
    print(xl.sheet_names)
except Exception as e:
    print(e)
