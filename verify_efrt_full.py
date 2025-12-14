
from InputReader import InputReader
from EFRT_Design import EFRTDesign
import os

def verify_full_integration():
    file_path = "EFRT Calculation.xls"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print(f"--- Full Verification with {file_path} ---")
    
    # 1. Read Inputs
    try:
        reader = InputReader(file_path)
        params = reader.get_efrt_parameters()
        print("Read EFRT Params:")
        # Get Main Design Params for SG
        design_params = reader.get_design_parameters()
        sg = design_params.get('G', 0.7)
        
        # Tank Diameter: Prefer EFRT sheet value if exists (for consistency)
        if params.get('Tank_D', 0) > 0:
            diameter = params.get('Tank_D')
            print(f"Using Diameter from Floating Roof Sheet: {diameter}m")
        else:
            diameter = design_params.get('D', 0)
            print(f"Using Diameter from Main Input: {diameter}m")
            
        yield_strength = 275.0 # Hardcoded for now
        
        print(f"\nTank Params: D={diameter}m, SG={sg}")
        
    except Exception as e:
        print(f"Error reading inputs: {e}")
        return

    # 2. Run Design
    try:
        efrt = EFRTDesign(diameter, yield_strength, sg)
        
        efrt.set_pontoon_geometry(
            width=params.get('Width_Pontoon', 0),
            h_out=params.get('H_outer', 0),
            h_in=params.get('H_inner', 0),
            n_pontoons=params.get('N_Pontoons', 0)
        )
        
        efrt.set_thickness(
            t_deck=params.get('T_Deck', 0),
            t_rim_out=params.get('T_Rim_Outer', 0),
            t_rim_in=params.get('T_Rim_Inner', 0),
            t_pon_top=params.get('T_Pon_Top', 0),
            t_pon_btm=params.get('T_Pon_Btm', 0)
        )
        
        # Check
        efrt.check_deck_thickness()
        efrt.calculate_buoyancy()
        
        # Check Rafter if size exists
        rafter_size = params.get('Rafter_Size', '')
        if rafter_size:
            efrt.check_pontoon_rafter(rafter_size)
            
        # Check Roof Legs
        leg_od = params.get('Leg_OD', 0)
        leg_thk = params.get('Leg_Thk', 0)
        num_legs = params.get('N_Pontoons', 16) # Assume Pontoon Legs count = N_pontoons? Or explicit Leg count?
        # Dump inspection found "Leg" = 16 at Row 65.
        
        if leg_od > 0:
            efrt.check_roof_leg(leg_od, leg_thk, length_m=2.0, num_legs=num_legs)
        
        print("\n--- Calculation Results ---")
        print(f"Deck Check: {efrt.results.get('Deck_Thickness_Check')}")
        print(f"Buoyancy Results: Safety Factor {efrt.results.get('Safety_Factor')}")
        print(f"Rafter Check: {efrt.results.get('Rafter_Check')}")
        print(f"Leg Check: {efrt.results.get('Leg_Check')}")
        
    except Exception as e:
        print(f"Error running logic: {e}")

if __name__ == "__main__":
    verify_full_integration()
