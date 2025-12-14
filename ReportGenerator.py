import pandas as pd
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, output_file_path):
        """
        Initialize Report Generator for Excel output.
        :param output_file_path: Path to save the .xlsx file.
        """
        self.output_file = output_file_path
        # Dictionary to store dataframes for each sheet
        self.sheets = {}
        
    def add_data(self, sheet_name, data_dict):
        """
        Add a dictionary of key-value pairs to a sheet.
        Useful for general parameters (Ch_2, Ch_4, etc.).
        """
        # Convert dict to DataFrame: Key | Value
        df = pd.DataFrame(list(data_dict.items()), columns=['Parameter', 'Value'])
        self.sheets[sheet_name] = df
        
    def add_table(self, sheet_name, data_list):
        """
        Add a list of dictionaries (table) to a sheet.
        Useful for Shell Courses (Ch_3).
        """
        if not data_list:
            df = pd.DataFrame()
        else:
            df = pd.DataFrame(data_list)
        self.sheets[sheet_name] = df
        
    def save(self):
        """
        Write all sheets to the Excel file.
        Ensures 'Summary' sheet is the first one if it exists.
        """
        try:
            # Ensure directory exists
            dirname = os.path.dirname(self.output_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            
            with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
                # Prepare Sheet Order: Summary first, then others
                sheet_names = list(self.sheets.keys())
                if 'Summary' in sheet_names:
                    sheet_names.remove('Summary')
                    sheet_names.insert(0, 'Summary')
                elif 'Ch_1_Summary' in sheet_names:
                    sheet_names.remove('Ch_1_Summary')
                    sheet_names.insert(0, 'Ch_1_Summary')
                
                if not sheet_names:
                    pd.DataFrame({'Info': ['No Data']}).to_excel(writer, sheet_name='Info')
                else:
                    for name in sheet_names:
                        self.sheets[name].to_excel(writer, sheet_name=name, index=False)
                    
            print(f"Excel Report saved to: {self.output_file}")
            
        except Exception as e:
            print(f"Error saving Excel report: {e}")
            # Fallback to csv if Excel fails (e.g. missing openpyxl)
            try:
                base, ext = os.path.splitext(self.output_file)
                for sheet_name, df in self.sheets.items():
                    csv_name = f"{base}_{sheet_name}.csv"
                    df.to_csv(csv_name, index=False)
                print("Saved as CSV files due to Excel error.")
            except Exception as e2:
                print(f"Error saving CSV fallback: {e2}")

if __name__ == "__main__":
    # Test
    rg = ReportGenerator("Test_Report.xlsx")
    rg.add_data("Ch_2_DesignData", {"D": 10, "H": 20})
    rg.add_table("Ch_3_Shell", [{"Course": 1, "Thickness": 10}, {"Course": 2, "Thickness": 8}])
    rg.save()
