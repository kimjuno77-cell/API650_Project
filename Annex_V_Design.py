
import math

class AnnexVDesign:
    """
    API 650 Annex V: Design of Tanks for External Pressure.
    """
    def __init__(self, D, H, shell_courses, P_ext_mmH2O, E=200000, Fy=250):
        """
        :param D: Tank Diameter (m)
        :param H: Total Shell Height (m)
        :param shell_courses: List of [{'t_used': mm, 'Width': m}]
        :param P_ext_mmH2O: External Design Pressure (mmH2O)
        :param E: Modulus of Elasticity (MPa)
        :param Fy: Yield Strength (MPa)
        """
        self.D = D
        self.H = H
        self.courses = shell_courses
        self.P_ext_kpa = (P_ext_mmH2O * 9.80665) / 1000.0
        self.E = E
        self.Fy = Fy
        self.results = {}

    def calculate_pa_unstiffened(self, t_mm, L_m):
        """
        API 650 V.8.1.1 & V.8.1.2: Allowable External Pressure for Unstiffened Tank.
        """
        if t_mm <= 0 or L_m <= 0: return 0.0, 0.0
        
        D_mm = self.D * 1000.0
        L_mm = L_m * 1000.0
        
        # V.8.1.1 Elastic Buckling Pressure Pe
        # Pe = [2.42 * E / (1 - mu^2)^0.75] * [(t/D)^2.5 / (L/D - 0.45(t/D)^0.5)]
        # Assuming mu = 0.3
        coeff = 2.42 * self.E / (0.91**0.75) # 2.42 * E / 0.932
        
        t_D = t_mm / D_mm
        L_D = L_mm / D_mm
        
        numerator = t_D ** 2.5
        denominator = L_D - 0.45 * math.sqrt(t_D)
        
        if denominator <= 0: Pe = 9999.0 # Very stiff
        else: Pe = coeff * (numerator / denominator)
        
        # V.8.1.2 Allowable Pa
        # Pa = Pe / 3.0 (If Pe < 0.8 Fy * t/D ?) - Simplified
        # Actually API has regions based on Yield.
        Pa = Pe / 3.0
        
        return Pe, Pa

    def run_design(self):
        """
        Main logic for Annex V check.
        """
        if not self.courses: return {}
        
        # Use top course thickness for unstiffened check (conservative)
        t_top = self.courses[-1].get('t_used', 5.0)
        
        Pe, Pa = self.calculate_pa_unstiffened(t_top, self.H)
        
        # V.8.2.3 Bottom Stiffener Region (N^2 check)
        # N^2 = (445 * D^3) / (t * H^2)
        N_sq = (445.0 * (self.D**3)) / (t_top * (self.H**2))
        
        status = "OK" if Pa >= self.P_ext_kpa else "FAIL"
        
        self.results = {
            'Design External Pressure (kPa)': self.P_ext_kpa,
            'Elastic Buckling Pressure Pe (kPa)': Pe,
            'Allowable External Pressure Pa (kPa)': Pa,
            'Bottom Stiffener Factor N2': N_sq,
            'Status': status,
            'Top Course Thickness (mm)': t_top
        }
        
        # Stiffener Rings Spacing (Simplified V.10)
        if status == "FAIL":
            # Determine Spacing L such that Pa >= P_ext
            # Solving Pe(L) = 3 * P_ext
            # 3 * P_ext = coeff * t_D^2.5 / (L/D - 0.45*sqrt(t_D))
            # L/D - 0.45*sqrt(t_D) = coeff * t_D^2.5 / (3 * P_ext)
            # L = D * [ (coeff * t_D^2.5 / (3 * P_ext)) + 0.45*sqrt(t_D) ]
            
            t_D = t_top / (self.D * 1000.0)
            coeff = 2.42 * self.E / (0.91**0.75)
            
            if self.P_ext_kpa > 0:
                L_max = self.D * ( (coeff * (t_D**2.5) / (3.0 * self.P_ext_kpa)) + 0.45 * math.sqrt(t_D) )
                self.results['Max Stiffener Spacing L (m)'] = L_max
                self.results['Required Number of Rings'] = math.ceil(self.H / L_max) - 1
            else:
                self.results['Max Stiffener Spacing L (m)'] = self.H
                self.results['Required Number of Rings'] = 0

        return self.results
