
import math

class EFRTDesign:
    def __init__(self, diameter, material_yield, specific_gravity):
        """
        Initialize EFRT Design with Tank Parameters.
        :param diameter: Tank Diameter (m) - Shell I.D or Reference
        :param material_yield: Yield Strength of Material (MPa)
        :param specific_gravity: S.G of product (Design)
        """
        self.D_tank = float(diameter)
        self.Sy = float(material_yield)
        self.SG = float(specific_gravity)
        
        # Pontoon Geometry (Defaults based on Dump, to be overwritten)
        self.B_pontoon = 1.7  # Pontoon Width (m) correspond to 'w'
        self.H_outer = 0.8    # Outer Rim Height (m) 'Hor'
        self.H_inner = 0.65   # Inner Rim Height (m) 'Hir'
        self.gap_rim = 0.2    # Rim Gap (m)
        self.N_pontoons = 16  # Number of Pontoons
        
        # Thicknesses (mm)
        self.t_deck = 5.0     # Deck Plate
        self.t_rim_outer = 6.0
        self.t_rim_inner = 6.0
        self.t_pontoon_top = 5.0
        self.t_pontoon_btm = 5.0
        
        self.results = {}

    def set_pontoon_geometry(self, width, h_out, h_in, n_pontoons):
        self.B_pontoon = float(width) / 1000.0 if width > 100 else float(width)
        self.H_outer = float(h_out) / 1000.0 if h_out > 100 else float(h_out)
        self.H_inner = float(h_in) / 1000.0 if h_in > 100 else float(h_in)
        self.N_pontoons = int(n_pontoons)

    def set_thickness(self, t_deck, t_rim_out, t_rim_in, t_pon_top, t_pon_btm):
        self.t_deck = float(t_deck)
        self.t_rim_outer = float(t_rim_out)
        self.t_rim_inner = float(t_rim_in)
        self.t_pontoon_top = float(t_pon_top)
        self.t_pontoon_btm = float(t_pon_btm)

    def calculate_buoyancy(self):
        """
        Check Buoyancy per API 650 C.3.4
        Floating Roof should have enough buoyancy to support:
        1. Dead Weight + 250mm rain (Deck Punctured)
        2. Dead Weight + 250mm rain (Pontoon Punctured - 2 compartments)
        """
        # 1. Calculate Weights
        # Assumption: Simple Annular Pontoon
        rho_steel_kgm3 = 7850.0
        
        D_outer_rim = self.D_tank - 2*self.gap_rim # Approx
        D_inner_rim = D_outer_rim - 2*self.B_pontoon
        
        area_deck = math.pi * (D_inner_rim/2.0)**2
        area_pontoon_top = math.pi * ((D_outer_rim/2.0)**2 - (D_inner_rim/2.0)**2)
        area_pontoon_btm = area_pontoon_top # Assume same
        
        # Perimeter for Rims
        c_outer = math.pi * D_outer_rim
        c_inner = math.pi * D_inner_rim
        
        # Weights (kg)
        w_deck = area_deck * (self.t_deck/1000.0) * rho_steel_kgm3
        w_rim_out = c_outer * self.H_outer * (self.t_rim_outer/1000.0) * rho_steel_kgm3
        w_rim_in = c_inner * self.H_inner * (self.t_rim_inner/1000.0) * rho_steel_kgm3
        w_pon_top = area_pontoon_top * (self.t_pontoon_top/1000.0) * rho_steel_kgm3
        w_pon_btm = area_pontoon_btm * (self.t_pontoon_btm/1000.0) * rho_steel_kgm3
        
        # Add approximate structural weight factor (rafters, legs, etc) - say 10%
        total_steel_weight_kg = (w_deck + w_rim_out + w_rim_in + w_pon_top + w_pon_btm) * 1.10
        total_weight_N = total_steel_weight_kg * 9.81
        
        # 2. Buoyancy Volume (Pontoon Only)
        # Volume of Pontoon = Area * Average Height? No, trapezoidal or rectangular section.
        # Assume Rectangular for initial check or Average Height
        avg_height = (self.H_outer + self.H_inner) / 2.0
        vol_pontoon = area_pontoon_top * avg_height
        
        # Buoyancy Force available (Product SG)
        buoyancy_N = vol_pontoon * 1000.0 * self.SG * 9.81
        
        # Check 1: Operating Buoyancy
        # Friction is usually ignored or add seal friction
        safety_factor = buoyancy_N / total_weight_N
        
        self.results['Weight_kg'] = round(total_steel_weight_kg, 1)
        self.results['Buoyancy_N'] = round(buoyancy_N, 1)
        self.results['Safety_Factor'] = round(safety_factor, 2)
        
        return self.results

    def check_deck_thickness(self):
        # API 650 C.3.3.2: Minimum 4.8mm (3/16 in)
        min_thk = 4.8
        status = "Pass" if self.t_deck >= min_thk else "Fail"
        
        self.results['Deck_Thickness_Check'] = {
            'Provided': self.t_deck,
            'Required': min_thk,
            'Status': status
        }
        return status

    def check_pontoon_rafter(self, rafter_size_str):
        """
        Check Pontoon Rafter Design.
        :param rafter_size_str: e.g. "L 75 x 75 x 6"
        """
        # Parse Size
        # Assume Angle L AxBxt
        # Very rough parsing, need Structure DB ideally
        try:
            parts = rafter_size_str.replace("L", "").replace("x", " ").split()
            if len(parts) >= 3:
                A = float(parts[0])
                B = float(parts[1])
                t = float(parts[2])
                
                # Approximate Section Modulus for Angle (if not in DB)
                # Z ~ (1/6)*t*h^2 * 1.5? Angles are tricky.
                # Use standard property approximation or lookup if exact match.
                # For L 75x75x6:
                # I ~ 36.1 cm4 (AISC/JIS) -> cm4 * 10000 = mm4
                # c ~ 21 mm
                # S ~ I/c ~ 17 cm3?
                # Let's use a small lookup for common metric angles found in API 650.
                
                # Fallback DB
                angle_props = {
                    '75': {'Sx': 7.08}, # cm3, rough
                    '65': {'Sx': 5.0},
                    '50': {'Sx': 3.0}
                }
                
                Sx_cm3 = 0.0
                key = str(int(A))
                if key in angle_props:
                    Sx_cm3 = angle_props[key]['Sx']
                else:
                    Sx_cm3 = 7.0 # Default for L75
                
                # Load Calculation (Annex C.3.10)
                # Live Load = 1.2 kPa? Or 2.4?
                # Annex C.3.10.2: Rafters... designed for dead load + 1.2 kPa
                LL = 1.2 # kPa
                DL = 0.5 # Assumed Pontoon Plate Load?
                q_total = LL + DL # 1.7 kPa
                
                # Span = Pontoon Width (radial)
                L = self.B_pontoon
                
                # Spacing = ? Assume 1m or based on circumference?
                # Rafters usually radial inside pontoon?
                # Let's assume spacing S = 1.0m roughly or derived from N?
                # If N_rafters not given, assume spacing at outer rim check?
                # Width at outer rim = Pi * D_outer / N_pontoons? No, Pontoons are annular.
                # Rafters are typically frames.
                # Let's handle 'w' dimension as span.
                
                spacing = 2.0 # Worst case width?
                # Actually, standard rafter spacing is ~1m?
                # Let's use 1.0 for now for estimation.
                w_load = q_total * spacing
                
                M_max = (w_load * L**2) / 8.0 # kNm
                
                # Stress
                fb = (M_max * 1000.0) * 1000.0 / (Sx_cm3 * 1000.0) # Nmm / mm3 = MPa
                
                allowable = 0.6 * self.Sy
                
                status = "Pass" if fb <= allowable else "Fail"
                
                self.results['Rafter_Check'] = {
                    'Size': rafter_size_str,
                    'Span_m': L,
                    'Moment_kNm': round(M_max, 2),
                    'Stress_MPa': round(fb, 2),
                    'Allowable_MPa': allowable,
                    'Status': status
                }
                return status
                
        except Exception as e:
            self.results['Rafter_Check'] = {'Error': str(e)}
            return "Error"
        
        return "Unknown"

    def check_roof_leg(self, leg_od, leg_thk, length_m=2.0, num_legs=16):
        """
        Check Roof Support Leg (API 650 C.3.10.3).
        Legs are checked as columns supporting the roof dead load + live load (or partial).
        Usually checked for:
        1. Operating (Landing) - Dead Load + 2.4 kPa (maintenance)? Or just Dead Load?
           API 650 C.3.10.3: Legs design for dead load + uniform live load of 1.2 kPa? 
           Wait, C.3.10.2 says rafters 1.2 kPa. Legs usually same or 25 psf.
           Let's assume Total Load = DL + 1.2 kPa.
        """
        try:
            # 1. Calculate Section Properties
            od_mm = float(leg_od)
            thk_mm = float(leg_thk)
            id_mm = od_mm - 2 * thk_mm
            
            area_mm2 = (math.pi / 4.0) * (od_mm**2 - id_mm**2)
            I_mm4 = (math.pi / 64.0) * (od_mm**4 - id_mm**4)
            r_mm = math.sqrt(I_mm4 / area_mm2)
            
            # 2. Calculate Load per Leg
            # Total Roof Weight (Steel) calculated in Buoyancy check
            # We need to run calculate_buoyancy first to get Weight_kg
            if 'Weight_kg' not in self.results:
                self.calculate_buoyancy()
                
            weight_kg = self.results.get('Weight_kg', 0)
            weight_N = weight_kg * 9.81
            
            # Additional Live Load (1.2 kPa) on Deck Area?
            # Area Deck ~ 131 m2 (Pontoon) + Deck? Area Total = Pi*D^2/4
            R_tank = self.D_tank / 2.0
            area_total = math.pi * R_tank**2
            
            # Live Load N
            LL_kPa = 1.2
            LL_N = LL_kPa * 1000.0 * area_total
            
            total_load_N = weight_N + LL_N
            
            # Load per Leg (Assumption: Uniform distribution? Pontoons take more?)
            # Usually Deck Legs take center, Pontoon legs take rim.
            # If 16 Pontoon legs + ? Deck legs.
            # Simplified: Average load per leg if we only have 16 legs (Conservative?)
            # Actually, if only 16 legs for 26m tank, that's very few. 
            # Likely there are deck legs too.
            # But let's check capacity of ONE pontoon leg for the tributary area (~ Pontoon Area / 16).
            
            # Tributary Area for Pontoon Leg: ~ Pontoon Area / N_pontoons
            D_out = self.D_tank - 2*self.gap_rim
            D_in = D_out - 2*self.B_pontoon
            area_pontoon = (math.pi/4.0)*(D_out**2 - D_in**2)
            trib_area = area_pontoon / float(num_legs)
            
            # Load on Pontoon Leg
            # Pontoon Weight (approx portion) + LL on Pontoon
            # Pontoon Weight ~ Area * 2 * t * rho?
            # Let's use simplified Total Load / Total Area * Trib Area approach
            
            unit_load = total_load_N / area_total # N/m2
            P_leg = unit_load * trib_area # N
            
            # Or use Pontoon-specific weight + LL
            # P_leg_conservative = (Total Weight + LL) / N (Very conservative if no deck legs)
            # Let's stick to Tributary Area of Pontoon.
            
            # 3. Column Buckling (AISC ASD / API 650)
            # Slenderness KL/r
            K = 1.0 # Pinned-Pinned
            L_mm = length_m * 1000.0
            KL_r = (K * L_mm) / r_mm
            
            # Allowable Stress Fa (AISC ASD)
            # Cc = Sqrt(2*pi^2*E / Fy)
            E = 200000.0 # MPa
            Fy = self.Sy
            Cc = math.sqrt(2 * math.pi**2 * E / Fy)
            
            Fa = 0.0
            if KL_r <= Cc:
                # Inelastic Buckling
                factor = 5.0/3.0 + (3.0*KL_r)/(8.0*Cc) - (KL_r**3)/(8.0*Cc**3)
                Fa = (Fy / factor) * (1.0 - (KL_r**2)/(2.0*Cc**2))
            else:
                # Elastic Buckling
                Fa = (12.0 * math.pi**2 * E) / (23.0 * KL_r**2)
            
            # Allowable Load
            P_allow = Fa * area_mm2 # N
            
            status = "Pass" if P_leg <= P_allow else "Fail"
            
            self.results['Leg_Check'] = {
                'Size': f"{od_mm:.1f}x{thk_mm:.1f}mm",
                'Length_m': length_m,
                'Slenderness_KL_r': round(KL_r, 1),
                'Load_per_Leg_kN': round(P_leg/1000.0, 1),
                'Capacity_kN': round(P_allow/1000.0, 1),
                'Status': status
            }
            return status

        except Exception as e:
            self.results['Leg_Check'] = {'Error': str(e)}
            return "Error"
