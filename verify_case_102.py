
import math
from Shell_Design import ShellDesign
from Materials import CARBON_STEEL_MATERIALS

def verify_102():
    print("--- Verification Case 716-D-102 ---")
    print("(Note: Inputs assumed identical to 716-D-101 due to unreadable PDF source)")
    
    # Inputs (Assumed Identical to 101)
    D = 71.6 # m
    H = 20.0 # m
    G = 1.0  # SG
    CA = 0.0 # mm
    mat_name = "A 516 70"
    E = 1.0
    
    # Courses (Extracted from 101 Report Dump - Applied to 102)
    # C1-C5: 2900mm
    # C6-C7: 1850mm
    # C8: 1800mm
    courses_input = []
    
    # 5 Courses of 2.9m
    for i in range(5):
        courses_input.append({
            'Course': i+1,
            'Material': mat_name,
            'Width': 2.9,
            'Thickness_Used': 0.0
        })
    
    # 2 Courses of 1.85m
    for i in range(2):
        courses_input.append({
            'Course': 5+i+1,
            'Material': mat_name,
            'Width': 1.85,
            'Thickness_Used': 0.0
        })
        
    # 1 Course of 1.8m
    courses_input.append({
        'Course': 8,
        'Material': mat_name,
        'Width': 1.8,
        'Thickness_Used': 0.0
    })
    
    shell_design = ShellDesign(
        diameter=D,
        height=H,
        design_liquid_level=H, # Full
        test_liquid_level=H,
        specific_gravity=G,
        corrosion_allowance=CA,
        p_design=0, 
        p_test=0,
        efficiency=E,
        courses_input=courses_input
    )
    
    # Run VDM
    print(f"Running VDM for D={D}m, H={H}m, SG={G}, Mat={mat_name}")
    shell_design.run_design(method='vdm')
    
    print("\n--- Results (VDM) ---")
    print(f"{'Course':<10} {'Width(m)':<10} {'td(mm)':<10} {'tt(mm)':<10} {'t_use(mm)':<10} {'Status'}")
    
    for c in shell_design.shell_courses:
        c_id = c['Course']
        w = c['Width']
        td = c['td']
        tt = c['tt']
        t_use = c['t_used']
        status = c['Status']
        print(f"{c_id:<10} {w:<10.3f} {td:<10.2f} {tt:<10.2f} {t_use:<10.2f} {status}")
        
    w_kg, w_N = shell_design.calculate_shell_weight()
    print(f"\nTotal Shell Weight: {w_kg:.1f} kg ({w_kg/1000.0:.1f} ton)")

if __name__ == "__main__":
    verify_102()
