
from Shell_Design import ShellDesign

def verify_case_05():
    # Parameters from Case 05-2 (Type 1 8x6)
    D = 8.0 # m
    H_shell = 6.0 # m
    H_design = 6.0 # m (Line 17)
    G = 0.87 # (Line 25)
    CA = 1.5 # mm (Line 40)
    P_design = 76.5 # mmAq (Line 31) -> 0.75 kPa
    P_test = 76.5 # mmAq
    
    # Material
    # Line 40 doesn't explicitly name it in the usual spot, but Line 42 (Bottom) and 44 (Roof) are A 283 C.
    # Calculation checks suggest A 283 C (Sd ~ 137).
    material_name = 'A 283 C'
    
    # Target Results (Design t) from Dump
    # Line 18: 2.940815
    # Line 19: 2.203969
    target_td = [2.94, 2.20]
    
    num_courses = 2
    course_width = H_shell / num_courses # 3.0 m
    
    courses = []
    for i in range(num_courses):
        courses.append({
            'Course': str(i+1),
            'Width': course_width,
            'Material': material_name,
            'Thickness_Used': 6.0 # Placeholder
        })
        
    # Initialize Design
    shell = ShellDesign(
        diameter=D,
        height=H_shell,
        design_liquid_level=H_design, 
        test_liquid_level=H_design, 
        specific_gravity=G,
        corrosion_allowance=CA,
        p_design=P_design, 
        p_test=P_test,
        efficiency=1.0,
        courses_input=courses
    )
    
    print("Running Verification for Case 05-2 (8x6 Small Tank)...")
    print(f"Inputs: D={D}m, H_shell={H_shell}m, G={G}, CA={CA}mm, P={P_design}mmAq")
    
    # Run
    shell.run_design(method='auto') # Should pick 1-Foot for D=8m
    
    print("\n--- Results Comparison ---")
    print(f"Method: {shell.design_report_info['Method']}")
    print(f"{'Course':<8} {'Mat':<12} {'Calc (mm)':<12} {'Target (mm)':<12} {'Diff (mm)':<12} {'Status'}")
    
    for i, res in enumerate(shell.results):
        calc_td = res.get('td', 0)
        tgt = target_td[i] if i < len(target_td) else 0.0
        diff = calc_td - tgt
        status = "MATCH" if abs(diff) < 0.2 else "MISMATCH"
        
        print(f"{res['Course']:<8} {res['Material']:<12} {calc_td:<12.4f} {tgt:<12.4f} {diff:<12.4f} {status}")

if __name__ == "__main__":
    verify_case_05()
