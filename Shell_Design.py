import math
from Materials import get_material_properties, is_stainless_steel

class ShellDesign:
    def __init__(self, diameter, height, design_liquid_level, test_liquid_level, specific_gravity, corrosion_allowance, 
                 p_design, p_test, efficiency=1.0, courses_input=None, design_temp=40.0):
        """
        Initialize Shell Design parameters.
        
        :param diameter: Tank Nominal Diameter (m)
        :param height: Tank Shell Height (m) (Physical)
        :param design_liquid_level: Design Liquid Level (m) (HD)
        :param test_liquid_level: Test Liquid Level (m) (HT)
        :param specific_gravity: Specific Gravity of stored liquid
        :param corrosion_allowance: Corrosion Allowance (mm)
        :param p_design: Internal Design Pressure (mmH2O)
        :param p_test: Internal Test Pressure (mmH2O)
        :param efficiency: Tank Joint Efficiency (0.0 to 1.0, default 1.0)
        :param courses_input: List of dicts defining courses (Width, Material, Thickness_Used)
        :param design_temp: Design Temperature (deg C) for Material Stress Derating
        """
        self.D = diameter
        self.H = height
        self.HD = design_liquid_level
        self.HT = test_liquid_level
        self.G = specific_gravity
        self.CA = corrosion_allowance
        self.P_design = p_design
        self.P_test = p_test
        self.E = efficiency # Joint Efficiency
        self.courses_input = courses_input
        self.design_temp = design_temp
        self.results = []

    def get_material_stress(self, material_name):
        props = get_material_properties(material_name, self.design_temp)
        return props['Sd'], props['St']

    def calculate_vdm_thickness(self, H_eff, G, S, CA, width):
        """
        Calculate thickness using Variable Design Point Method (API 650 5.6.4).
        """
        # Initial guess: Calculate at bottom (x=0)
        # Note: API 650 5.6.4.1 doesn't explicitly show E in the x calc, but it is in t calc.
        # t = (4.9 * D * (H - x) * G) / (Sd * E) + CA
        
        t = (4.9 * self.D * H_eff * G) / (S * self.E) + CA
        
        # Iteration for VDM
        for _ in range(10):
            # x calculation (API 650 5.6.4.1)
            x = 0.61 * math.sqrt(self.D * (t / 1000.0)) # x in meters
            
            # Calculate H at design point
            H_x = H_eff - x
            if H_x < 0: H_x = 0
            
            # Recalculate t
            t_new = (4.9 * self.D * H_x * G) / (S * self.E) + CA
            
            if abs(t_new - t) < 0.01:
                t = t_new
                break
            t = t_new
            
        return t

    def calculate_1ft_thickness(self, H_eff, G, S, CA):
        """
        Calculate thickness using 1-Foot Method (API 650 5.6.3).
        td = (4.9 * D * (H - 0.3) * G) / (Sd * E) + CA
        """
        # H_eff is the liquid height at the bottom of the course.
        # 1-Foot method uses (H - 0.3) where H is the liquid level above the bottom of the course.
        # So effective design height is max(0, H_eff - 0.3).
        
        H_design = H_eff - 0.3
        if H_design < 0: H_design = 0
        
        t = (4.9 * self.D * H_design * G) / (S * self.E) + CA
        return t

    def calculate_shell_weight(self):
        """
        Calculates the total weight of the shell plates in kg and Newtons.
        W_shell = Sum(Pi * D * Width * Thickness * Density)
        """
        total_weight_kg = 0.0
        
        # Density of steel (approx 7850 kg/m3)
        rho_steel = 7850.0
        
        for course in self.results:
            # Use calculated thickness if available, else used thickness
            # Actually, weight should be based on USED thickness (nominal)
            t = course['t_used'] / 1000.0 # m
            w = course['Width'] # m
            
            # Volume = Pi * D * w * t
            # D is centerline diameter? Approx D_inner + t
            # Use D_inner for simplicity or D + t
            D_center = self.D + t
            vol = math.pi * D_center * w * t
            weight = vol * rho_steel
            total_weight_kg += weight
            
        return total_weight_kg, total_weight_kg * 9.81 # kg, N

    def run_design(self, method='auto'):
        """
        Run shell design calculation.
        :param method: 'auto', 'vdm', or '1ft'. 
                       'auto' selects based on API 650 (D <= 61m -> 1ft, else VDM).
        """
        # Determine Method
        use_vdm = True
        is_annex_a = False
        
        if method == '1ft':
            use_vdm = False
        elif method == 'annex_a':
            use_vdm = False
            is_annex_a = True
        elif method == 'auto':
            if self.D <= 61:
                use_vdm = False
            else:
                use_vdm = True
        
        design_method_name = 'Variable Design Point Method (VDM)' if use_vdm else '1-Foot Method'
        if is_annex_a: design_method_name = "Annex A (Small Tanks)"
        
        # Check for Annex S (Stainless) or X (Duplex)
        # Check first course material
        mat_0 = self.courses_input[0]['Material']
        is_stainless = is_stainless_steel(mat_0)
        
        formula_str = ""
        if is_stainless:
            design_method_name += " (Annex S/X Applied)"
            # Annex S/X uses same formulas but different S values (Yield based)
        
        if use_vdm:
             formula_str = "t = VDM Iteration [t_min = (4.9*D*(H-x)*G)/(S*E) + CA]"
        else:
             formula_str = "t_d = (4.9*D*(H-0.3)*G)/(Sd*E) + CA"

        self.design_report_info = {
            "Method": design_method_name,
            "Formula": formula_str,
            "Is_Stainless": is_stainless
        }
        
        print(f"Selected Design Method: {design_method_name}")

        # Effective Heights
        # Use HD for Design, HT for Test
        head_design_m = (self.P_design / 1000.0) / self.G
        H_eff_design_total = self.HD + head_design_m
        
        head_test_m = (self.P_test / 1000.0) / 1.0
        H_eff_test_total = self.HT + head_test_m
        
        current_height_from_bottom = 0.0
        
        # Store thickness of previous course for VDM
        t_prev_d = 0.0
        t_prev_t = 0.0
        
        for i, course in enumerate(self.courses_input):
            # width = course['Width'] - 0.02
            # Removed hardcoded 20mm subtraction per user feedback (Mismatch Bug).
            width = course['Width']
            
            material = course['Material']
            t_used = course['Thickness_Used']
            
            Sd, St = self.get_material_stress(material)
            
            # Height of liquid above bottom of this course
            H_eff_d = H_eff_design_total - current_height_from_bottom
            H_eff_t = H_eff_test_total - current_height_from_bottom
            
            if H_eff_d < 0: H_eff_d = 0
            if H_eff_t < 0: H_eff_t = 0
            
            # Calculate Thickness
            td = 0.0
            tt = 0.0
            
            if use_vdm:
                if i == 0:
                    # Bottom Course Formula (API 650 5.6.4.2)
                    # Design
                    term1 = math.sqrt(H_eff_d / Sd)
                    term2 = (0.0696 * self.D / H_eff_d) * term1
                    factor = 1.06 - term2
                    # Apply E to base_t
                    base_t = (4.9 * H_eff_d * self.D * self.G) / (Sd * self.E) 
                    td = factor * base_t + self.CA
                    
                    # Test (Efficiency usually applies to design, check 5.6.4.2)
                    # For hydrotest, E is typically considered 1.0 or same?
                    # API 650 5.6.2.2: "St = maximum allowable stress for simple hydrostatic test..."
                    # Does NOT mention E for test. Usually E=1.0 for test unless specified.
                    # However, if we follow formula strictly, E should differ?
                    # Standard practice: Use E only for Design condition. Test is E=1.0?
                    # Let's assume E applies to Design (Sd) but for Test (St), checking the code...
                    # 5.6.3.2 (1-Foot) says "E = joint efficiency..."
                    # It's applied to the formula.
                    # For Test case, it usually uses E=1.0 because it's a short term test and St is higher.
                    # Often E is kept 1.0 for test in commercial software unless shell has radiography issues.
                    # I'll use self.E for Design and 1.0 for Test or self.E? 
                    # Let's keep self.E for both or 1.0 for test. 
                    # Most examples show E applied to Design only. 
                    # Let's apply self.E to Design, and assume 1.0 for Test (fully inspected/new tank).
                    # Actually if joint is not radiographed, it's weak always.
                    # So self.E should apply to both?
                    # 3.4 of API 650: E depends on radiography.
                    # Let's apply self.E to both for safety, or 1.0 for test?
                    # I will apply self.E to Design and keep Test as is (usually full stress allowed).
                    # Wait, 5.6.3.2 does not distinguish.
                    # I will apply E to both.
                    
                    term1_t = math.sqrt(H_eff_t / St)
                    term2_t = (0.0696 * self.D / H_eff_t) * term1_t
                    factor_t = 1.06 - term2_t
                    base_t_t = (4.9 * H_eff_t * self.D * 1.0) / (St * self.E)
                    tt = factor_t * base_t_t
                else:
                    # Upper Courses (API 650 5.6.4.3)
                    # Design
                    x_d = 0.61 * math.sqrt(self.D * (t_prev_d / 1000.0))
                    H_x_d = H_eff_d - x_d
                    if H_x_d < 0: H_x_d = 0
                    td = (4.9 * self.D * H_x_d * self.G) / (Sd * self.E) + self.CA
                    
                    # Test
                    x_t = 0.61 * math.sqrt(self.D * (t_prev_t / 1000.0))
                    H_x_t = H_eff_t - x_t
                    if H_x_t < 0: H_x_t = 0
                    tt = (4.9 * self.D * H_x_t * 1.0) / (St * self.E)
            else:
                # 1-Foot Method (API 650 5.6.3)
                td = self.calculate_1ft_thickness(H_eff_d, self.G, Sd, self.CA)
                tt = self.calculate_1ft_thickness(H_eff_t, 1.0, St, 0.0)
            
            # Update prev for next iteration (VDM needs it, 1-Foot doesn't but harmless)
            t_prev_d = td
            t_prev_t = tt
            
            # Min Thickness (API 650 5.6.1.1)
            t_min_code = 5.0
            if self.D >= 60: t_min_code = 10.0
            elif self.D >= 36: t_min_code = 8.0
            elif self.D >= 15: t_min_code = 6.0
            
            t_req = max(td, tt, t_min_code)
            
            # Recommended Thickness Calculation
            # Standard Commercial Plates (Common metric sizes in mm)
            # 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20...
            # For simplicity, let's use 1mm increments, but ensure strict >= coverage
            # Using math.ceil catches 10.1 -> 11.
            
            t_rec = math.ceil(t_req)
            
            # Optional: Enforce Even numbers for larger thicknesses if preferred?
            # Many standards use 6, 8, 10, 12 (even) or 5, 6, 8, 9...
            # Let's keep 1mm increments (math.ceil) as it's safe.
            # However, ensure it's never less than t_req. (Ceil is safe).
            
            # Double check against Rec logic:
            if t_rec < t_req: t_rec += 1 # Should not happen with ceil
            
            # Auto-assign Recommended if Used is 0
            if t_used <= 0.0:
                t_used = t_rec
            
            self.results.append({
                'Course': course['Course'],
                'Material': material,
                'Sd': Sd, 'St': St,
                'Width': width,
                'H_eff_d': H_eff_d,
                'H_eff_t': H_eff_t,
                'td': td,
                'tt': tt,
                't_req': t_req,
                't_rec': t_rec,
                't_used': t_used,
                'Status': 'OK' if t_used >= t_req - 0.01 else 'FAIL'
            })
            
            current_height_from_bottom += width
            
        # Calculate Weight
        W_kg, W_N = self.calculate_shell_weight()
        print(f"Total Shell Weight: {W_kg:.2f} kg ({W_N/1000:.2f} kN)")
        
        return self.shell_courses, W_kg

    @property
    def shell_courses(self):
        return self.results

    def print_report(self):
        print(f"{'Course':<10} | {'Mat':<10} | {'W(m)':<6} | {'Hd(m)':<8} | {'td(mm)':<8} | {'tt(mm)':<8} | {'Req(mm)':<8} | {'Rec(mm)':<8} | {'Used':<8} | {'Status'}")
        print("-" * 115)
        for r in self.results:
            print(f"{r['Course']:<10} | {r['Material']:<10} | {r['Width']:<6.2f} | {r['H_eff_d']:<8.3f} | {r['td']:<8.3f} | {r['tt']:<8.3f} | {r['t_req']:<8.3f} | {r['t_rec']:<8.0f} | {r['t_used']:<8.3f} | {r['Status']}")

if __name__ == "__main__":
    from InputReader import InputReader
    import os
    
    input_file = "Excel_Logic_input_03-1 i-070936-67-T-0319-0327-Type4-78x18-(For_Education)-Ver. 1.05.xls"
    
    if os.path.exists(input_file):
        try:
            reader = InputReader(input_file)
            params = reader.get_design_parameters()
            courses = reader.get_shell_courses()
            
            tank = ShellDesign(
                diameter=params['D'],
                height=params['H'],
                design_liquid_level=params.get('HD', params['H']), # Fallback to H if HD missing
                test_liquid_level=params.get('HT', params['H']),
                specific_gravity=params['G'],
                corrosion_allowance=params['CA'],
                p_design=params['P_design'],
                p_test=params['P_test'],
                courses_input=courses
            )
            
            print("\nAPI 650 Shell Design Calculation (Variable Design Point Method)")
            print(f"Diameter: {tank.D} m, Height: {tank.H} m")
            print(f"Design Liquid Level (HD): {tank.HD} m, Test Liquid Level (HT): {tank.HT} m")
            print(f"SG: {tank.G}, CA: {tank.CA} mm")
            print(f"P_design: {tank.P_design} mmH2O, P_test: {tank.P_test} mmH2O")
            
            tank.run_design()
            tank.print_report()
            
        except Exception as e:
            print(f"Error: {e}")
