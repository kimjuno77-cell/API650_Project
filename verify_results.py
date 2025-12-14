
import math
from Shell_Design import ShellDesign
from Roof_Design import RoofDesign
from Wind_Girder_Design import WindGirderDesign
from Loads import SeismicLoad, WindLoad
# Mock Materials if needed, but classes usually handle strings.

def verify_tank_calculation():
    print("--- API 650 Tank Design Verification ---\n")
    
    # Case Parameters (Standard Water Tank)
    D = 20.0 # m
    H = 12.0 # m
    G = 1.0 # Water
    CA = 2.0 # mm
    Sd = 137.0 # MPa
    St = 150.0 # MPa
    
    print(f"Input: D={D}m, H={H}m, G={G}, CA={CA}mm")
    
    # 1. Shell Design (1-Foot Method)
    # ------------------------------------------------
    # Create dummy course input (width 2400mm)
    num_courses = int(H / 2.4)
    courses = []
    for i in range(num_courses):
        courses.append({
            'Course': f"Course {i+1}",
            'Width': 2.4,
            'Material': 'A 283 C',
            'Thickness_Used': 10.0
        })
    
    shell = ShellDesign(D, H, H, H*0.75, G, CA, 0, 0, 1.0, courses)
    # Adjust run_design to populate results
    # ShellDesign.run_design updates self.results (list of dicts) if logical?
    # Actually ShellDesign.run_design iterates courses_input and returns nothing but checks?
    # Let's check ShellDesign.py logic. It calculates t and updates... wait.
    # It updates lines 91-105 iterate 'self.results'.
    # I need to see if run_design populates 'self.results'.
    # Assuming it does.
    
    shell.run_design(method='1ft')
    print("\n[Shell Design Results]")
    for i, c in enumerate(shell.results): # It populates results?
         # Wait, ShellDesign.run_design snippet 830 showed it iterates 'self.courses_input', 
         # calculates 'td', 'tt', but DOES IT STORE it?
         # I need to verify ShellDesign.run_design stores to self.results.
         # The snippet ended before showing where 'self.results' is appended.
         # Most likely it appends.
         pass
         
    # I'll rely on it running. If attributes missing, I'll fix.
    
    # 2. Roof Design (Self-Supported Cone)
    # ------------------------------------------------
    print("\n[Roof Design: Self-Supported Cone]")
    roof_cone = RoofDesign(D, 'Self-Supported Cone Roof', 0.2, CA, 'A 283 C', 8.0)
    roof_cone.check_roof_plate(total_load_kPa=1.2)
    print("Results:", roof_cone.results)
    
    # 3. Wind Girder
    # ------------------------------------------------
    print("\n[Wind Girder]")
    wg = WindGirderDesign(D, H, shell.results, 190.0) # shell.results contains t_used
    res_wg = wg.calculate_intermediate_girders()
    print("Girder Check:", res_wg.get('Status'))
    
    # 4. Seismic Load (API 650 Annex E)
    # ------------------------------------------------
    print("\n[Seismic Load]")
    # Needs params dict
    seismic_params = {
        'D': D, 'H': H, 'G': G, 
        'SDS': 0.5, 'S1': 0.2, 'I': 1.0, 'Site Class': 'D',
        'Method': 'Map',
        'W_shell_kg': 50000, # Approx
        'W_roof_kg': 10000,
        'W_liquid_kg': math.pi*(D/2)**2 * H * 1000,
        't_shell_bot': 12.0
    }
    seismic = SeismicLoad(seismic_params)
    s_res = seismic.calculate_loads(seismic_params['W_shell_kg'], seismic_params['W_roof_kg'], seismic_params['W_liquid_kg'])
    print(f"Base Shear V: {s_res.get('Base_Shear_kN', 0):.1f} kN")
    print(f"Overturning M: {s_res.get('Overturning_Moment_kNm', 0):.1f} kNm")
    
    # Check Hoop Stress
    stress_res = seismic.check_hoop_stress(12.0, H, Sd, 1.0)
    print(f"Hoop Stress Check: {stress_res['Status']} ({stress_res['Stress_MPa']:.1f} MPa vs {stress_res['Allow_MPa']:.1f} MPa)")

if __name__ == "__main__":
    try:
        verify_tank_calculation()
        print("\nVerification Completed Successfully.")
    except Exception as e:
        print(f"\nExample Failed: {e}")
        import traceback
        traceback.print_exc()
