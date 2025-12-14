
import math
from Structure_Design import StructureDesign, ANGLE_SECTIONS

def verify_roof_06():
    # Case 06 Input Parameters
    D_mm = 8000.0
    R_m = D_mm / 2000.0 # 4.0 m
    
    Live_Load_kPa = 1.2 
    Dead_Load_kPa = 0.5 
    Total_Load_kPa = Live_Load_kPa + Dead_Load_kPa # 1.7
    
    Fy_A36 = 250.0 # MPa
    
    structure = StructureDesign(diameter=D_mm/1000.0, loads=None, material_yield=Fy_A36)
    
    possible_Ns = [12] # Check N=12
    
    print("--- Verification of Roof Rafters (Case 06) ---")
    print(f"Radius = {R_m} m, Load = {Total_Load_kPa} kPa")
    print("Verifying that Small Angles FAIL (matching Dump):")
    
    # Sections to check
    # Small Angles (Left List in Dump - likely Wind Girder, but checking Rafter Logic)
    # Large Angles (Right List in Dump - likely Rafters, showed Failure)
    
    sections_checking = [
        ("L 40x40x5", "Pass?"), # Passed in Left List
        ("L 75x75x6", "Fail"), # Failed in Right List
        ("L 100x100x13", "Fail") # Failed in Right List (my read)
    ]
    
    print(f"{'Section':<12} {'Sx(cm3)':<8} {'Dump':<8} {'Result (N=12)'}")
    
    for sec_name, dump_stat in sections_checking:
        props = ANGLE_SECTIONS.get(sec_name)
        if not props:
            print(f"{sec_name} Not Found")
            continue
            
        Sx = props['Sx']
        
        # Calc
        N = 12
        p = 2 * math.pi * R_m / N
        q = Total_Load_kPa
        w = q * p
        L = R_m
        M = (w * L**2) / 8.0
        
        check, ratio, fb = structure.check_rafter_bending(M, Sx)
        res = "Pass" if check else "Fail"
        print(f"{sec_name:<12} {Sx:<8.2f} {dump_stat:<8} {res} (Ratio {ratio:.2f})")

if __name__ == "__main__":
    verify_roof_06()
