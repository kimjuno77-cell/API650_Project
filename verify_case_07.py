
from Shell_Design import ShellDesign

def verify_case_07():
    # Parameters from Case 07-2 (Type 6 8x6)
    D = 8.0 # m
    H_shell = 6.0 # m
    H_design = 6.0 # m
    G = 0.87
    CA = 1.5 # mm
    P_design = 100.0 # mmAq (Different from 05/06)
    P_test = 100.0 # mmAq (Assumption, usually same if not specified, line 35 says 100)
    
    material_name = 'A 283 C' # Standard Name
    
    # Target Results (Design t) from Dump 07
    # Line 18: 3.148942
    # Line 19: 2.309576
    target_td = [3.15, 2.31] # Rounded for display match
    
    num_courses = 2
    course_width = H_shell / num_courses # 3.0 m
    
    courses = []
    for i in range(num_courses):
        courses.append({
            'Course': str(i+1),
            'Width': course_width,
            'Material': material_name,
            'Thickness_Used': 6.0 
        })
        
    # Initialize Design
    # Passing design_temp=150.0 to trigger derating
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
        courses_input=courses,
        design_temp=150.0
    )
    
    print("Running Verification for Case 07-2 (Type 6 8x6)...")
    print(f"Inputs: D={D}m, H_shell={H_shell}m, G={G}, CA={CA}mm, P={P_design}mmAq, Temp=150C")
    
    # Run
    shell.run_design(method='auto') # Should pick 1-Foot
    
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
    verify_case_07()
