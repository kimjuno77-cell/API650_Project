
import math
from Materials import get_material_properties

class BottomDesign:
    def __init__(self, diameter, corrosion_allowance, bottom_material_name='A 283 C', annular_material_name=None, stress_first_course=0.0):
        """
        API 650 Bottom and Annular Plate Design (Sections 5.4, 5.5).
        
        :param diameter: Tank Nominal Diameter (m)
        :param corrosion_allowance: Bottom CA (mm)
        :param bottom_material_name: Material for bottom plates
        :param annular_material_name: Material for annular plates (if applicable)
        :param stress_first_course: Stress in the first shell course (MPa) - used for Annular Plate check
        """
        self.D = diameter
        self.CA = corrosion_allowance
        self.mat_bottom = bottom_material_name
        self.mat_annular = annular_material_name if annular_material_name else bottom_material_name
        self.S_first = stress_first_course
        self.results = {}

    def calculate_bottom_thickness(self):
        """
        API 650 5.4.1: Minimum nominal thickness = 6mm (exclusive of CA).
        """
        min_nominal = 6.0
        t_req = min_nominal + self.CA
        return t_req

    def calculate_annular_thickness(self, H, G):
        """
        API 650 5.5.3 / Table 5-1.
        Annular plate thickness depends on Hydrostatic Test Stress in first course.
        """
        # Placeholder for complex logic, simplified in run_design
        t_annular_req = 6.0 + self.CA
        return max(t_annular_req, 6.0)

    def calculate_annular_width(self, t_shell_bot_mm, projection_out_mm=50.0):
        """
        API 650 5.5.2: Minimum Radial Width.
        Radial width >= 600mm between inside of shell and any lap weld.
        Total Radial Width = 600mm + t_shell + projection_out
        """
        # Min Inside Width = 600 mm
        L_inside = 600.0
        # Total Required
        L_total = L_inside + t_shell_bot_mm + projection_out_mm
        return L_total

    def run_design(self, H=10.0, G=1.0, use_annular=False, t_shell_bot_mm=0.0, user_width=0.0, user_thk=0.0):
        # 1. Standard Bottom Plate
        t_bottom_req = self.calculate_bottom_thickness()
        
        self.results['Bottom Plate'] = {
            'Material': self.mat_bottom,
            'CA': self.CA,
            'Req Thk (mm)': t_bottom_req,
            'Notes': 'Minimum 6mm + CA (API 650 5.4.1)'
        }
        
        # 2. Annular Plate Logic
        # API 650 5.5.1: Required if Stress > 170 MPa (approx for Group IV+ or high stress)
        # We separate "Is Required" from "Is Applied".
        
        is_required = False
        if self.S_first > 170: 
             is_required = True
             
        annular_res = {}
        
        if use_annular:
             # Logic for Thickness
             t_annular_req = 6.0 + self.CA
             if self.S_first > 190: t_annular_req = max(t_annular_req, 8.0 + self.CA) # Table 5-1 simplified
             if self.S_first > 210: t_annular_req = max(t_annular_req, 11.0 + self.CA)
             
             min_width = self.calculate_annular_width(t_shell_bot_mm)
             
             status = 'Applied'
             note = 'Dimensions OK'
             warning = None
             
             # Validation Checks if inputs provided
             if user_width > 0 and user_width < min_width:
                 warning = f"Applied Width ({user_width}mm) < Minimum Required ({min_width:.1f}mm)"
                 status = 'Insufficient Width'
             
             if user_thk > 0 and user_thk < t_annular_req:
                 w_msg = f"Applied Thickness ({user_thk}mm) < Minimum Required ({t_annular_req:.1f}mm)"
                 if warning: warning += " | " + w_msg
                 else: warning = w_msg
                 status = 'Insufficient Thickness'

             annular_res = {
                'Required?': 'Yes' if is_required else 'No',
                'Applied': True,
                'Min Thk (mm)': t_annular_req,
                'Min Width (mm)': min_width,
                'Applied Thk (mm)': user_thk if user_thk > 0 else t_annular_req,
                'Applied Width (mm)': user_width if user_width > 0 else min_width,
                'Status': status,
                'Notes': 'Min Width = 600mm (inside) + t_shell + 50mm (proj)',
                'Calculation Details': {
                    'Stress in First Shell Course (S_d)': f"{self.S_first:.1f} MPa",
                    'Governing Table 5-1 Limit': '170/190/210 MPa',
                    'Calculated t_shell_bot': f"{t_shell_bot_mm:.2f} mm",
                    'Min Inside Radial Width': '600 mm',
                    'Min Projection': '50 mm',
                    'Formula_Width': f"600 + {t_shell_bot_mm:.2f} + 50 = {min_width:.2f} mm",
                    'Formula_Thk': f"Base 6.0mm + CA ({self.CA}mm) = {6.0+self.CA}mm (Adjusted for Stress > {190 if self.S_first>190 else 170})"
                }
             }
             if warning: annular_res['Warning'] = warning
             
        else:
             # Not Applied
             annular_res = {
                'Required?': 'Yes' if is_required else 'No',
                'Applied': False,
                'Min Thk (mm)': 6.0 + self.CA, # Default min if applied
                'Min Width (mm)': 0.0,
                'Status': 'Not Applied'
             }
             
             if is_required:
                 annular_res['Warning'] = "Annular Plate is REQUIRED by API 650 (Stress > 170 MPa) but is NOT applied."
                 annular_res['Status'] = "MISSING (REQUIRED)"

        self.results['Annular Plate'] = annular_res
        return self.results
