
import math

class AnchorBoltDesign:
    def __init__(self, diameter, design_pressure, uplift_load_wind, uplift_load_seismic, shell_weight, roof_weight, vertical_acceleration_Av=0.0):
        """
        Initialize Anchor Bolt Design.
        
        :param diameter: Tank Diameter (m)
        :param design_pressure: Internal Design Pressure (kPa)
        :param uplift_load_wind: Uplift due to Wind (kN)
        :param uplift_load_seismic: Uplift due to Seismic (kN)
        :param shell_weight: Corroded Shell Weight (kN) -> resisting force
        :param roof_weight: Corroded Roof Plate Weight (kN) -> resisting force
        :param vertical_acceleration_Av: Vertical Seismic Acceleration Parameter (g)
        """
        self.D = diameter
        self.P_design = design_pressure
        self.U_wind = uplift_load_wind
        self.U_seismic = uplift_load_seismic
        self.W_shell = shell_weight
        self.W_roof = roof_weight
        self.Av = vertical_acceleration_Av
        self.results = {}

    def calculate_anchorage(self):
        """
        Determine if anchors are required and calculate size (API 650 5.12 / F.7).
        """
        # 1. Calculate Uplift Load due to Internal Pressure (F.7.1)
        # U_pressure = P * Area (but usually P * Pi * D^2 / 4)
        # API 650 F.1.2: Uplift = (P - 0.00024*th) ... complicated.
        # Simplified: Uplift = P * Area_projected using P_design
        radius = self.D / 2.0
        area = math.pi * (radius ** 2)
        
        # Uplift Forces (Load)
        U_pres_design = self.P_design * area # kN
        
        # Resisting Forces (Dead Load)
        W_DL_nominal = self.W_shell + self.W_roof
        
        # Load Cases (Simplified representation of Table 5.21a/b)
        uplift_cases = []
        
        # Case 1: Design Pressure + Wind
        # Load = P_design + Wind Uplift
        # Resist = Dead Load (Nominal)
        # Note: API 650 5.12.2 uses nominal weight for wind check.
        load_1 = U_pres_design + self.U_wind
        resist_1 = W_DL_nominal
        net_1 = load_1 - resist_1
        uplift_cases.append({
            'Case': 'Design Pressure + Wind',
            'S_uplift': load_1, # Total Uplift Load
            'W_resist': resist_1, # Resisting Weight
            'Net_Uplift': max(0, net_1)
        })
        
        # Case 2: Design Pressure + Seismic
        # Load = P_design + Seismic Uplift
        # Resist = Dead Load (Reduced by Av)
        load_2 = U_pres_design + self.U_seismic
        reduction_factor = 1.0 - (0.4 * self.Av)
        resist_2 = W_DL_nominal * reduction_factor
        net_2 = load_2 - resist_2
        uplift_cases.append({
            'Case': 'Design Pressure + Seismic',
            'S_uplift': load_2,
            'W_resist': resist_2,
            'Net_Uplift': max(0, net_2)
        })
        
        # Case 3: Design Pressure Only
        # Load = P_design
        # Resist = Dead Load
        load_3 = U_pres_design
        resist_3 = W_DL_nominal
        net_3 = load_3 - resist_3
        uplift_cases.append({
            'Case': 'Design Pressure Only',
            'S_uplift': load_3,
            'W_resist': resist_3,
            'Net_Uplift': max(0, net_3)
        })
        
        # Determine Max Uplift
        net_uplift = max([case['Net_Uplift'] for case in uplift_cases])
        
        status = "Anchors Not Required"
        req_area = 0.0
        num_bolts = 0
        bolt_dia = 0.0
        
        if net_uplift > 0:
            status = "Anchors Required"
            Sd_bolt = 140.0 # MPa (A 307 / A 36)
            F_uplift_N = net_uplift * 1000.0
            req_area = F_uplift_N / Sd_bolt # mm2
            
            # Select Bolts
            perimeter = math.pi * self.D
            min_bolts_spacing = int(perimeter / 3.0) + 1
            if min_bolts_spacing < 4: min_bolts_spacing = 4
            
            num_bolts = min_bolts_spacing
            
            # Ensure multiple of 4
            rem = num_bolts % 4
            if rem != 0:
                num_bolts += (4 - rem)
            
            area_per_bolt = req_area / num_bolts
            bolt_dia = math.sqrt(area_per_bolt * 4 / math.pi)
            if bolt_dia < 20: bolt_dia = 24
            else: bolt_dia = math.ceil(bolt_dia / 2) * 2
            
            # Chair Dimensions (Approximate Standard)
            # Hc ~ 12*d, Top Plate ~ 6*d width
            h_chair = max(300, 10 * bolt_dia)
            w_top = max(100, 4 * bolt_dia + 40) # clearance
            t_top = max(12, bolt_dia * 0.75)
            
        else:
             h_chair = 0
             w_top = 0
             t_top = 0
            
        self.results = {
            'Net Uplift Force (kN)': net_uplift,
            'Status': status,
            'Required Bolt Area (mm2)': req_area,
            'Number of Bolts': num_bolts,
            'Bolt Diameter (mm)': bolt_dia,
            'Chair Height (mm)': h_chair,
            'Top Plate Width (mm)': w_top,
            'Top Plate Thk (mm)': t_top,
            'Uplift_Table': uplift_cases
        }
        
    def run_design(self):
        self.calculate_anchorage()
        print(f"Anchor Design: {self.results['Status']}")
        if self.results['Number of Bolts'] > 0:
            print(f"  Qty: {self.results['Number of Bolts']} x M{self.results['Bolt Diameter (mm)']}")
            
