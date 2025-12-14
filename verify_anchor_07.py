
# Verification of Seismic Parameters for Case 07-2
# Based on excel_dump_07.txt data

def verify_seismic_07():
    print("--- Verification of Seismic Parameters (Case 07) ---")
    
    # Inputs from Excel Dump 07
    # Line 35: Site Class D
    # Line 42: SS = 0.6
    # Line 43: S1 = 0.08 # (Wait, Dump 07 Line 43 says S1 0.08)
    
    site_class = 'D'
    Ss = 0.6
    S1 = 0.08 # Adjusted from 0.08 in dump? Line 43 says "S1 0.08".
    
    print(f"Inputs: Site Class={site_class}, Ss={Ss}, S1={S1}")
    
    # Target Values from Dump
    # Line 49: Fa = 1.2
    # Line 50: Fv = 1.65 (Wait, Line 50 says Fv 1.65)
    # Line 47: SDS = 0.48 (Wait, Line 47 Col 120 says SDS = 0.042667?? No, Line 47 in Dump 07 says SDS=??)
    # Let's re-read Dump 07 Line 47 carefully.
    
    # Dump 07 Line 47 (text):
    # "SDS = 0.042667" (Col 120 approx)
    # Wait, Dump 07 Line 46: ...
    # Dump 06 Line 47 says "SDS = 0.48". (Check Dump 06)
    # My previous thought said "Dump 07 Line 47 SDS = 0.48".
    # Let's check the file content I viewed for Dump 07.
    
    # Value in Dump 07 (Step 1635 view):
    # Line 47 Col 100+: `SDS = 0.042667` ?
    # Line 48: `SD1 = 0.032`.
    # Line 49: `Fa = 1.6`. (`Ai = 0.013333`).
    # Line 50: `Fv = 2.4`. (`Ac = 0.010154`).
    
    # WAIT. The values in Dump 07 are DIFFERENT from my previous "Dump 06" memory?
    # Dump 07 Line 42: `SS 0.04` ??
    # Dump 07 Line 42 Col 100+: `SS 0.04`.
    # Dump 07 Line 43 Col 100+: `S1 0.02`.
    
    # Ah! I misread the specific values in the last step.
    # Dump 07 (Step 1635):
    # Line 42: `SS 0.04`
    # Line 43: `S1 0.02`
    # Line 49: `Fa 1.6`
    # Line 50: `Fv 2.4`
    # Line 47: `SDS 0.042667`.
    # Line 48: `SD1 0.032`.
    
    # Let's verify THESE values.
    # Case 07 is likely a Low Seismic case.
    
    actual_Ss = 0.04
    actual_S1 = 0.02
    target_Fa = 1.6
    target_Fv = 2.4
    target_SDS = 0.042667
    target_SD1 = 0.032
    
    print(f"Corrected Inputs from Dump 07: Ss={actual_Ss}, S1={actual_S1}")
    print(f"Targets: Fa={target_Fa}, Fv={target_Fv}, SDS={target_SDS}, SD1={target_SD1}")
    
    # 1. Calculate Fa, Fv (ASCE 7 Tables 11.4-1, 11.4-2)
    # For Site Class D:
    # Ss <= 0.25 -> Fa = 1.6
    # S1 <= 0.1  -> Fv = 2.4
    
    # Calc
    calc_Fa = 1.6 # Since Ss=0.04 < 0.25
    calc_Fv = 2.4 # Since S1=0.02 < 0.1
    
    print(f"Calculated Fa: {calc_Fa} (Target {target_Fa}) -> {'MATCH' if calc_Fa == target_Fa else 'MISMATCH'}")
    print(f"Calculated Fv: {calc_Fv} (Target {target_Fv}) -> {'MATCH' if calc_Fv == target_Fv else 'MISMATCH'}")
    
    # 2. Calculate SMS, SM1
    # SMS = Fa * Ss
    # SM1 = Fv * S1
    SMS = calc_Fa * actual_Ss # 1.6 * 0.04 = 0.064
    SM1 = calc_Fv * actual_S1 # 2.4 * 0.02 = 0.048
    
    # 3. Calculate SDS, SD1
    # SDS = 2/3 * SMS
    # SD1 = 2/3 * SM1
    
    SDS = (2.0/3.0) * SMS
    SD1 = (2.0/3.0) * SM1
    
    print(f"Calculated SDS: {SDS:.6f} (Target {target_SDS})")
    print(f"Calculated SD1: {SD1:.6f} (Target {target_SD1})")
    
    diff_SDS = abs(SDS - target_SDS)
    diff_SD1 = abs(SD1 - target_SD1)
    
    status_SDS = "MATCH" if diff_SDS < 1e-5 else "MISMATCH"
    status_SD1 = "MATCH" if diff_SD1 < 1e-5 else "MISMATCH"
    
    print(f"Status SDS: {status_SDS}")
    print(f"Status SD1: {status_SD1}")
    
    # 4. Impact on Anchor Design
    # Ai formula (API 650 E.6.1.1 or similar?)
    # Line 49: Ai = 0.013333
    # Ai = SDS * I / R_factor? Or something like that.
    # Dump Line 49 says "Ai = 0.013333".
    # SDS = 0.042667.
    # 0.042667 * (something) = 0.013333?
    # 0.042667 / 3.2 = 0.013333.
    # Is R = 3.2? Or I/R?
    # Importance I?
    # Line 51: Importance factor I = 1.25.
    # Ai = SDS * I / R ?
    # If I=1.25: 0.042667 * 1.25 = 0.05333.
    # If Ai = 0.01333:
    # Maybe R = 4? (Self-anchored) or R=Something?
    # 0.05333 / 4 = 0.01333.
    # So if R = 4, then Ai matches EXACTLY.
    # API 650 Table E.4: Anchorage system.
    # Self-anchored flat-bottom tanks: Rw = 3.5 (or similar).
    # Mechanically anchored: Rw = 4.0?
    # Dump Line 39: "Anchorage System ... 2. Mechanically - Anchored".
    # Standard usually R=4 for Mechanically Anchored?
    # Let's Verify R=4 assumption.
    
    calc_Ai = SDS * (1.25 / 4.0)
    print(f"Calculated Ai (assuming I=1.25, R=4): {calc_Ai:.6f} (Target 0.013333)")

if __name__ == "__main__":
    verify_seismic_07()
