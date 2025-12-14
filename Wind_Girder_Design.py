import math

class WindGirderDesign:
    """
    Implements API 650 Section 5.9 Wind Girder Design.
    Checks for Intermediate Wind Girders.
    """
    def __init__(self, D, H, shell_courses, V_wind_kph):
        """
        :param D: Tank Diameter (nominal, m)
        :param H: Tank Height (m)
        :param shell_courses: List of dicts [{'t_used': mm, 'Width': m, ...}]
        :param V_wind_kph: Design Wind Speed (3-sec gust) in km/h or m/s?
                           API 650 5.9.7 uses V in km/h.
        """
        self.D = D
        self.H = H
        self.shell_courses = shell_courses
        self.V_wind_kph = V_wind_kph # Ensure units
        self.results = {}

    def calculate_intermediate_girders(self):
        """
        Determine if intermediate wind girders are required (API 650 5.9.7).
        """
        # 1. Transformed Shell Height (H_tr)
        # API 650 5.9.7.1:
        # The transformed height provides an equivalent height of a shell of uniform thickness (t_top).
        # H_tr = Sum( W_i * (t_top / t_i)^2.5 )
        
        # Get top course thickness
        if not self.shell_courses:
            return {'Status': 'No Data'}
            
        top_course = self.shell_courses[-1]
        t_top = top_course.get('t_used', 0.0)
        
        if t_top <= 0:
            return {'Status': 'Error', 'Message': 'Invalid Top Course Thickness'}
            
        H_tr = 0.0
        
        # Iterate all courses
        for course in self.shell_courses:
            w_i = course.get('Width', 0.0)
            t_i = course.get('t_used', 0.0)
            
            if t_i > 0:
                # Contribution to height: W * (t_top / t_i)^2.5
                term = (t_top / t_i) ** 2.5
                H_tr += w_i * term
                
        # 2. Maximum Unstiffened Height (H1)
        # API 650 5.9.7.1 SI Formula:
        # H1 = 9.47 * t * sqrt( (t/D)^3 ) * (190 / V)^2
        # where t=mm, D=m, V=km/h. Result H1 in meters.
        
        # Determine V in km/h
        if self.V_wind_kph <= 0: V_use = 190.0 # Default fallback (Standard design speed)
        else: V_use = self.V_wind_kph
        
        # Note: If V_use > 190 (which is high often), term_wind < 1.
        
        term_geom = 9.47 * t_top * math.sqrt( (t_top / self.D)**3 )
        term_wind = (190.0 / V_use)**2
        
        H1 = term_geom * term_wind # meters
        
        # 3. Check Requirement
        # If H_tr > H1, intermediate girders required.
        status = "Not Required"
        num_girders = 0
        min_Z = 0.0
        
        if H_tr > H1:
            # Girders needed
            # Number of girders needed to reduce spacing < H1
            # Num = ceil( H_tr / H1 ) - 1
            num_girders = math.ceil(H_tr / H1) - 1
            
            # If num_girders is 0 but H_tr > H1 (e.g. 1.01 * H1), we technically need 1 to split it?
            # ceil(1.01) = 2 -> 2-1 = 1. Correct.
            
            status = f"Required ({num_girders} Girders)"
            
            # Required Section Modulus (Z) for Intermediate Girder
            # API 650 5.9.7.6 refers to 5.9.6.1 logic:
            # Z = (D^2 * H_spacing * (V/190)^2) / 17
            # where Z is cm3, D in m, H_spacing in m, V in km/h.
            
            # Use H1 as the spacing (Limit design)
            H_sp = H_tr / (num_girders + 1) # Actual spacing if equally spaced
            
            Z_req_cm3 = (self.D**2 / 17.0) * H_sp * ((V_use / 190.0)**2)
            min_Z = Z_req_cm3
            
        else:
            status = "Not Required (H_tr <= H1)"

        if num_girders > 0:
             # Find Recommended Section
             rec_section = "Custom / Detail"
             rec_weight = 0.0
             
             # Search Database
             found = False
             # Sort by weight (efficiency)
             sorted_sect = sorted(WIND_GIRDER_SECTIONS.items(), key=lambda x: x[1]['w'])
             
             for name, props in sorted_sect:
                 if props['Z'] >= min_Z:
                     rec_section = name
                     rec_weight = props['w']
                     found = True
                     break
             
             if not found:
                 rec_section = "Check Large Sections (UPN 200+)"
                 
             self.results['Recommended Section'] = rec_section
             self.results['Section Weight (kg/m)'] = rec_weight
             
        return self.results

# Standard Structural Sections for Wind Girder (Simplified)
# Z in cm3, w in kg/m
WIND_GIRDER_SECTIONS = {
    "L 65x65x6": {'Z': 5.8, 'w': 5.91}, # Approx Z min
    "L 75x75x6": {'Z': 7.6, 'w': 6.85},
    "L 75x75x9": {'Z': 11.0, 'w': 9.96},
    "L 90x90x7": {'Z': 13.0, 'w': 9.61},
    "L 100x100x8": {'Z': 19.8, 'w': 12.2},
    "L 100x100x10": {'Z': 24.3, 'w': 15.0},
    "L 120x120x10": {'Z': 35.0, 'w': 18.2},
    "L 150x150x12": {'Z': 66.0, 'w': 27.3},
    
    # Channels (UPN) - Strong Axis
    "UPN 80":  {'Z': 26.5, 'w': 8.6},
    "UPN 100": {'Z': 41.2, 'w': 10.6},
    "UPN 120": {'Z': 60.7, 'w': 13.4},
    "UPN 140": {'Z': 86.4, 'w': 16.0},
    "UPN 160": {'Z': 116.0, 'w': 18.8},
    "UPN 180": {'Z': 150.0, 'w': 22.0},
    "UPN 200": {'Z': 191.0, 'w': 25.3}
}
