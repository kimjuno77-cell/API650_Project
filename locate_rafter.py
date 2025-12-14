
import pandas as pd

def locate_rafter():
    f = "EFRT Calculation.xls"
    sheet = "Floating roof "
    print(f"--- Locating Rafter in '{sheet}' ---")
    
    try:
        df = pd.read_excel(f, sheet_name=sheet, header=None)
        
        keywords = {
            'Rafter': 'Rafter Size'
        }
        
        for r in range(df.shape[0]):
            for c in range(df.shape[1]):
                val = str(df.iloc[r, c])
                for k, v in keywords.items():
                    if k in val:
                        # Scan next 10 columns for string value "L..."
                        value = None
                        val_col = -1
                        for offset in range(1, 10):
                            if c + offset < df.shape[1]:
                                cell_val = str(df.iloc[r, c + offset])
                                if 'L' in cell_val or 'x' in cell_val:
                                    value = cell_val.strip()
                                    val_col = c + offset
                                    break
                        
                        if value:
                            print(f"Found '{k}' at Row {r}, Col {val_col}: '{value}'")
                        else:
                            # Maybe value is in the same cell?
                            pass

    except Exception as e:
        print(e)

if __name__ == "__main__":
    locate_rafter()
