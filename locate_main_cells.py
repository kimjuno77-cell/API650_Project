
import pandas as pd

def locate_main_cells():
    f = "EFRT Calculation.xls"
    sheet = "API650"
    print(f"--- Locating Cells in '{sheet}' ---")
    
    try:
        df = pd.read_excel(f, sheet_name=sheet, header=None)
        
        keywords = {
            'Inside diameter': 'D',
            'Specific gravity of operating liquid': 'SG',
            'Design pressure': 'P',
            'Tank height': 'H'
        }
        
        for r in range(df.shape[0]):
            for c in range(df.shape[1]):
                val = str(df.iloc[r, c])
                for k, v in keywords.items():
                    if k in val:
                        # Scan next 15 columns for value
                        value = None
                        val_col = -1
                        for offset in range(1, 15):
                            if c + offset < df.shape[1]:
                                cell_val = df.iloc[r, c + offset]
                                try:
                                    f_val = float(cell_val)
                                    if not pd.isna(cell_val):
                                        value = f_val
                                        val_col = c + offset
                                        break
                                except:
                                    pass
                        
                        if value is not None:
                            print(f"Found '{k}' ({v}) at Row {r}, Col {val_col}: {value}")
                        else:
                            print(f"Found Label '{k}' at Row {r}, Col {c} but NO Value found.")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    locate_main_cells()
