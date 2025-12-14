import pandas as pd
import os

class InputReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {}
        self._read_excel()

    def _read_excel(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        try:
            # Read 'Input' sheet or 'API650'
            sheet_name = 'Input'
            is_efrt_layout = False
            try:
                df = pd.read_excel(self.file_path, sheet_name='Input', header=None, nrows=60)
            except ValueError:
                # Try API650 (Common in EFRT files)
                try:
                    sheet_name = 'API650'
                    is_efrt_layout = True
                    df = pd.read_excel(self.file_path, sheet_name='API650', header=None, nrows=60)
                except ValueError:
                    raise ValueError("Could not find 'Input' or 'API650' sheet.")
            
            # Helper to get value safely
            def get_val(row, col):
                if row >= df.shape[0] or col >= df.shape[1]:
                    return 0.0
                val = None
                try:
                    val = df.iloc[row, col]
                    if pd.isna(val):
                        return 0.0
                    if isinstance(val, str):
                        val = val.strip()
                    return float(val)
                except ValueError:
                    return 0.0
                except Exception:
                    return 0.0

            # Geometry
            if is_efrt_layout:
                # Indices from locate_main_cells.py for 'API650' sheet
                self.data['D'] = get_val(12, 5) / 1000.0 # mm to m
                self.data['H'] = get_val(15, 10) / 1000.0 # mm to m (Col 10!)
                self.data['G'] = get_val(16, 10) # SG (Col 10!)
                self.data['HD'] = self.data['H'] # Assume H=HD for now
                self.data['HT'] = self.data['H']
                
                # Material might be different location too, defaulting a bit
                self.data['CA'] = get_val(38, 3) # Check if valid
                self.data['CA_bottom'] = get_val(44, 3)
                
            else:
                # Standard 'Input' sheet logic
                self.data['D'] = get_val(13, 5) / 1000.0 # mm to m
                self.data['H'] = get_val(14, 5) / 1000.0 # mm to m
                self.data['HD'] = get_val(15, 5) / 1000.0 # mm to m
                self.data['HT'] = get_val(16, 5) / 1000.0 # mm to m
                
                # Design Conditions
                self.data['G'] = get_val(23, 5)
                
                # Material & CA
                self.data['CA'] = get_val(38, 3) # mm
                # Bottom CA (Row 44 based on inspection mention, usually below Shell CA)
                # CA_bottom often at Row 40 or 44 depending on format. 
                # Original code said 40. Let's retry 44 if 40 is 0?
                val_40 = get_val(40, 3)
                val_44 = get_val(44, 3)
                self.data['CA_bottom'] = val_44 if val_44 > 0 else val_40
            
            # Dynamic Search for Roof Parameters
            roof_row_idx = -1
            for i in range(len(df)):
                val = str(df.iloc[i, 1]) # Check Col 1 (B)
                if 'Roof Plate' in val:
                    roof_row_idx = i
                    break
            
            if roof_row_idx != -1:
                self.data['CA_roof'] = get_val(roof_row_idx, 3)
                self.data['Roof_Material'] = str(df.iloc[roof_row_idx, 5])
                # Try multiple columns for thickness
                t_val = get_val(roof_row_idx, 37)
                if t_val == 0: t_val = get_val(roof_row_idx, 16)
                if t_val == 0: t_val = get_val(roof_row_idx, 14)
                self.data['Roof_Thickness'] = t_val
            else:
                self.data['CA_roof'] = 0.0
                self.data['Roof_Material'] = 'Unknown'
                self.data['Roof_Thickness'] = 0.0

            # Wind Parameters (Verified Indices)
            self.data['Wind_Velocity_3sec'] = get_val(18, 14) # Row 18: 3 sec Gust (10)
            self.data['Wind_Velocity_Basic'] = get_val(11, 14) # Row 11: Basic Wind Velocity (45)
            # Use Basic as primary if > 0, else 3sec
            self.data['Wind_Velocity'] = self.data['Wind_Velocity_Basic'] if self.data['Wind_Velocity_Basic'] > 0 else self.data['Wind_Velocity_3sec']
            
            # Factors at Rows 20-23, Col 14
            self.data['Kzt'] = get_val(20, 14)
            self.data['Kd'] = get_val(21, 14)
            self.data['G_wind'] = get_val(22, 14)
            self.data['Cf'] = get_val(23, 14)
            
            # Seismic Parameters (Verified Indices)
            self.data['S1'] = get_val(41, 16)
            self.data['S0'] = get_val(42, 16)
            self.data['SDS'] = get_val(45, 18)
            self.data['Z'] = get_val(28, 20)
            self.data['Site_Class'] = str(df.iloc[30, 18])
            self.data['I_seismic'] = get_val(31, 20)
            
            # Stresses
            self.data['Sd'] = get_val(55, 2) # MPa
            self.data['St'] = get_val(56, 2) # MPa
            
            # Pressures (mmH2O)
            self.data['P_design'] = get_val(31, 5)
            self.data['P_test'] = get_val(33, 5)
            
        except Exception as e:
            raise ValueError(f"Error parsing Excel file: {e}")

    def get_design_parameters(self):
        return self.data

    def get_shell_courses(self):
        """
        Reads the shell course definition table from the Input sheet.
        Returns a list of dictionaries with keys: 'Course', 'Material', 'Width', 'Thickness_Used'.
        """
        courses = []
        try:
            # Read rows 160-200 to cover all courses
            df = pd.read_excel(self.file_path, sheet_name='Input', header=None, skiprows=160, nrows=40, engine='openpyxl')
            
            for i, row in df.iterrows():
                if len(row) <= 16:
                    continue
                    
                course_name = str(row[11])
                
                # Shell Courses
                if 'shell' in course_name.lower() and 'plate' not in course_name.lower():
                    width = row[16]
                    material = row[13]
                    thickness = row[14]
                    
                    if pd.notna(width) and pd.notna(material):
                        courses.append({
                            'Course': course_name,
                            'Material': material,
                            'Width': float(width) / 1000.0, # mm to m
                            'Thickness_Used': float(thickness) if pd.notna(thickness) else 0.0
                        })
                        
                # Bottom Plate
                elif 'bottom' in course_name.lower() and 'plate' in course_name.lower():
                    self.data['Bottom_Plate'] = {
                        'Material': row[13],
                        'Thickness_Used': float(row[14]) if pd.notna(row[14]) else 0.0
                    }
                    
                # Annular Plate
                elif 'annular' in course_name.lower() and 'plate' in course_name.lower():
                    self.data['Annular_Plate'] = {
                        'Material': row[13],
                        'Thickness_Used': float(row[14]) if pd.notna(row[14]) else 0.0,
                        'Width': float(row[16]) / 1000.0 if pd.notna(row[16]) else 0.0
                    }
                                
        except Exception as e:
            print(f"Error reading shell courses: {e}")
            
        return courses

    def get_efrt_parameters(self):
        """
        Reads EFRT parameters from the 'Floating roof ' sheet.
        Returns a dictionary with keys matching EFRTDesign inputs.
        """
        efrt_data = {}
        sheet_name = 'Floating roof ' 
        
        try:
            # Check if sheet exists first (requires peek or try-catch)
            # Use pandas ExcelFile to check sheets if not already known, 
            # but simpler to just try reading.
            
            # Read 'Floating roof ' sheet
            # Note: Header=None, so 0-indexed rows match text file line numbers roughly (Line 1 = Row 0)
            df = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None, nrows=600)
            
            def get_val(row, col):
                try:
                    val = df.iloc[row, col]
                    if pd.isna(val): return 0.0
                    return float(val)
                except:
                    return 0.0

            # Mapped Indices from locate_efrt_cells.py
            # Note: These are 0-indexed row/col from dataframe
            
            efrt_data['H_outer'] = get_val(36, 10) # 800
            efrt_data['H_inner'] = get_val(37, 10) # 650
            efrt_data['Width_Pontoon'] = get_val(38, 10) # 1700
            efrt_data['Gap_Rim'] = get_val(39, 10) # 200
            efrt_data['N_Pontoons'] = get_val(42, 10) # 16
            
            efrt_data['T_Rim_Outer'] = get_val(52, 10) # 8
            # Inferred locations for others based on dump structure
            efrt_data['T_Rim_Inner'] = get_val(53, 10) # 10
            efrt_data['T_Pon_Top'] = get_val(54, 10) # 6
            efrt_data['T_Pon_Btm'] = get_val(55, 10) # 6
            efrt_data['T_Bulkhead'] = get_val(56, 10) # 8
            efrt_data['T_Deck'] = get_val(57, 10) # 8
            
            # Tank Diameter from this sheet (Critical for consistency)
            efrt_data['Tank_D'] = get_val(23, 10) / 1000.0 # mm to m (Row 23)
            
            # Rafter Size (Row 6, Col 8)
            # Note: 0-indexed, so Row 6 is index 6 (actually line 7) or index 5?
            # locate_rafter.py found it at Row 6. Python iloc is 0-indexed.
            # Convert "L 75 x 75 x 6" to string.
            try:
                val = df.iloc[6, 8] # Row 6, Col 8
                efrt_data['Rafter_Size'] = str(val).strip() if pd.notna(val) else ""
            except:
                efrt_data['Rafter_Size'] = ""
            
            # Rim Diameters (Optional, good for check)
            efrt_data['D_Rim_Outer'] = get_val(44, 10)
            efrt_data['D_Rim_Inner'] = get_val(45, 10)
            
            # Roof Leg Parameters (Rows 550-551)
            efrt_data['Leg_OD'] = get_val(550, 10) # 88.9
            efrt_data['Leg_Thk'] = get_val(551, 10) # 7.62
            
            return efrt_data
            
        except Exception as e:
            print(f"Warning: Could not read '{sheet_name}' sheet. EFRT data might be missing. {e}")
            return {}

if __name__ == "__main__":
    # Test
    f = "Excel_Logic_input_03-1 i-070936-67-T-0319-0327-Type4-78x18-(For_Education)-Ver. 1.05.xls"
    try:
        reader = InputReader(f)
        print("Read Parameters:")
        for k, v in reader.get_design_parameters().items():
            print(f"{k}: {v}")
            
        print("\nShell Courses:")
        courses = reader.get_shell_courses()
        for c in courses:
            print(c)
            
        print("\nBottom/Annular Plate Data:")
        if 'Bottom_Plate' in reader.data:
            print(f"Bottom Plate: {reader.data['Bottom_Plate']}")
        if 'Annular_Plate' in reader.data:
            print(f"Annular Plate: {reader.data['Annular_Plate']}")
    except Exception as e:
        print(e)
