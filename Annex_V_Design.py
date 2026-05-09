
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
        self.results = {
            'Checks': {}
        }

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
        
        # Governing Case: Unstiffened Shell
        t_min_shell = min([c['t_used'] for c in self.courses])
        Pe, Pa = self.calculate_pa_unstiffened(t_min_shell, self.H)
        
        # V.8.2.3 Bottom Stiffener Region (N^2 check)
        # N^2 = (445 * D^3) / (t * H^2)
        N_sq = (445.0 * (self.D**3)) / (t_min_shell * (self.H**2)) if t_min_shell > 0 and self.H > 0 else 0
        
        status = "OK" if Pa >= self.P_ext_kpa else "FAIL"
        
        self.results = {
            'P_ext_kPa': self.P_ext_kpa,
            'Pe_kPa': Pe,
            'Pa_kPa': Pa,
            'N_sq': N_sq,
            'Status': status,
            't_min_mm': t_min_shell,
            'H_m': self.H,
            'D_m': self.D
        }
        
        if status == "FAIL":
            t_D = t_min_shell / (self.D * 1000.0)
            coeff = 2.42 * self.E / (0.91**0.75)
            if self.P_ext_kpa > 0:
                L_max = self.D * ( (coeff * (t_D**2.5) / (3.0 * self.P_ext_kpa)) + 0.45 * math.sqrt(t_D) )
                num_rings = math.ceil(self.H / L_max) - 1
                self.results['L_max_m'] = L_max
                self.results['Num_Rings'] = max(0, int(num_rings))
            else:
                self.results['L_max_m'] = self.H
                self.results['Num_Rings'] = 0

        return self.results
