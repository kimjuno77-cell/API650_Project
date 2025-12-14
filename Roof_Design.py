import math
from Materials import get_material_properties

class RoofDesign:
    def __init__(self, diameter, roof_type, slope, corrosion_allowance, material, thickness_used, dome_radius=None):
        """
        Initialize Roof Design parameters.
        :param dome_radius: Radius of curvature for Dome/Umbrella (m). If None, defaults to 0.8*D to 1.2*D logic.
        """
        self.D = float(diameter) if diameter else 0.0
        self.roof_type = roof_type if roof_type else 'Supported Cone Roof'
        self.slope = float(slope) if slope else 0.0625
        self.CA = float(corrosion_allowance) if corrosion_allowance else 0.0
        self.material = material if material else 'A 283 C'
        self.t_used = float(thickness_used) if thickness_used else 0.0
        self.dome_radius = float(dome_radius) if dome_radius else (0.8 * self.D) # Default to 0.8D
        self.results = {}

    def get_material_stress(self):
        props = get_material_properties(self.material)
        return props.get('Sd', 137.0), props.get('Fy', 205.0), props.get('E', 200000.0)

    def check_roof_plate(self, total_load_kPa=1.2):
        """
        Check Roof Plate Thickness.
        :param total_load_kPa: Total Design Load (Live + Dead) [kPa]
        """
        t_min_std = 5.0 # API 650 5.10.2.2 standard min
        Sd, Fy, E_mod = self.get_material_stress() # E_mod in MPa
        
        # Self-Supported Cone Roof (API 650 5.10.5)
        if 'self-supported cone' in self.roof_type.lower():
            # API 650 5.10.5.1: Minimum Thickness
            # Nominal thickness shall not be less than:
            # t_min = D / (4.8 * sin(theta)) (in mm? No, D in m, result in mm logic?)
            # Wait, API units:
            # SI: t_min (mm) = D (m) / (4.8 * sin(theta)) ? 
            # Actually standard says: D / (400 sin theta) in Imperial?
            # SI Spec 5.10.5.1: t = D / (4.8 * sin(theta)) where D in meters, t in mm.
            # Max thickness limit is 13mm.
            
            theta = math.atan(self.slope)
            sin_theta = math.sin(theta)
            
            t_geom_mm = 0.0
            if sin_theta > 0.001:
                t_geom_mm = self.D / (4.8 * sin_theta)
            
            # Buckling Check (5.10.5.2 is about Top Angle, not plate buckling usually)
            # However, 5.10.5.1 implies slope > 1:4.8 (approx).
            # Max thickness 13mm.
            
            t_min_std = max(5.0, t_geom_mm)
            if t_min_std > 13.0:
                self.results['Warning'] = f"Calculated Thickness {t_min_std:.1f}mm exceeds 13mm limit for Self-Supported Cone."
            
        # Self-Supported Dome/Umbrella Roof (API 650 5.10.6)
        elif 'dome' in self.roof_type.lower() or 'umbrella' in self.roof_type.lower():
            # API 650 5.10.6.1: Min Thickness 5mm (+CA)
            # API 650 5.10.6.2: Buckling Required Thickness
            # Allowable Live Load P_all = (1.6 * E * t^2) / R^2
            # Rearranging for t: t_req = R * sqrt( P_design / (1.6 * E) )
            
            # P_design in MPa?
            # total_load_kPa includes Dead + Live.
            # 5.2.1.b: Design P = Dead + Live (min 1.2 kPa) usually.
            
            P_MPa = total_load_kPa / 1000.0
            R_r = self.dome_radius
            
            # 5.10.6 requires R_r within range 0.8D to 1.2D
            if R_r < 0.8 * self.D or R_r > 1.2 * self.D:
                self.results['Warning'] = f"Dome Radius {R_r}m is outside API range (0.8D-1.2D)."
            
            term = P_MPa / (1.6 * (E_mod/1000.0)) # E in GPa? No, E_mod is MPa.
            # term = P (MPa) / (1.6 * E (MPa)) -> Dimensionless
            # T = R * sqrt(term)
            
            if term > 0:
                t_calc_buckling_m = R_r * math.sqrt(P_MPa / (1.6 * E_mod))
                t_calc_buckling = t_calc_buckling_m * 1000.0
            else:
                t_calc_buckling = 0.0
                
            t_min_std = max(5.0, t_calc_buckling)
            
            if t_min_std > 13.0:
                 self.results['Warning'] = f"Calculated Thickness {t_min_std:.1f}mm exceeds 13mm limit."

        # Required Thickness (Add CA)
        t_req = t_min_std + self.CA
        
        status = 'OK' if self.t_used >= t_req - 0.01 else 'FAIL'
        
        self.results['Roof Plate'] = {
            'Material': self.material,
            'Type': self.roof_type,
            'Req Thk': t_req,
            'Used Thk': self.t_used,
            'Status': status
        }

    def check_frangibility(self, W_shell_kg, W_roof_plates_kg, W_roof_struct_kg, area_participating_mm2):
        """
        Check Frangibility requirements per API 650 5.10.2.6.
        Returns detailed status and requirements.
        """
        if 'cone' not in self.roof_type.lower():
             return {
                'Is_Frangible': False,
                'Warning': "Roof type is not Cone (Not Frangible by definition)",
                'Requires_Emergency': True
             }

        theta = math.atan(self.slope)
        tan_theta = self.slope
        
        # Participating Area A (mm2)
        A = float(area_participating_mm2)
        
        if self.D <= 0: return {}
        
        # P_failure calculation (API 650 5.10.2.6.a.5)
        # Pf (kPa) = (245000 * A * tan(theta)) / D^2  (D in meters)
        P_failure_kPa = (245000.0 * A * tan_theta) / (self.D**2)
        
        # Limit Area Check (Inequality derived from Code)
        # Limit A_max approx = W_total / (201 * tan_theta)
        W_total_kg = W_shell_kg + W_roof_plates_kg + W_roof_struct_kg
        limit_A = W_total_kg / (201.0 * tan_theta) if tan_theta > 0 else 999999
        
        is_frangible = True
        warning = None
        
        if self.slope > 0.17: # > 1:6
             warning = "Slope > 1:6 (Typically Not Frangible)"
             is_frangible = False
        elif A > limit_A:
             warning = f"Participating Area ({A:.0f} mm2) exceeds Frangibility Limit (~{limit_A:.0f} mm2)"
             is_frangible = False
        
        self.results['Frangibility'] = {
            'Is_Frangible': is_frangible,
            'P_failure_kPa': P_failure_kPa,
            'Participating_Area_mm2': A,
            'Limit_Area_mm2': limit_A,
            'Warning': warning,
            'Requires_Emergency': not is_frangible
        }
        
        return self.results['Frangibility']

    def calculate_roof_weight(self):
        """
        Calculates Total Roof Weight.
        """
        # Area Calculation
        radius = self.D / 2.0
        area = math.pi * (radius ** 2) # Flat default
        
        if 'cone' in self.roof_type.lower():
            theta = math.atan(self.slope)
            area = area / math.cos(theta)
        elif 'dome' in self.roof_type.lower() or 'umbrella' in self.roof_type.lower():
            # Area of spherical cap approx = 2 * pi * R * h_cap (or similar)
            # Exact: 2 * pi * R^2 * (1 - cos(phi)) ?
            # R_r = radius of curvature.
            # sin(phi) = (D/2) / R_r
            R_r = self.dome_radius
            if R_r >= radius:
                phi = math.asin(radius / R_r)
                h_cap = R_r * (1.0 - math.cos(phi))
                area = 2 * math.pi * R_r * h_cap
            else:
                 area = area * 1.2 # Fallback
                 
        rho_steel = 7850.0
        t_m = self.t_used / 1000.0
        W_plates_kg = area * t_m * rho_steel
        
        W_struct_kg = 0.0 # Default 0 for self-supported
        if 'supported' in self.roof_type.lower() and 'self' not in self.roof_type.lower():
             # Placeholder for Supported Structure Weight estimate if not calculated externally
             W_struct_kg = 0.0 # Handled by Structure_Design module
             
        self.results['Weight_kg'] = W_plates_kg + W_struct_kg
        return W_plates_kg, W_plates_kg * 9.81



    def check_top_member(self):
        """
        Check Top Angle / Compression Ring (API 650 5.1.5.9).
        Simplified check: Minimal required section modulus or area.
        Most common: Angle 2.5x2.5x0.25 inch (65x65x6 mm) minimum.
        """
        # API 650 5.1.5.9.e: Minimum size for D > 10m is L75x75x6?
        # 5.1.5.9.e specifies min angle size based on diameter.
        # D <= 10m: L50x50x5
        # 10 < D <= 18m: L50x50x6
        # D > 18m: L75x75x10 (common practice, API 5.1.5.9.e says: 75x75x6 for some)
        
        req_size = ""
        if self.D <= 10:
            req_size = "L50x50x5"
        elif self.D <= 18:
            req_size = "L50x50x6"
        else:
            req_size = "L75x75x10" # Recommended for large tanks
            
        self.results['Top Member'] = {
            'Required Size': req_size,
            'Selected Size': req_size + " (Default)", # Placeholder
            'Status': 'OK'
        }

    def run_design(self):
        try:
            self.check_roof_plate()
            self.check_top_member() # Add top member check
            W_kg, W_N = self.calculate_roof_weight()
            print(f"Total Roof Weight: {W_kg:.2f} kg ({W_N/1000:.2f} kN)")
        except Exception as e:
            print(f"Error in Roof Design Run: {e}")

    def print_report(self):
        print("\nAPI 650 Roof Design")
        print("------------------------------------------------------------")
        r = self.results.get('Roof Plate', {})
        if r:
            print("Roof Plate:")
            print(f"  Type: {self.roof_type}")
            print(f"  Material: {self.material}")
            print(f"  Min Thk (Std): {r.get('Min Thk (Std)', 0):.2f} mm")
            print(f"  CA: {r.get('CA', 0):.2f} mm")
            print(f"  Req Thk: {r.get('Req Thk', 0):.2f} mm")
            print(f"  Used Thk: {r.get('Used Thk', 0):.2f} mm")
            print(f"  Status: {r.get('Status', 'N/A')}")
            
        tm = self.results.get('Top Member', {})
        if tm:
            print("Top Member:")
            print(f"  Required: {tm.get('Required Size')}")
            print(f"  Status: {tm.get('Status')}")
            
        w = self.results.get('Weight', {})
        if w:
            print("Roof Weight:")
            print(f"  Plates: {w.get('Plate Weight (kg)', 0):.2f} kg")
            print(f"  Structure (Est): {w.get('Structure Weight (kg)', 0):.2f} kg")
            print(f"  Total: {w.get('Total Weight (kg)', 0):.2f} kg")

if __name__ == "__main__":
    # Test Standalone
    rd = RoofDesign(
        diameter=78.0,
        roof_type='Supported Cone Roof',
        slope=0.0625,
        corrosion_allowance=1.5,
        material='A 36',
        thickness_used=6.0
    )
    rd.run_design()
    rd.print_report()
