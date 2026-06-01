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

    def calculate_bottom_thickness(self, apply_annex_j=False):
        """
        API 650 5.4.1 / J.3.1: Minimum nominal thickness.
        """
        min_nominal = 6.0 # Both standard 5.4.1 and Annex J.3.1 specify 6mm min thickness for carbon steel bottom
        t_req = min_nominal + self.CA
        return t_req

    def calculate_annular_width(self, t_shell_bot_mm, projection_out_mm=50.0):
        """
        API 650 5.5.2: Minimum Radial Width (for lap weld).
        """
        L_inside = 600.0
        L_total = L_inside + t_shell_bot_mm + projection_out_mm
        return L_total

    def run_design(self, H=10.0, G=1.0, use_annular=False, t_shell_bot_mm=0.0, user_width=0.0, user_thk=0.0, apply_annex_j=False, annular_joint_type="Lap-Welded"):
        # 1. Standard / Annex J Bottom Plate
        t_bottom_req = self.calculate_bottom_thickness(apply_annex_j)
        
        bottom_notes = 'Minimum 6mm + CA (API 650 5.4.1)'
        bottom_warnings = []
        
        if apply_annex_j:
            bottom_notes = 'Annex J Shop-Assembled: Minimum 6mm + CA (J.3.1). Bottom joints must be butt-welded (J.3.2).'
            if self.D > 6.0:
                bottom_warnings.append(f"🚨 [ANNEX J SCOPE FAIL] Tank nominal diameter ({self.D:.3f} m) exceeds the 6.0 m (20 ft) shop-assembled limit in API 650 J.1.2.")
        
        self.results['Bottom Plate'] = {
            'Material': self.mat_bottom,
            'CA': self.CA,
            'Req Thk (mm)': t_bottom_req,
            'Notes': bottom_notes,
            'Warnings': bottom_warnings
        }
        
        # 2. Annular Plate Logic
        # API 650 5.5.1: Required if Stress > 170 MPa
        is_required = self.S_first > 170.0
        annular_res = {}
        
        if use_annular:
            t_annular_req = 6.0 + self.CA
            if self.S_first > 190: t_annular_req = max(t_annular_req, 8.0 + self.CA)
            if self.S_first > 210: t_annular_req = max(t_annular_req, 11.0 + self.CA)
            
            # tb is the nominal thickness of the annular plate (in mm)
            tb = user_thk if user_thk > 0 else t_annular_req
            H_val = H if H > 0 else 1.0
            G_val = G if G > 0 else 1.0
            
            # API 650 5.5.2 calculated radial width: L_calc = 215 * tb / sqrt(H * G)
            L_calc = 215.0 * tb / math.sqrt(H_val * G_val)
            
            # Total Widths
            min_width_lap = 600.0 + t_shell_bot_mm + 50.0
            min_width_calc = L_calc + t_shell_bot_mm + 50.0
            
            if annular_joint_type == "Butt-Welded":
                min_width = min_width_calc
                note = f"Butt-Welded Annular Plate (API 650 5.5.5): Required radial width = {min_width:.1f} mm. Joint must be full-penetration butt welded with square or V-groove preparation and a min. 3mm backing strip."
            else:
                min_width = max(min_width_lap, min_width_calc)
                note = f"Lap-Welded Annular Plate (API 650 5.5.2): Required radial width = {min_width:.1f} mm (governed by the larger of 600mm inside limit and calculated width L_calc)."
                
            status = 'Applied'
            warning = None
            
            # Validation Checks
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
                'Joint Type': annular_joint_type,
                'Min Thk (mm)': t_annular_req,
                'Min Width (mm)': min_width,
                'Applied Thk (mm)': user_thk if user_thk > 0 else t_annular_req,
                'Applied Width (mm)': user_width if user_width > 0 else min_width,
                'Status': status,
                'Notes': note,
                'Calculation Details': {
                    'Stress in First Shell Course (S_d)': f"{self.S_first:.1f} MPa",
                    'Calculated t_shell_bot': f"{t_shell_bot_mm:.2f} mm",
                    'Calculated Radial Width L_calc': f"215 * {tb:.1f} / sqrt({H_val:.3f} * {G_val:.3f}) = {L_calc:.1f} mm",
                    'Min Inside Radial Width (Lap-Welded)': '600 mm',
                    'Min Outer Projection': '50 mm',
                    'Formula_Width': f"L_calc ({L_calc:.1f} mm) + t_shell ({t_shell_bot_mm:.2f} mm) + 50 = {min_width_calc:.1f} mm",
                    'Formula_Thk': f"Base 6.0mm + CA ({self.CA}mm) = {6.0+self.CA}mm (Adjusted for Stress > {190 if self.S_first>190 else 170})"
                }
            }
            if warning: annular_res['Warning'] = warning
            
        else:
            # Not Applied
            annular_res = {
                'Required?': 'Yes' if is_required else 'No',
                'Applied': False,
                'Min Thk (mm)': 6.0 + self.CA,
                'Min Width (mm)': 0.0,
                'Status': 'Not Applied'
            }
            if is_required:
                annular_res['Warning'] = "Annular Plate is REQUIRED by API 650 (Stress > 170 MPa) but is NOT applied."
                annular_res['Status'] = "MISSING (REQUIRED)"

        self.results['Annular Plate'] = annular_res
        return self.results
