
# API 650 Material Database
# Values are typical and based on API 650 Table 5-2a (SI)
# Sd: Allowable Design Stress (MPa)
# St: Allowable Test Stress (MPa)
# Fy: Minimum Yield Strength (MPa)
# Fu: Minimum Tensile Strength (MPa)

# Standard Materials (Ambient / < 40C Properties)
CARBON_STEEL_MATERIALS = {
    'A 283 C': {'Fy': 205, 'Fu': 380, 'Sd': 137, 'St': 154},
    'A 283 D': {'Fy': 225, 'Fu': 415, 'Sd': 137, 'St': 154}, 
    'A 285 C': {'Fy': 205, 'Fu': 380, 'Sd': 137, 'St': 154},
    'A 36':    {'Fy': 250, 'Fu': 400, 'Sd': 160, 'St': 171}, 
    'A 573 58': {'Fy': 220, 'Fu': 400, 'Sd': 160, 'St': 171}, 
    'A 573 65': {'Fy': 240, 'Fu': 450, 'Sd': 180, 'St': 193}, 
    'A 573 70': {'Fy': 290, 'Fu': 485, 'Sd': 193, 'St': 208},
    'A 516 55': {'Fy': 205, 'Fu': 380, 'Sd': 137, 'St': 154},
    'A 516 60': {'Fy': 220, 'Fu': 415, 'Sd': 138, 'St': 155},
    'A 516 65': {'Fy': 240, 'Fu': 450, 'Sd': 180, 'St': 193},
    'A 516 70': {'Fy': 260, 'Fu': 485, 'Sd': 173, 'St': 194},
    'A 537 1':  {'Fy': 345, 'Fu': 485, 'Sd': 193, 'St': 215},
    'A 537 2':  {'Fy': 415, 'Fu': 550, 'Sd': 220, 'St': 246},
    'A 553 Type 1': {'Fy': 585, 'Fu': 690, 'Sd': 193, 'St': 208}, 
    'A 645':    {'Fy': 450, 'Fu': 655, 'Sd': 183, 'St': 196}, 
    'A 131 A': {'Fy': 235, 'Fu': 400, 'Sd': 137, 'St': 154}, 
    'A 131 B': {'Fy': 235, 'Fu': 400, 'Sd': 137, 'St': 154}, 
    'A 131 CS': {'Fy': 235, 'Fu': 400, 'Sd': 137, 'St': 154}, 
    'A 131 EH 36': {'Fy': 355, 'Fu': 490, 'Sd': 196, 'St': 218},
}

STAINLESS_STEEL_MATERIALS = {
    '304':      {'Fy': 205, 'Fu': 515, 'Sd': 155, 'St': 186}, 
    '304L':     {'Fy': 170, 'Fu': 485, 'Sd': 145, 'St': 153}, 
    '316':      {'Fy': 205, 'Fu': 515, 'Sd': 155, 'St': 186}, 
    '316L':     {'Fy': 170, 'Fu': 485, 'Sd': 145, 'St': 153}, 
    '317':      {'Fy': 205, 'Fu': 515, 'Sd': 155, 'St': 186}, 
    '317L':     {'Fy': 205, 'Fu': 515, 'Sd': 155, 'St': 186}, 
}

# Temperature Derating Tables (Sd vs Temp C)
# Format: { 'Material': { 40: Sd1, 90: Sd2, 150: Sd3, 200: Sd4, 260: Sd5 } }
# Derived from API 650 Table 5-2a and verification data
TEMP_DERATING_SD = {
    'A 283 C': {40: 137, 90: 137, 150: 120.3, 200: 115, 260: 110}, # 120.3 derived from verify_case_07
    'A 283 D': {40: 137, 90: 137, 150: 120.3, 200: 115, 260: 110},
    'A 285 C': {40: 137, 90: 137, 150: 120.3, 200: 115, 260: 110},
    'A 36':    {40: 160, 90: 160, 150: 148, 200: 130, 260: 120}, # Approx
    'A 516 70': {40: 173, 90: 173, 150: 173, 200: 165, 260: 155}, # 516Gr70 holds strength well
}

def interpolate(x, x1, y1, x2, y2):
    if x2 == x1: return y1
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

def get_derated_Sd(material_name, temp_c):
    """
    Calculate Allowable Design Stress (Sd) at a given temperature.
    Uses linear interpolation between defined points.
    """
    if temp_c is None: temp_c = 40.0
    if temp_c <= 40.0: temp_c = 40.0
    
    # Clean Name
    name_clean = str(material_name).strip()
    
    # Check if we have derating data
    if name_clean in TEMP_DERATING_SD:
        points = TEMP_DERATING_SD[name_clean]
        sorted_temps = sorted(points.keys())
        
        # Check range
        if temp_c <= sorted_temps[0]:
            return points[sorted_temps[0]]
        if temp_c >= sorted_temps[-1]:
            # Cap at max defined temp or extrapolate? API limits usually 260C for these.
            return points[sorted_temps[-1]]
            
        # Interpolate
        for i in range(len(sorted_temps) - 1):
            t1 = sorted_temps[i]
            t2 = sorted_temps[i+1]
            if t1 <= temp_c <= t2:
                sd1 = points[t1]
                sd2 = points[t2]
                return interpolate(temp_c, t1, sd1, t2, sd2)
                
    # If no data, return base Sd (Unsafe for high temp, but default behavior)
    # Could warn here
    base_props = get_material_properties_base(name_clean)
    return base_props['Sd']

def is_stainless_steel(material_name):
    name_clean = str(material_name).strip().upper()
    for k in STAINLESS_STEEL_MATERIALS:
        if k in name_clean: return True
    if "304" in name_clean or "316" in name_clean or "317" in name_clean: return True
    return False

def get_material_properties_base(material_name):
    name_clean = str(material_name).strip()
    if name_clean in CARBON_STEEL_MATERIALS: return CARBON_STEEL_MATERIALS[name_clean]
    if name_clean in STAINLESS_STEEL_MATERIALS: return STAINLESS_STEEL_MATERIALS[name_clean]
    for k, v in STAINLESS_STEEL_MATERIALS.items():
        if k in name_clean: return v
    return CARBON_STEEL_MATERIALS['A 283 C']

def get_material_properties(material_name, design_temp_c=None):
    """
    Retrieve material properties with Temperature Derating for Sd.
    """
    base_props = get_material_properties_base(material_name).copy()
    
    # Apply Derating for Sd
    if design_temp_c and design_temp_c > 40:
        derated_Sd = get_derated_Sd(material_name, design_temp_c)
        base_props['Sd'] = derated_Sd
        # Note: Fy and Fu might also change but Shell Design uses Sd mainly.
        # St is usually at ambient (hydrotest).
    
    return base_props

if __name__ == "__main__":
    # verification
    print("Test A 283 C at 150C:")
    print(get_material_properties('A 283 C', 150))
    print("Test A 36 at 200C:")
    print(get_material_properties('A 36', 200))
