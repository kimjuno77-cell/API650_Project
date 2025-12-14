
from EFRT_Design import EFRTDesign

def verify_efrt_logic():
    print("--- Verifying EFRT Logic against EFRT Calculation.xls Dump ---")
    
    # Tank Data from Dump
    # Di = 26806 mm = 26.806 m
    # Sy = 275 MPa (A 516 Gr 65N, though dump says 275 Yield? Wait, sample says Material SA 516 Gr 65N, Yeild 275)
    # SG = 0.7 to 1.0 (Design)
    
    diameter = 26.806
    yield_strength = 275.0
    sg = 0.7 # Minimum SG for Buoyancy check usually critical? or Design SG? Use 0.7
    
    efrt = EFRTDesign(diameter, yield_strength, sg)
    
    # Set Geometry from Dump
    # Hor = 800, Hir = 650, w = 1700, N = 16
    efrt.set_pontoon_geometry(width=1700, h_out=800, h_in=650, n_pontoons=16)
    
    # Set Thicknesses from Dump
    # Outer Rim = 8, Inner Rim = 10, Top/Btm = 6, Deck = 8
    efrt.set_thickness(t_deck=8, t_rim_out=8, t_rim_in=10, t_pon_top=6, t_pon_btm=6)
    
    # 1. Deck Thickness Check
    efrt.check_deck_thickness()
    print(f"Deck Check: {efrt.results.get('Deck_Thickness_Check')}")
    
    # 2. Buoyancy Check
    efrt.calculate_buoyancy()
    print(f"Buoyancy Results: {efrt.results}")
    
    # Expected Results?
    # We don't have the final calculation result in the dump, only inputs.
    # But we can verify if the calculation runs without error and produces reasonable values.
    
    # Manual Check estimate:
    # Pontoon Arrea approx: Pi*(D_out^2 - D_in^2)/4
    # D_out ~= 26.8 - 0.4 = 26.4
    # D_in ~= 26.4 - 3.4 = 23.0
    # Area ~= Pi/4 * (26.4^2 - 23.0^2) ~= 0.785 * (696 - 529) ~= 131 m2
    # Vol ~= 131 * 0.725 (avg ht) ~= 95 m3
    # Buoyancy = 95 * 1000 * 0.7 * 9.81 ~= 650 kN
    
    # Weight:
    # 131m2 * 2 (top/btm) * 6mm -> ~12.5 ton
    # Deck: Pi/4 * 23^2 = 415 m3 * 8mm -> ~26 ton
    # Rims... total roughly 40-50 ton? ~400-500 kN?
    # SF should be > 1.0.
    
if __name__ == "__main__":
    verify_efrt_logic()
