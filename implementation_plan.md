# Implementation Plan - EFRT Error Fixes

## Goal Description
Fix repeated `AttributeError` and `NameError` issues occurring when "External Floating Roof" (EFRT) is selected. The goal is to make the application robust by correctly identifying the active roof mode (Fixed vs. EFRT) and conditionally executing relevant logic (e.g., Frangibility, Annex F, Weight Summary).

## User Review Required
> [!IMPORTANT]
> This plan disables "Frangibility Check" and "Annex F (Top Angle) Check" for EFRT, as these are primarily for Fixed Cone/Dome roofs. EFRT design (Annex C) has its own checks (Buoyancy, etc.) which are already implemented.

## Proposed Changes

### Logic & UI Updates (`app.py`)

#### [MODIFY] [app.py](file:///g:/다른 컴퓨터/내 노트북/API650_Project/app.py)
1.  **Global Safety Initialization**: Ensure `annex_f` and `anchor_chair` are initialized variables (even if technically unused for EFRT) or handle their absence.
    -   *Current Status*: `annex_f` is initialized around line 1053. It depends on `w_roof_kN`. This seems safe if `w_roof_kN` is valid.
2.  **Weight Summary Section (~Line 1520)**:
    -   Replace the direct call `roof_design.calculate_roof_weight()` with logic that checks `roof_type`.
    -   If EFRT: Use `W_roof_kg` (calculated earlier from EFRT results).
    -   If Fixed: Use `roof_design.calculate_roof_weight()`.
3.  **Frangibility & Annex F Display (~Line 1510-1532)**:
    -   Wrap the entire "Annex F (Top Angle)" and "Frangible Roof Check" UI blocks in `if roof_design:`.
    -   This prevents accessing `annex_f.results` or `roof_design.check_frangibility` when they are irrelevant or invalid.
4.  **Report Data Preparation**:
    -   Ensure `efrt_res` is correctly populated in the `results` dictionary sent to the Report Generator.
    -   Ensure `roof_res` (Fixed Roof) is empty or safe for EFRT.

## Verification Plan

### Manual Verification
1.  **Scenario 1: External Floating Roof (EFRT)**
    -   Select "External Floating Roof".
    -   Run Calculations.
    -   **Expectation**: No `AttributeError` or crash.
    -   **Expectation**: "Weight Summary" shows EFRT weight.
    -   **Expectation**: "Frangibility" and "Annex F" sections are HIDDEN.
    -   **Expectation**: "Results" tab shows Deck Thickness and Buoyancy Safety Factor.
2.  **Scenario 2: Supported Cone Roof (Fixed)**
    -   Select "Supported Cone Roof".
    -   Run Calculations.
    -   **Expectation**: "Frangibility" and "Annex F" sections are VISIBLE and populated.

### Automated Checks
None (Manual testing required due to UI nature).
