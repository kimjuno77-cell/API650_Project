
import math
from Shell_Design import ShellDesign

def verify_t033():
    # Parameters from Target Sample T-033 extraction
    D = 65.334 # m
    H = 20.0 # m
    
    # Tuned Parameters based on Course 1 match attempt
    G = 0.965 
    CA = 1.6 
    P_design = 0
    P_test = 0
    
    # Material
    mat_name = 'A 573 70'
    
    # Courses
    # Target had 9 or 10 values? Found 9 distinct descending + 7.7 mixed.
    # Pattern: 33, 20, 18, 15, 12, 9.7, 9.2, 5.2, 2.1
    # Let's assume 10 courses for H=20m (2m each).
    courses = []
    num_courses = 10
    course_width = H / num_courses
    
    for i in range(num_courses):
        courses.append({
            'Course': str(i+1),
            'Width': course_width,
            'Material': mat_name,
            'Thickness_Used': 10.0 
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
    
    # Run Verification
    print("Running Shell Design Verification for T-033...")
    print(f"Inputs: D={D}m, H={H}m, G={G}, CA={CA}mm, Mat={mat_name} (Sd=193)")
    
    shell.run_design(method='auto')
    
    print("\n--- Results Comparison ---")
    print(f"Method Applied: {shell.design_report_info['Method']}")
    
    # Target Values extracted from report (approximate mapping)
    target_td = [33.22, 20.41, 17.96, 15.16, 12.43, 9.70, 9.25, 7.71, 5.25, 2.16]
    # Added 7.71 to make 10 items, placing it logically? 
    # Wait, 9.25 -> 5.25 is big. 7.71 fits in between.
    
    print("\nCalculated vs Target Thicknesses (td):")
    print(f"{'Course':<8} {'Calc (mm)':<12} {'Target (mm)':<12} {'Diff (mm)':<12} {'Status'}")
    
    for i, res in enumerate(shell.results):
        calc_td = res.get('td', 0)
        tgt = target_td[i] if i < len(target_td) else 0.0
        diff = calc_td - tgt
        status = "MATCH" if abs(diff) < 0.5 else "MISMATCH"
        
        print(f"{res['Course']:<8} {calc_td:<12.4f} {tgt:<12.4f} {diff:<12.4f} {status}")
        
if __name__ == "__main__":
    verify_t033()
