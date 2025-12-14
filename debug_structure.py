from Structure_Design import StructureDesign

# Mock Inputs
D = 31.0
H = 20.0
loads = {'Live': 1.2, 'Snow': 0.0, 'Dead_Plate': 0.5, 'Dead_Add': 0.0}
struct_yield = 235.0

print(f"DEBUG: Initializing StructureDesign with D={D}, H={H}, loads={loads}")
try:
    struct = StructureDesign(D, loads, material_yield=struct_yield)
    struct.set_height(H)
    struct.run_design()
    
    print("DEBUG: Design Run Completed.")
    print("DEBUG: Results:")
    for k, v in struct.results.items():
        print(f"  {k}: {v}")
        
    # Check specifics
    raf_len = struct.results.get('Rafter Length (m)', 'MISSING')
    raf_wt = struct.results.get('Rafter Unit Weight (kg/m)', 'MISSING')
    print(f"DEBUG CHECK: Rafter Length={raf_len}, UnitWt={raf_wt}")

except Exception as e:
    print(f"DEBUG ERROR: {e}")
