
from Shell_Design import ShellDesign

def verify_case_04():
    # Parameters from Case 04-2 (Type 9 FRT)
    D = 78.0 # m
    H_shell = 17.6 # m
    H_design = 16.1 # m (From Dump Row 17)
    G = 0.897
    CA = 1.5 # mm
    P_design = 0.0 # Atmospheric (FRT)
    P_test = 0.0
    
    # Material Map (Same as Case 03-2, from Dump)
    material_names = [
        'A 553 Type 1',
        'A 645',
        'A 573 58',
        'A 573 65',
        'A 573 70',
        'A 516 55'
    ]
    
    # Target Results (Design t) from Dump (Col 65)
    # Row 18: 29.566154
    # Row 19: 24.361481
    # Row 20: 19.156808
    # Row 21: 13.952135
    # Row 22: 8.747463
    # Row 23: 4.377799
    
    target_td = [29.57, 24.36, 19.16, 13.95, 8.75, 4.38]
    
    num_courses = len(material_names)
    course_width = H_shell / num_courses # 2.933 m
    
    courses = []
    for i in range(num_courses):
        courses.append({
            'Course': str(i+1),
            'Width': course_width,
            'Material': material_names[i],
            'Thickness_Used': 10.0 # Placeholder
        })
        
    # Initialize Design
    shell = ShellDesign(
        diameter=D,
        height=H_shell,
        design_liquid_level=H_design, 
        test_liquid_level=H_design, # Assuming Test H = Design H for now (Dump says Test H=16100)
        specific_gravity=G,
        corrosion_allowance=CA,
        p_design=P_design, 
        p_test=P_test,
        efficiency=1.0,
        courses_input=courses
    )
    
    print("Running Verification for Case 04-2 (FRT)...")
    print(f"Inputs: D={D}m, H_shell={H_shell}m, H_liq={H_design}m, G={G}, P={P_design}")
    
    # Run
    shell.run_design(method='auto') # Should pick VDPM
    
    print("\n--- Results Comparison ---")
    print(f"Method: {shell.design_report_info['Method']}")
    print(f"{'Course':<8} {'Mat':<12} {'Calc (mm)':<12} {'Target (mm)':<12} {'Diff (mm)':<12} {'Status'}")
    
    for i, res in enumerate(shell.results):
        calc_td = res.get('td', 0)
        tgt = target_td[i] if i < len(target_td) else 0.0
        diff = calc_td - tgt
        status = "MATCH" if abs(diff) < 0.5 else "MISMATCH"
        
        print(f"{res['Course']:<8} {res['Material']:<12} {calc_td:<12.4f} {tgt:<12.4f} {diff:<12.4f} {status}")

if __name__ == "__main__":
    verify_case_04()
