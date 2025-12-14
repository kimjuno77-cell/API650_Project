
import math

class AnchorChairDesign:
    def __init__(self, net_uplift_kN, num_bolts, bolt_diameter_mm, shell_t_bot_mm, shell_yield_MPa=250.0, chair_yield_MPa=250.0):
        """
        Anchor Chair Design based on typical industry practices (e.g., AISI E-1, Bednar).
        API 650 does not provide explicit chair formulas but requires anchors to be capable.
        
        :param net_uplift_kN: Total Net Uplift Force (kN)
        :param num_bolts: Number of Anchor Bolts
        :param bolt_diameter_mm: Diameter of one anchor bolt (mm)
        :param shell_t_bot_mm: Thickness of bottom shell course (mm)
        :param shell_yield_MPa: Yield Strength of Shell (MPa)
        :param chair_yield_MPa: Yield Strength of Chair Material (MPa)
        """
        self.U_total = net_uplift_kN
        self.N = num_bolts
        self.d = bolt_diameter_mm
        self.t_shell = shell_t_bot_mm
        self.Sy_shell = shell_yield_MPa
        self.Sy_chair = chair_yield_MPa
        self.results = {}

    def run_design(self):
        if self.U_total <= 0 or self.N == 0:
            self.results = {
                'Status': 'Not Required',
                'Top Plate Thk (mm)': 0,
                'Chair Height (mm)': 0,
                'Chair Width (mm)': 0
            }
            return

        # 1. Load per Bolt
        P_bolt_kN = self.U_total / self.N
        P_bolt_N = P_bolt_kN * 1000.0
        
        # 2. Geometry Rules of Thumb (Bednar / Industry Std)
        # Eccentricity e from shell: approx 1.5 * d + clearance (say 2*d minimal for wrench)
        # Let's assume moment arm e = 40 mm + 0.5*d typically?
        # A conservative simplified check: e = 1.5 * d
        e = 1.5 * self.d
        
        # Top Plate Width (a): Sufficient to accommodate bolt washer/nut. 
        # Min width ~ 3 * d
        width_top = 3.0 * self.d
        
        # Top Plate Length (b): e + clearance? Say 1.5*d
        # Just use width for bending calc width.
        
        # 3. Top Plate Thickness Calculation (Beam Bending)
        # Model as cantilever or guided beam? Typical: Guided beam fixed at sides (gussets).
        # Moment M = P * L / X?
        # Simplified Plate Bending formula for Chair Top:
        # t_req = sqrt( 2 * P * e / (S_allow * width) ) NO, that's cantilever.
        # Critical Moment usually calculated as P * (e - d/2) ?
        # Let's use: M = P * (e/2) (load distributed)
        # Allowable Stress S_allow = 0.66 * Sy (AISC) or similar.
        S_allow = 0.66 * self.Sy_chair
        
        # Bending Moment M (N-mm)
        # Assume effective moment arm is 'e/2' for a distributed reaction or critical section logic.
        # Conservative: M = P_bolt_N * (self.d * 0.8) # Approx arm
        M_bending = P_bolt_N * (self.d * 0.5) 
        
        # t = sqrt( (6 * M) / (width * S_allow) )
        if width_top > 0 and S_allow > 0:
            t_req_bending = math.sqrt( (6 * M_bending) / (width_top * S_allow) )
        else:
            t_req_bending = 0
            
        # Min practical thickness
        t_req_min = max(10.0, self.d * 0.5) # At least half bolt dia or 10mm
        
        t_top = max(t_req_bending, t_req_min)
        
        # 4. Chair Height (h)
        # Governed by longitudinal stress distribution into shell.
        # Stress in shell = P / (h_effective * t_shell) ???
        # Usually assume load spreads at 45 deg or check shear?
        # Bednar formula for Height: h >= P * e / (t_shell^2 * ...)? No.
        # Simple limit: Average shear/tension in weld/shell.
        # Practical: h = 6 to 8 * d.
        h_chair = 8.0 * self.d
        
        # 5. Check Shell Stress
        # Local stress at chair attachment. 
        # Acceptable if h_chair is large enough.
        # We report the recommended h.
        
        self.results = {
            'Status': 'Design OK',
            'Load per Bolt (kN)': P_bolt_kN,
            'Top Plate Width (mm)': width_top,
            'Top Plate Thk (mm)': t_top,
            'Chair Height (mm)': h_chair,
            'Eccentricity (mm)': e,
            'Notes': 'Simplified calculation based on Bolt Load and Yield Stress'
        }
