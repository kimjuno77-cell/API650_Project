import math

class VentingDesign:
    """
    Implements API 2000 (7th Edition) Venting Calculations.
    Units: Metric (m3/h, m2, m, etc.)
    """
    def __init__(self, volume_m3, surface_area_m2, wetted_area_m2, 
                 pump_in_rate, pump_out_rate, flash_point_category, insulation_factor=1.0):
        """
        :param volume_m3: Tank Net Capacity (m3)
        :param surface_area_m2: Tank Surface Area (Not strictly used for Table 2 lookup but good for reference)
        :param wetted_area_m2: Wetted surface area for Fire Case (usually bottom 9.14m shell)
        :param pump_in_rate: Filling rate (m3/h)
        :param pump_out_rate: Emptying rate (m3/h)
        :param flash_point_category: 'High' (>= 40C) or 'Low' (< 40C)
        :param insulation_factor: F (1.0 for bare tank, lower for insulated)
        """
        self.V = volume_m3
        self.A_wetted = wetted_area_m2
        self.pump_in = pump_in_rate
        self.pump_out = pump_out_rate
        self.flash_point_cat = flash_point_category # 'High' or 'Low'
        self.F = insulation_factor
        self.results = {}

    def calculate_normal_venting(self):
        """
        Calculate Inbreathing and Outbreathing Requirements (Nm3/h of Air).
        Refs: API 2000 7th Ed, Annex A (Metric).
        """
        # --- 1. Liquid Movement ---
        # Outbreathing (Filling) - Table A.3 Metric
        # Low Flash Point (< 40C) or Boiling: 2.02 Nm3/h per m3/h filling
        # High Flash Point (>= 40C): 1.01 Nm3/h per m3/h filling
        rate_out_factor = 2.02 if self.flash_point_cat == 'Low' else 1.01
        req_out_liquid = self.pump_in * rate_out_factor
        
        # Inbreathing (Emptying) - Table A.3 Metric
        # Standard: 0.94 Nm3/h per m3/h emptying
        req_in_liquid = self.pump_out * 0.94
        
        # --- 2. Thermal Effects ---
        # Refs: API 2000 Table 2 (Metric Units)
        # Based on Tank Capacity V (m3).
        # Data format: (Volume, Inbreathing, Outbreathing_HighFP)
        # Note: If Low FP, Outbreathing typically equals Inbreathing (See API 2000 3.3.2.3.2)
        
        thermal_table = [
             (2, 0.17, 0.11), (4, 0.34, 0.22), (20, 1.7, 1.1), (40, 3.4, 2.2),
             (100, 8.5, 5.5), (200, 17, 11), (400, 34, 22), (1000, 85, 55),
             (2000, 170, 110), (3000, 255, 165), (4000, 340, 220), 
             (5000, 425, 275), (6000, 510, 330), (8000, 680, 440), 
             (10000, 850, 550), (15000, 1270, 825), (20000, 1700, 1100),
             (25000, 2120, 1375), (30000, 2550, 1650)
        ]
        
        req_in_thermal = 0.0
        req_out_thermal = 0.0
        
        v_calc = self.V
        
        # Extrapolation logic for V > 30000 (Linear scaling approximation)
        if v_calc > 30000:
             ratio = v_calc / 30000.0
             req_in_thermal = 2550 * ratio
             req_out_thermal = 1650 * ratio
        else:
            # Interpolation
            lower = thermal_table[0]
            for row in thermal_table:
                if v_calc <= row[0]:
                    upper = row
                    # Linear Interpolation
                    rng = upper[0] - lower[0]
                    if rng < 1e-9: rng = 1.0
                    frac = (v_calc - lower[0]) / rng
                    
                    req_in_thermal = lower[1] + frac * (upper[1] - lower[1])
                    req_out_thermal = lower[2] + frac * (upper[2] - lower[2])
                    break
                lower = row
        
        # Adjustment for Low Flash Point (API 2000 3.3.2.3.2)
        if self.flash_point_cat == 'Low':
            req_out_thermal = req_in_thermal

        # --- Totals ---
        self.results['Inbreathing_Liquid_Nm3h'] = req_in_liquid
        self.results['Inbreathing_Thermal_Nm3h'] = req_in_thermal
        self.results['Total_Inbreathing_Nm3h'] = req_in_liquid + req_in_thermal
        
        self.results['Outbreathing_Liquid_Nm3h'] = req_out_liquid
        self.results['Outbreathing_Thermal_Nm3h'] = req_out_thermal
        self.results['Total_Outbreathing_Nm3h'] = req_out_liquid + req_out_thermal
        
        return self.results

    def calculate_emergency_venting(self):
        """
        Calculate Emergency Venting for Fire Case (API 2000 4.3.3).
        Metric Units (Nm3/h Air).
        Formula approx based on Table 5.
        q = 208.2 * F * A (for A <= 260 approx?) - Actually Curve depends.
        Standard fit: q = 221.7 * F * A^0.82
        """
        A = self.A_wetted
        F = self.F
        q_air = 0.0
        
        # API 2000 Formulae logic usually split around A=200-260m2.
        # Below 260m2, Heat Input Q follows curve. 
        # Above 260m2, Q often capped or follows slower growth.
        # Using the standard power law fit which is conservative and smooth:
        # q = 221.7 * F * A^0.82
        
        q_air = 221.7 * F * (A ** 0.82)
        
        self.results['Wetted_Area_m2'] = A
        self.results['Emergency_Venting_Nm3h'] = q_air
        self.results['Insulation_Factor_F'] = F
        
        # Estimate Sizes
        self.estimate_vent_sizes()
        
        return self.results

    def estimate_vent_sizes(self):
        """
        Estimates minimum required size for Normal Breather and Emergency Hatch
        based on typical flow capacities (Reference only, not vendor specific).
        """
        # Normal Venting (Breather Valve)
        # Max of Inbreathing or Outbreathing Total
        max_normal = max(self.results.get('Total_Inbreathing_Nm3h', 0), 
                         self.results.get('Total_Outbreathing_Nm3h', 0))
        
        # Approximate Breather Valve Capacities (Nm3/h)
        # 2": 60, 3": 150, 4": 350, 6": 900, 8": 1600, 10": 2500, 12": 4500
        caps = [(2, 60), (3, 150), (4, 350), (6, 900), (8, 1600), (10, 2500), (12, 4500)]
        
        size_str = "> 12\""
        for sz, cap in caps:
            if max_normal <= cap:
                size_str = f"{sz}\" (min)"
                break
        
        self.results['Min_Normal_Vent_Size'] = size_str
        
        # Emergency Venting (Hatch)
        q_emerg = self.results.get('Emergency_Venting_Nm3h', 0)
        
        # Approximate Hatch Capacities (Nm3/h)
        # 16": 12000, 18": 16000, 20": 22000, 24": 32000
        hatch_caps = [(16, 12000), (18, 16000), (20, 22000), (24, 32000)]
        
        hatch_str = "> 24\" (Multiple Req)"
        for sz, cap in hatch_caps:
            if q_emerg <= cap:
                hatch_str = f"{sz}\" (min)"
                break
                
        if q_emerg > 32000:
            count = math.ceil(q_emerg / 32000)
            hatch_str = f"{count} x 24\""
            
        self.results['Min_Emergency_Vent_Size'] = hatch_str

    def calculate_all(self):
        self.calculate_normal_venting()
        self.calculate_emergency_venting()
        return self.results
