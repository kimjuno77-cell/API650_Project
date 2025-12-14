import math

# Standard I-Beam Sections (Simplified Database)
# Name: [Weight(kg/m), Sx(cm3), Ix(cm4), Area(cm2), Depth(mm)]
RAFTER_SECTIONS = {
    "IPE 100": {'w': 8.1, 'Sx': 34.2, 'Ix': 171, 'A': 10.3, 'd': 100},
    "IPE 120": {'w': 10.4, 'Sx': 53.0, 'Ix': 318, 'A': 13.2, 'd': 120},
    "IPE 140": {'w': 12.9, 'Sx': 77.3, 'Ix': 541, 'A': 16.4, 'd': 140},
    "IPE 160": {'w': 15.8, 'Sx': 109.0, 'Ix': 869, 'A': 20.1, 'd': 160},
    "IPE 180": {'w': 18.8, 'Sx': 146.0, 'Ix': 1317, 'A': 23.9, 'd': 180},
    "IPE 200": {'w': 22.4, 'Sx': 194.0, 'Ix': 1943, 'A': 28.5, 'd': 200},
    "IPE 220": {'w': 26.2, 'Sx': 252.0, 'Ix': 2772, 'A': 33.4, 'd': 220},
    "IPE 240": {'w': 30.7, 'Sx': 324.0, 'Ix': 3892, 'A': 39.1, 'd': 240},
    "IPE 270": {'w': 36.1, 'Sx': 429.0, 'Ix': 5790, 'A': 45.9, 'd': 270},
    "IPE 300": {'w': 42.2, 'Sx': 557.0, 'Ix': 8356, 'A': 53.8, 'd': 300},
    "IPE 330": {'w': 49.1, 'Sx': 713.0, 'Ix': 11770, 'A': 62.6, 'd': 330},
    "IPE 360": {'w': 57.1, 'Sx': 904.0, 'Ix': 16270, 'A': 72.7, 'd': 360},
    "IPE 400": {'w': 66.3, 'Sx': 1160.0, 'Ix': 23130, 'A': 84.5, 'd': 400},
    "IPE 450": {'w': 77.6, 'Sx': 1500.0, 'Ix': 33740, 'A': 98.8, 'd': 450},
    "IPE 500": {'w': 90.7, 'Sx': 1930.0, 'Ix': 48200, 'A': 116.0, 'd': 500},
    "IPE 550": {'w': 106.0, 'Sx': 2440.0, 'Ix': 67120, 'A': 134.0, 'd': 550},
    "IPE 600": {'w': 122.0, 'Sx': 3070.0, 'Ix': 92080, 'A': 156.0, 'd': 600}
}
# Sort by weight (cost efficiency)
SORTED_RAFTERS = sorted(RAFTER_SECTIONS.items(), key=lambda x: x[1]['w'])

# Pipe Columns (Schedule 40 approx)
COLUMN_SECTIONS = {
    "Pipe 4in Sch40": {'w': 16.07, 'A': 20.0, 'r': 39.0}, # r approx 1.51" = 38.4mm
    "Pipe 6in Sch40": {'w': 28.26, 'A': 36.0, 'r': 57.0}, # r approx 2.25" = 57.2mm
    "Pipe 8in Sch40": {'w': 42.55, 'A': 54.0, 'r': 75.0}, # r approx 2.95" = 75mm
    "Pipe 10in Sch40": {'w': 60.30, 'A': 77.0, 'r': 95.0}, # r approx 3.67" = 93mm
    "Pipe 12in Sch40": {'w': 73.8, 'A': 94.0, 'r': 112.0} # r approx 4.38" = 111mm
}

# Standard Metric Angles (Equal Leg)
# Approx Properties for Verification
# Name: [Weight(kg/m), Sx(cm3), Ix(cm4), Area(cm2), d(mm), t(mm)]
# Source: Standard Tables (Approx)
ANGLE_SECTIONS = {
    "L 25x25x3": {'w': 1.12, 'Sx': 0.39, 'Ix': 0.68, 'A': 1.42, 'd': 25, 't': 3},
    "L 30x30x3": {'w': 1.36, 'Sx': 0.53, 'Ix': 1.05, 'A': 1.74, 'd': 30, 't': 3},
    "L 40x40x3": {'w': 1.83, 'Sx': 0.90, 'Ix': 2.45, 'A': 2.35, 'd': 40, 't': 3},
    "L 40x40x5": {'w': 2.97, 'Sx': 1.43, 'Ix': 3.79, 'A': 3.79, 'd': 40, 't': 5},
    "L 45x45x4": {'w': 2.74, 'Sx': 1.62, 'Ix': 4.84, 'A': 3.49, 'd': 45, 't': 4},
    "L 50x50x4": {'w': 3.06, 'Sx': 2.05, 'Ix': 7.62, 'A': 3.89, 'd': 50, 't': 4},
    "L 50x50x6": {'w': 4.47, 'Sx': 2.91, 'Ix': 10.95, 'A': 5.69, 'd': 50, 't': 6},
    "L 65x65x6": {'w': 5.91, 'Sx': 5.25, 'Ix': 23.50, 'A': 7.53, 'd': 65, 't': 6},
    "L 65x65x8": {'w': 7.73, 'Sx': 6.85, 'Ix': 30.20, 'A': 9.85, 'd': 65, 't': 8},
    "L 75x75x6": {'w': 6.85, 'Sx': 7.08, 'Ix': 36.60, 'A': 8.73, 'd': 75, 't': 6},
    "L 75x75x9": {'w': 9.96, 'Sx': 10.20, 'Ix': 52.40, 'A': 12.69, 'd': 75, 't': 9},
    "L 75x75x12": {'w': 13.10, 'Sx': 13.10, 'Ix': 62.40, 'A': 16.20, 'd': 75, 't': 12}, 
    "L 90x90x7": {'w': 9.61, 'Sx': 11.9, 'Ix': 72.9, 'A': 12.2, 'd': 90, 't': 7},
    "L 90x90x10": {'w': 13.4, 'Sx': 16.5, 'Ix': 100.0, 'A': 17.1, 'd': 90, 't': 10},
    "L 90x90x13": {'w': 17.0, 'Sx': 20.8, 'Ix': 124.0, 'A': 21.7, 'd': 90, 't': 13},
    "L 100x100x7": {'w': 10.7, 'Sx': 15.0, 'Ix': 103.0, 'A': 13.6, 'd': 100, 't': 7},
    "L 100x100x10": {'w': 15.0, 'Sx': 20.9, 'Ix': 142.0, 'A': 19.2, 'd': 100, 't': 10},
    "L 100x100x13": {'w': 19.2, 'Sx': 26.5, 'Ix': 177.0, 'A': 24.4, 'd': 100, 't': 13},
    "L 120x120x8": {'w': 14.7, 'Sx': 24.5, 'Ix': 202.0, 'A': 18.7, 'd': 120, 't': 8},
    "L 130x130x9": {'w': 17.9, 'Sx': 32.7, 'Ix': 310.0, 'A': 22.8, 'd': 130, 't': 9},
    "L 130x130x12": {'w': 23.6, 'Sx': 42.5, 'Ix': 400.0, 'A': 30.0, 'd': 130, 't': 12},
    "L 130x130x15": {'w': 29.1, 'Sx': 51.8, 'Ix': 483.0, 'A': 37.0, 'd': 130, 't': 15},
    "L 150x150x12": {'w': 27.3, 'Sx': 57.0, 'Ix': 600.0, 'A': 34.8, 'd': 150, 't': 12},
    "L 150x150x15": {'w': 33.8, 'Sx': 69.8, 'Ix': 731.0, 'A': 43.0, 'd': 150, 't': 15},
    "L 150x150x19": {'w': 42.1, 'Sx': 85.0, 'Ix': 888.0, 'A': 53.6, 'd': 150, 't': 19}
}

class StructureDesign:
    def __init__(self, diameter, loads, material_yield=235.0):
        self.D = diameter
        self.loads = loads
        self.Fy = material_yield
        self.Fb = 0.6 * self.Fy # Allowable Bending Stress (API/AISC ASD)
        self.E = 200000.0 # MPa (Steel)
        self.H = 10.0 # Default H
        
        self.results = {}
        self.layout_data = {}

    def set_height(self, H):
        self.H = H

    def check_buckling(self, Load_kN, L_m, A_cm2, r_mm):
        """
        AISC ASD Column Buckling Check
        """
        P_N = Load_kN * 1000.0
        r_mm = float(r_mm)
        
        K = 1.0 # Pinned-Pinned
        KL = K * (L_m * 1000.0) # mm
        
        if r_mm <= 0: return False, 999.0, 0.0
        
        slenderness = KL / r_mm
        if slenderness > 200: return False, 999.0, 0.0 # Fail recommended max
        
        # AISC ASD
        Cc = math.sqrt(2.0 * math.pi**2 * self.E / self.Fy)
        
        if slenderness <= Cc:
            # Inelastic
            FS = 5.0/3.0 + (3.0*slenderness)/(8.0*Cc) - (slenderness**3)/(8.0*Cc**3)
            Fa = (1.0 - (slenderness**2)/(2.0*Cc**2)) * self.Fy / FS
        else:
            # Elastic
            FS = 23.0/12.0 # 1.92
            Fa = (12.0 * math.pi**2 * self.E) / (23.0 * slenderness**2)
            
        # Allowable Load
        # Area convert to mm2
        A_mm2 = A_cm2 * 100.0
        Pa_N = Fa * A_mm2
        Pa_kN = Pa_N / 1000.0
        
        ratio = Load_kN / Pa_kN if Pa_kN > 0 else 999.0
        status = True if ratio <= 1.0 else False
        return status, ratio, Pa_kN

    def check_rafter_bending(self, M_kN_m, Sx_cm3):
        """
        Check Bending Stress: fb = M / Sx <= Fb (Allowable)
        M in kN-m
        Sx in cm3
        """
        # Convert M to N-mm: kN-m * 10^6
        M_Nmm = M_kN_m * 1000.0 * 1000.0
        
        # Convert Sx to mm3: cm3 * 1000
        Sx_mm3 = Sx_cm3 * 1000.0
        
        if Sx_mm3 <= 0: return False, 999.0
        
        fb = M_Nmm / Sx_mm3 # MPa
        
        ratio = fb / self.Fb
        status = True if ratio <= 1.0 else False
        
        return status, ratio, fb

    def select_col_pipe(self, Load_kN):
        # Iterate Sorted Sections
        for name, props in COLUMN_SECTIONS.items():
            # Check Capacity (Buckling)
            status, ratio, Pa = self.check_buckling(Load_kN, self.H, props['A'], props['r'])
            
            if status:
                 props_out = props.copy()
                 props_out['Ratio'] = ratio
                 props_out['Allowable_kN'] = Pa
                 return name, props_out
                 
        # Fallback
        return "Custom Heavy Pipe", {'w': 100.0, 'A': 999.0, 'r': 100.0, 'Ratio': 1.0, 'Allowable_kN': Load_kN}

    def select_section(self, Sx, db):
        # Sort db
        sorted_items = sorted(db.items(), key=lambda x: x[1]['w'])
        for name, props in sorted_items:
            if props['Sx'] >= Sx:
                return name, props
        # Fallback
        return "Custom Heavy", {'w': 200.0, 'Sx': Sx, 'd': 800.0, 'A': 200.0, 'Ix': 9999}

    def run_design(self):
        # 0. Setup
        R = self.D / 2.0
        
        # Loads
        q_live = self.loads.get('Live', 0.0)
        q_snow = self.loads.get('Snow', 0.0)
        q_dead_p = self.loads.get('Dead_Plate', 0.0)
        q_dead_add = self.loads.get('Dead_Add', 0.0)
        q_design = q_dead_p + q_dead_add + max(q_live, q_snow) # kPa
        
        # 1. Trial 1: Single Span (Center Column Only)
        max_spacing = 2.0 # m
        circ = math.pi * self.D
        num_rafters = math.ceil(circ / max_spacing)
        if num_rafters % 2 != 0: num_rafters += 1
        if num_rafters < 4: num_rafters = 4
        
        spacing_outer = circ / num_rafters
        Area_Sector = (math.pi * R**2) / num_rafters
        P_total_rafter = q_design * Area_Sector # kN
        
        # Single Span L = R.
        # M = 0.128 * P * R (approx for triangular, or uniform sector)
        L = R
        M_max_kN_m = 0.1283 * P_total_rafter * L
        
        Sx_req_cm3 = (M_max_kN_m * 1e6) / self.Fb / 1000.0
        
        # Check Section
        rafter, r_props = self.select_section(Sx_req_cm3, RAFTER_SECTIONS)
        
        # User Constraint: If Depth > 200mm, use Intermediate Support
        use_girders = False
        if r_props['d'] > 200.0:
            use_girders = True
            
        # 2. Design Logic Switch
        if not use_girders:
            # --- Single Span Design ---
            self.finalize_single_span(num_rafters, spacing_outer, rafter, r_props, M_max_kN_m, P_total_rafter, q_design, L)
        else:
            # --- Intermediate Girder System ---
            # Place Ring at R/2 approx
            R_ring = R / 2.0
            
            # Simplified: Design for max span L = R/2.
            Lx_raf = R / 2.0
            spacing_avg_outer = spacing_outer # Conservative logic
            
            w_lin = q_design * spacing_avg_outer # kN/m
            M_raf = w_lin * Lx_raf**2 / 8.0 # kNm
            
            Sx_raf = (M_raf * 1e6) / self.Fb / 1000.0
            rafter_name, rafter_props = self.select_section(Sx_raf, RAFTER_SECTIONS)
            
            # Girder Design
            circ_ring = math.pi * (2 * R_ring)
            num_cols = (math.ceil(circ_ring / 6.0))
            if num_cols < 4: num_cols = 4
            if num_cols % 2 != 0: num_cols += 1
            
            girder_len = circ_ring / num_cols
            
            w_girder = q_design * (R / 2.0) # kN/m
            M_girder = w_girder * girder_len**2 / 8.0
            
            Sx_girder = (M_girder * 1e6) / self.Fb / 1000.0
            girder_name, girder_props = self.select_section(Sx_girder, RAFTER_SECTIONS)
            
            # Column Design
            Area_Inner = math.pi * R_ring**2
            P_center = q_design * 0.25 * Area_Inner
            
            Total_Ring_Load = q_design * math.pi * (R**2) * 0.5
            P_col_ring = Total_Ring_Load / num_cols
            
            # Select Cols
            center_col, c_props = self.select_col_pipe(P_center)
            ring_col, rc_props = self.select_col_pipe(P_col_ring)
            
            # Calc Weights
            rafter_wt = num_rafters * R * rafter_props['w']
            girder_wt = num_cols * girder_len * girder_props['w']
            center_col_wt = 1 * self.H * c_props['w']
            ring_col_wt = num_cols * self.H * rc_props['w']
            col_wt = center_col_wt + ring_col_wt
            
            total_wt = (rafter_wt + girder_wt + col_wt) * 1.1
            
            self.results = {
                'Type': 'Girder System (1-Ring)',
                'Num Rafters': num_rafters,
                'Rafter Section': rafter_name,
                'Rafter_Wt': rafter_props['w'],
                'Rafter_Length': R, 
                'Rafter_Total_Wt': rafter_wt,
                'Girder Section': girder_name,
                'Num Girders': num_cols,
                'Girder_Length': girder_len,
                'Girder_Wt': girder_props['w'],
                'Girder_Total_Wt': girder_wt,
                'Center Col Section': center_col,
                'Center Col Load (kN)': P_center,
                'Center_Col_Wt': c_props['w'],
                'Center_Col_Total_Wt': center_col_wt,
                'Ring Col Section': ring_col,
                'Num Ring Cols': num_cols,
                'Ring Col Load (kN)': P_col_ring,
                'Ring_Col_Wt': rc_props['w'],
                'Ring_Col_Total_Wt': ring_col_wt,
                'Total_Struct_Weight': total_wt,
                'Rafter Spacing (m)': spacing_outer,
                'Max Moment (kNm)': max(M_raf, M_girder)
            }
            self.layout_data = {
                'R': R, 'D': self.D, 'N_raf': num_rafters, 'N_col': num_cols, 'R_ring': R_ring, 'Type': 'Ring'
            }

    def finalize_single_span(self, num_rafter, spacing, rafter_name, r_props, M_max, P_load, q, L):
         # Column Check
        total_load = q * math.pi * (self.D/2)**2
        col_load = total_load / 3.0 # Approx
        col_name, c_props = self.select_col_pipe(col_load)
        
        rafter_wt = num_rafter * L * r_props['w']
        center_col_wt = 1.0 * self.H * c_props['w']
        wt = (rafter_wt + center_col_wt) * 1.1
        
        self.results = {
            'Type': 'Center Column Only',
            'Num Rafters': num_rafter,
            'Rafter Section': rafter_name,
            'Rafter_Wt': r_props['w'],
            'Rafter_Length': L,
            'Rafter_Total_Wt': rafter_wt,
            'Center Col Section': col_name,
            'Center Col Load (kN)': col_load,
            'Center_Col_Wt': c_props['w'],
            'Center_Col_Total_Wt': center_col_wt,
            'Total_Struct_Weight': wt,
            'Rafter Spacing (m)': spacing,
            'Max Moment (kNm)': M_max,
            'Num Girders': 0,
            'Girder Section': '-',
            'Girder_Length': 0,
            'Girder_Wt': 0,
            'Girder_Total_Wt': 0,
            'Ring_Col_Wt': 0,
            'Ring_Col_Total_Wt': 0
        }
        self.layout_data = {
                'R': L, 'D': self.D, 'N_raf': num_rafter, 'N_col': 0, 'R_ring': 0, 'Type': 'Single'
        }

    def generate_structure_plot(self):
        # Create SVG
        R = self.layout_data.get('R', 10)
        cx, cy = 300, 300
        scale = 250 / R if R > 0 else 10
        
        svg = []
        svg.append(f'<svg width="600" height="600" xmlns="http://www.w3.org/2000/svg">')
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{R*scale}" stroke="black" stroke-width="2" fill="none"/>')
        
        # Rafters
        N_raf = self.layout_data.get('N_raf', 8)
        for i in range(N_raf):
            ang = 2 * math.pi * i / N_raf
            x2 = cx + R * scale * math.cos(ang)
            y2 = cy + R * scale * math.sin(ang)
            svg.append(f'<line x1="{cx}" y1="{cy}" x2="{x2}" y2="{y2}" stroke="#666" stroke-width="1"/>')
            
        # Ring Girders & Cols
        if self.layout_data.get('Type') == 'Ring':
            R_ring = self.layout_data.get('R_ring', R/2)
            r_ring_px = R_ring * scale
            N_col = self.layout_data.get('N_col', 4)
            
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_ring_px}" stroke="#d9534f" stroke-width="2" fill="none" stroke-dasharray="5,5"/>')
            
            # Draw Girders (Lines between points)
            pts = []
            for i in range(N_col):
                ang = 2 * math.pi * i / N_col
                px = cx + r_ring_px * math.cos(ang)
                py = cy + r_ring_px * math.sin(ang)
                pts.append((px, py))
                
                # Column Rect
                sz = 8
                svg.append(f'<rect x="{px-sz/2}" y="{py-sz/2}" width="{sz}" height="{sz}" fill="#d9534f"/>')
            
            for i in range(N_col):
                p1 = pts[i]
                p2 = pts[(i+1)%N_col]
                svg.append(f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="#d9534f" stroke-width="2"/>')

        # Center Col
        sz_c = 12
        svg.append(f'<rect x="{cx-sz_c/2}" y="{cy-sz_c/2}" width="{sz_c}" height="{sz_c}" fill="black"/>')
        svg.append('</svg>')
        
        return "\n".join(svg)
