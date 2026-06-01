import math

class AnnexFDesign:
    def __init__(self, D, W_roof_total_kN, W_shell_kN, P_design_kPa, roof_slope, top_angle_size, detail_type, t_shell_top_mm=0.0, W_roof_plates_kN=None):
        """
        API 650 Annex F - Design of Tanks for Small Internal Pressure
        
        :param D: Tank Diameter (m)
        :param W_roof_total_kN: Total Roof Weight (Plates + Structure) (kN)
        :param W_shell_kN: Total Shell Weight (kN)
        :param P_design_kPa: Design Internal Pressure (kPa)
        :param roof_slope: Roof Slope (rise/run)
        :param top_angle_size: String key (e.g. 'L75x75x6')
        :param detail_type: Figure F.2 Detail key ('a', 'c', 'd', 'e')
        :param t_shell_top_mm: Thickness of top shell course (mm)
        :param W_roof_plates_kN: Nominal weight of roof plates only (kN)
        """
        self.D = D
        self.W_roof = W_roof_total_kN # DLr
        self.W_shell = W_shell_kN # DLs
        self.P = P_design_kPa
        self.slope = roof_slope
        self.theta = math.atan(roof_slope)
        self.angle_size = top_angle_size
        self.detail = detail_type
        self.t_shell = t_shell_top_mm
        
        # If plates weight not provided, estimate standard 5mm plate weight + roof slope factor
        if W_roof_plates_kN is None:
            # 5mm steel plates: 5/1000 * 7850 * 9.81 = 0.385 kPa = 0.385 kN/m2
            area = math.pi * (D / 2.0) ** 2
            slope_fac = 1.0 / math.cos(self.theta) if math.cos(self.theta) > 0 else 1.0
            self.W_roof_plates = 0.385 * area * slope_fac
        else:
            self.W_roof_plates = W_roof_plates_kN
        
        # Angle Properties (Area in mm2, Weight in kg/m - approx)
        self.angle_props = {
            'L50x50x4': {'A': 3.89, 'w': 3.06, 'Leg': 50, 't': 4}, # cm2 -> 389 mm2
            'L50x50x5': {'A': 4.80, 'w': 3.77, 'Leg': 50, 't': 5},
            'L50x50x6': {'A': 5.69, 'w': 4.47, 'Leg': 50, 't': 6},
            'L65x65x5': {'A': 6.26, 'w': 4.91, 'Leg': 65, 't': 5},
            'L65x65x6': {'A': 7.44, 'w': 5.84, 'Leg': 65, 't': 6},
            'L65x65x8': {'A': 9.76, 'w': 7.66, 'Leg': 65, 't': 8},
            'L75x75x6': {'A': 8.73, 'w': 6.85, 'Leg': 75, 't': 6},
            'L75x75x9': {'A': 12.8, 'w': 10.1, 'Leg': 75, 't': 9},
            'L100x100x6': {'A': 11.8, 'w': 9.26, 'Leg': 100, 't': 6},
            'L100x100x8': {'A': 15.5, 'w': 12.2, 'Leg': 100, 't': 8},
            'L100x100x10': {'A': 19.2, 'w': 15.1, 'Leg': 100, 't': 10},
        }
        self.results = {}

    def calculate_participating_area(self):
        """
        Calculate Area of the Roof-to-Shell Junction (A) per F.5.1 and Figure F.2.
        Units: mm2
        """
        prop = self.angle_props.get(self.angle_size, {'A': 0, 'w': 0})
        A_angle = prop['A'] * 100.0 # cm2 to mm2
        return A_angle

    def run_check(self):
        # 1. Participating Area
        A_mm2 = self.calculate_participating_area()
        
        # 2. Key calculations
        Area_tank = math.pi * (self.D ** 2) / 4.0
        
        # Pressures resisted by gravity (in kPa)
        P_roof_plates = self.W_roof_plates / Area_tank
        P_roof_total = self.W_roof / Area_tank
        P_max_gravity = (self.W_roof + self.W_shell) / Area_tank
        
        # 3. Required Compression Area (F.5.1)
        Fy = 205.0 # Basic yield stress MPa (A36 top angle / shell)
        tan_theta = math.tan(self.theta)
        
        # F.5.1 required compression area
        if tan_theta > 0:
            P_net = max(0.0, self.P - P_roof_total)
            A_req_mm2 = (self.D**2 * P_net * 1000.0) / (1.27 * Fy * tan_theta)
        else:
            A_req_mm2 = 0.0
            
        # 4. Failure Pressure (5.10.2.6 API 650)
        # P_fail = 0.00127 * A * Fy / D^2 + 0.000122 * W_roof / D^2 (kPa)
        P_fail = 0.00127 * A_mm2 * Fy / (self.D**2) + 0.000122 * self.W_roof_plates * 1000 / (self.D**2)
        
        # 5. Frangibility Check under API 650 5.10.2.6
        warnings = []
        is_frangible = True
        
        # Slope check: must be <= 1:6 (0.1667)
        if self.slope > 0.1667:
            is_frangible = False
            warnings.append(f"Roof slope ({self.slope:.4f}) is steeper than 1:6 (0.1667) limit.")
            
        # Top shell course thickness check: must be <= 13 mm (1/2 in)
        if self.t_shell > 13.0:
            is_frangible = False
            warnings.append(f"Top course shell thickness ({self.t_shell:.1f} mm) exceeds 13.0 mm limit.")
            
        # Compression Area A limit (API 650 5.10.2.6.3):
        # A_max = W_plates_N / (2 * pi * R * F_y * tan(theta))
        R_mm = (self.D / 2.0) * 1000.0 # radius in mm
        W_plates_N = self.W_roof_plates * 1000.0
        
        if tan_theta > 0:
            A_max_mm2 = W_plates_N / (2 * math.pi * R_mm * Fy * tan_theta)
        else:
            A_max_mm2 = 0.0
            
        if A_mm2 > A_max_mm2 and A_max_mm2 > 0:
            is_frangible = False
            warnings.append(f"Provided compression area ({A_mm2:.1f} mm²) exceeds maximum allowable area for a frangible joint ({A_max_mm2:.1f} mm²).")
            
        # 6. Determine Annex F.2 Design Status & Warnings
        design_warnings = []
        
        # Scope limit: P_design <= 18 kPa
        if self.P > 18.0:
            design_warnings.append(f"Design pressure ({self.P:.2f} kPa) exceeds 18 kPa. This is outside the scope of API 650 Annex F (max 18 kPa / 2.5 psi). Custom pressure vessel design (ASME Sec. VIII) is recommended.")
            
        # Lift check:
        if self.P <= P_roof_plates:
            design_notes = f"Design pressure ({self.P:.3f} kPa) is less than or equal to roof plates resistance ({P_roof_plates:.3f} kPa). Top joint has no tendency to lift."
        elif self.P <= P_max_gravity:
            design_notes = f"Design pressure ({self.P:.3f} kPa) exceeds roof plate weight resistance ({P_roof_plates:.3f} kPa). The roof-to-shell joint is subject to uplift compression. Ring design (F.5) or frangible joint is satisfied."
        else:
            design_notes = f"Design pressure ({self.P:.3f} kPa) exceeds total tank dead weight resistance ({P_max_gravity:.3f} kPa). Mechanical anchors (Anchor Bolts) must be provided."
            design_warnings.append(f"Design pressure exceeds total tank dead weight resistance ({P_max_gravity:.3f} kPa). MECHANICAL ANCHORAGE (Anchor Bolts) IS MANDATORY per F.7.")
            
        if not is_frangible and self.P > P_roof_plates:
            design_warnings.append("⚠️ NON-FRANGIBLE JOINT: The roof-to-shell joint is non-frangible. Emergency venting devices (API 2000) or anchoring is mandatory for safety.")
            
        self.results = {
            'Top Angle': self.angle_size,
            'Detail': self.detail,
            'Provided Area (mm2)': A_mm2,
            'Junction Area (mm2)': A_mm2,
            'Required Area (mm2)': A_req_mm2,
            'Max Design Pressure P_max (kPa)': P_max_gravity,
            'Failure Pressure P_fail (kPa)': P_fail,
            'P_roof_plates_kPa': P_roof_plates,
            'P_roof_total_kPa': P_roof_total,
            'P_max_gravity_kPa': P_max_gravity,
            'Top Course Thickness (mm)': self.t_shell,
            'Max Frangible Area (mm2)': A_max_mm2,
            'Frangible?': 'Yes' if is_frangible else 'No',
            'Frangibility Warnings': warnings,
            'Design Notes': design_notes,
            'Design Warnings': design_warnings,
            'Status': 'PASS' if A_mm2 >= A_req_mm2 and self.P <= 18.0 else 'FAIL',
            'Notes': 'Refer to API 650 Annex F.2 / F.5'
        }
