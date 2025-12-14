
import math
from Shell_Design import ShellDesign

def verify_case_03():
    # Parameters from Case 03-2 (For Education)
    D = 78.0 # m
    H = 17.6 # m
    G = 0.897
    CA = 1.5 # mm
    P_design = 76.5 * 9.80665 # mmH2O to Pa? 
    # Logic note: mmAq (mmH2O) approx 9.8 Pa. 
    # Use 76.5 mmH2O for P_design. 
    # But wait, Shell_Design calc uses head. 
    # P_design is Internal Pressure. 
    # Usually added to head? H_eff = H + P/(G*rho)?
    # Shell_Design expects P_design in mmH2O (see input).
    
    P_test = 76.5 # Approx test pressure same as design? Or see input.
    # Row 33 Col 6 says 76.5.
    
    # Material Map (Bottom to Top)
    # Deduced from dump: Courses 12 to 17 used.
    # Course 1 (Bottom) -> Dump Row 18 ("12") -> A 553 Type 1
    # Course 2 -> Dump Row 19 ("13") -> A 645
    # Course 3 -> Dump Row 20 ("14") -> A 573 58
    # Course 4 -> Dump Row 21 ("15") -> A 573 65
    # Course 5 -> Dump Row 22 ("16") -> A 573 70
    # Course 6 (Top) -> Dump Row 23 ("17") -> A 516 55
    
    material_names = [
        'A 553 Type 1',
        'A 645',
        'A 573 58',
        'A 573 65',
        'A 573 70',
        'A 516 55'
    ]
    
    # Target Results (Design t) from Dump (Col 65)
    # Row 18: 32.38
    # Row 19: 27.17
    # Row 20: 21.97
    # Row 21: 16.76
    # Row 22: 11.56
    # Row 23: 8.34
    
    target_td = [32.38, 27.17, 21.97, 16.76, 11.56, 8.34]
    
    num_courses = len(material_names)
    course_width = H / num_courses # 2.933 m
    
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
        height=H,
        design_liquid_level=H, 
        test_liquid_level=H,   
        specific_gravity=G,
        corrosion_allowance=CA,
        p_design=P_design, 
        p_test=P_test,
        efficiency=1.0,
        courses_input=courses
    )
    
    print("Running Verification for Case 03-2...")
    print(f"Inputs: D={D}m, H={H}m, G={G}, P={P_design}")
    
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
    verify_case_03()
