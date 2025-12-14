
import pandas as pd

def locate_cells():
    f = "EFRT Calculation.xls"
    sheet = "Floating roof " # Note space
    print(f"--- Locating Cells in '{sheet}' ---")
    
    try:
        df = pd.read_excel(f, sheet_name=sheet, header=None)
        
        keywords = {
            'Outer Rim Height': 'hor',
            'Inner Rim Height': 'hir',
            'Pontoon width': 'w',
            'No. of Pontoons': 'N',
            'Deck Plate Thickness': 'Td',
            'Rim Gap': 'Gap',
            'Design pressure': 'Pressure',
            'Outer Rim Thk': 'Tor',
            'Rafter': 'Rafter',
            'Post': 'Post',
            'Leg': 'Leg',
            'Pipe': 'Pipe',
            'Sleeve': 'Sleeve'
        }
        
        found = {}
        
        for r in range(df.shape[0]):
            for c in range(df.shape[1]):
                val = str(df.iloc[r, c])
                for k, v in keywords.items():
                    if k in val and k not in found:
                        # Found label, look for value in next few columns
                        # Usually label is at C, value is at C+2 or C+3
                        # Scan next 10 cols
                        value = None
                        val_col = -1
                        for offset in range(1, 15):
                            if c + offset < df.shape[1]:
                                cell_val = df.iloc[r, c + offset]
                                # Check if it's a number
                                try:
                                    f_val = float(cell_val)
                                    if not pd.isna(cell_val):
                                        value = f_val
                                        val_col = c + offset
                                        break
                                except:
                                    pass
                        
                        if value is not None:
                            found[k] = (r, val_col, value)
                            print(f"Found '{k}' at Row {r}, Col {val_col}: {value}")
                        else:
                            print(f"Found Label '{k}' at Row {r}, Col {c} but NO Value found nearby.")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    locate_cells()
