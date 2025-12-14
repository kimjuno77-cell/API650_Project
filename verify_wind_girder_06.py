
from Wind_Girder_Design import WindGirderDesign
from Structure_Design import ANGLE_SECTIONS

def verify_wind_girder_06():
    # Case 06 Parameters
    D = 8.0 # m
    H = 6.0 # m
    V_wind_kph = 162.0 # 45 m/s
    
    # Shell Courses
    # Assumption: Min Shell Thickness of 6.0mm or 6.5mm used?
    # Excel Dump Line 5 says "Min th = 6.5 mm".
    # Let's try t_top = 6.0mm and 6.5mm
    t_used = 6.0 # mm
    
    # 2 Courses, 3m each
    courses = [
        {'Course': '1', 'Width': 3.0, 't_used': t_used},
        {'Course': '2', 'Width': 3.0, 't_used': t_used}
    ]
    
    print("--- Verification of Wind Girder (Case 06) ---")
    print(f"D={D}m, H={H}m, V={V_wind_kph}km/h, t_shell={t_used}mm")
    
    # Initialize Design
    wg = WindGirderDesign(D, H, courses, V_wind_kph)
    
    # Run
    res = wg.calculate_intermediate_girders()
    
    print("Calculated Results:")
    for k, v in res.items():
        print(f"  {k}: {v}")
        
    Z_req = res.get('Required_Z_cm3', 0.0)
    # If not in dict, maybe I need to update WindGirderDesign to return it? 
    # Reading Wind_Girder_Design.py lines 80-99... it sets 'min_Z' but puts it where?
    # Ah, I need to check if 'min_Z' is in the returned dictionary.
    # The viewed code ended at line 100.
    
    # Let's inspect the returned dict keys in the script
    if 'min_Z_cm3' in res:
        Z_req = res['min_Z_cm3']
    elif 'Required_Z_cm3' in res:
        Z_req = res['Required_Z_cm3']
    elif 'Z_req' in res:
         Z_req = res['Z_req']
    else:
        # Manually calculate if missing from return (I should update WindGirderDesign later)
        # Re-calc locally for verification
        # H_tr calculation
        t_top = t_used
        H_tr = 0.0
        for c in courses:
             term = (t_top / c['t_used']) ** 2.5
             H_tr += c['Width'] * term
        
        # H1
        import math
        term_geom = 9.47 * t_top * math.sqrt( (t_top / D)**3 )
        term_wind = (190.0 / V_wind_kph)**2
        H1 = term_geom * term_wind
        
        print(f"  [Manual Calc] H_tr: {H_tr:.3f}m")
        print(f"  [Manual Calc] H1: {H1:.3f}m")
        
        if H_tr > H1:
            num = math.ceil(H_tr / H1) - 1
            H_sp = H_tr / (num + 1)
            Z_req = (D**2 / 17.0) * H_sp * ((V_wind_kph / 190.0)**2)
            print(f"  [Manual Calc] Required Z: {Z_req:.4f} cm3")
        else:
            print("  [Manual Calc] No Inter. Girder Required")
            Z_req = 0.0

    print(f"\nComparing against Excel Dump 'Intermediate stiffeners':")
    print(f"Target Threshold: > 0.90 (Fail) and <= 1.43 (Pass) ??")
    
    pass_matches = []
    fail_matches = []
    
    sections_to_check = [
        "L 25x25x3", "L 30x30x3", "L 40x40x3", "L 40x40x5", 
        "L 45x45x4", "L 50x50x4"
    ]
    
    print(f"{'Section':<12} {'Sx(cm3)':<8} {'Status (Calc)'}")
    
    for sec in sections_to_check:
        props = ANGLE_SECTIONS.get(sec)
        if not props: continue
        Sx = props['Sx']
        status = "Pass" if Sx >= Z_req else "Fail"
        print(f"{sec:<12} {Sx:<8.2f} {status}")

if __name__ == "__main__":
    verify_wind_girder_06()
