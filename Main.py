import math
import os
from InputReader import InputReader
from Shell_Design import ShellDesign
from Roof_Design import RoofDesign
from Loads import WindLoad, SeismicLoad
from Anchor_Design import AnchorBoltDesign
from Appendix_F import AppendixF, FrangibleCheck
from ReportGenerator import ReportGenerator
from datetime import datetime


def generate_report_filename(input_file):
    base = os.path.basename(input_file)
    name, ext = os.path.splitext(base)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"Calc_Report_{name}_{timestamp}.xlsx"

import sys

def main():
    print("============================================================")
    print("API 650 Tank Design Program - Main Execution")
    print("============================================================")
    
    # Default file
    default_input = "Excel_Logic_input_03-1 i-070936-67-T-0319-0327-Type4-78x18-(For_Education)-Ver. 1.05.xls"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        print(f"Using Input File from Command Line: {input_file}")
    else:
        input_file = default_input
        print(f"Using Default Input File: {input_file}")
        
    # Check priority: if default doesn't exist but Template exists, use Template?
    if input_file == default_input and not os.path.exists(input_file):
        if os.path.exists("API650_Input_Template.xlsx"):
            print(f"Default file not found. Switching to Template: API650_Input_Template.xlsx")
            input_file = "API650_Input_Template.xlsx"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return

    try:
        # Initialize Report Generator
        report_file = generate_report_filename(input_file)
        report = ReportGenerator(report_file)
        
        # 1. Read Input
        print("\n[1] Reading Input Parameters...")
        reader = InputReader(input_file)
        params = reader.get_design_parameters()
        shell_courses_input = reader.get_shell_courses()
        
        print("    Input Read Successfully.")
        print(f"    D={params['D']}m, H={params['H']}m, SG={params['G']}")
        
        # Prepare Ch_2 Design Data
        report.add_data("Ch_2_DesignData", {
            'Diameter (D, m)': params['D'],
            'Height (H, m)': params['H'], 
            'Design Level (HD, m)': params.get('HD', params['H']),
            'Test Level (HT, m)': params.get('HT', params['H']),
            'Specific Gravity (G)': params['G'],
            'Shell CA (mm)': params['CA'],
            'Roof CA (mm)': params.get('CA_roof', 0.0),
            'Bottom CA (mm)': params.get('CA_bottom', 0.0),
            'Roof Type': params.get('Roof_Type', 'Supported Cone Roof'),
            'Wind Velocity (m/s)': params.get('Wind_Velocity', 0),
            'Site Class': params.get('Site_Class', 'D')
        })

        # 2. Shell Design
        print("\n[2] Running Shell Design...")
        shell_design = ShellDesign(
            diameter=params['D'],
            height=params['H'],
            design_liquid_level=params.get('HD', params['H']),
            test_liquid_level=params.get('HT', params['H']),
            specific_gravity=params['G'],
            corrosion_allowance=params['CA'],
            p_design=params['P_design'],
            p_test=params['P_test'],
            courses_input=shell_courses_input
        )
        shell_design.run_design()
        W_shell_kg, W_shell_N = shell_design.calculate_shell_weight()
        
        # Prepare Ch_3 Shell Data
        # Add summary row first? No, table is better.
        report.add_table("Ch_3_Shell_Design", shell_design.shell_courses)
        
        # 3. Roof Design
        print("\n[3] Running Roof Design...")
        roof_design = RoofDesign(
            diameter=params['D'],
            roof_type=params.get('Roof_Type', 'Supported Cone Roof'),
            slope=params.get('Roof_Slope', 0.0625),
            corrosion_allowance=params.get('CA_roof', 0.0),
            material=params.get('Roof_Material', 'Unknown'),
            thickness_used=params.get('Roof_Thickness', 0.0)
        )
        roof_design.run_design()
        W_roof_kg, W_roof_N = roof_design.calculate_roof_weight()
        
        # 4. Liquid Weight
        print("\n[4] Calculating Liquid Weight...")
        radius = params['D'] / 2.0
        HD = params.get('HD', params['H'])
        vol_liquid = math.pi * (radius ** 2) * HD
        rho_water = 1000.0 # kg/m3
        W_liquid_kg = vol_liquid * params['G'] * rho_water
        
        # Prepare Ch_4 Roof & Bottom (and Weights)
        ch4_data = {
            'Roof Material': roof_design.material,
            'Roof Thickness Used (mm)': roof_design.t_used,
            'Roof Plate Weight (kg)': roof_design.results.get('Weight', {}).get('Plate Weight (kg)', 0),
            'Roof Structure Weight (kg)': roof_design.results.get('Weight', {}).get('Structure Weight (kg)', 0),
            'Total Roof Weight (kg)': W_roof_kg,
            'Shell Weight (kg)': W_shell_kg,
            'Liquid Volume (m3)': vol_liquid,
            'Liquid Weight (kg)': W_liquid_kg
        }
        report.add_data("Ch_4_Roof_Bottom_Weight", ch4_data)

        # 5. Wind Loads
        print("\n[5] Calculating Wind Loads...")
        wind_load = WindLoad(params)
        P_wind = wind_load.calculate_pressure()
        M_wind = wind_load.calculate_overturning_moment()
        
        # 6. Seismic Loads
        print("\n[6] Calculating Seismic Loads...")
        seismic_load = SeismicLoad(params)
        seismic_results = seismic_load.calculate_loads(W_shell_kg, W_roof_kg, W_liquid_kg)
        
        # Prepare Ch_5 Loads
        ch5_data = {
            'Design Wind Pressure (kPa)': P_wind,
            'Wind Overturning Moment (kNm)': M_wind,
            'Seismic Impulsive Weight Wi (kg)': seismic_results['Wi_kg'],
            'Seismic Convective Weight Wc (kg)': seismic_results['Wc_kg'],
            'Seismic Base Shear V (kN)': seismic_results['Base_Shear_kN'],
            'Seismic Overturning Moment M (kNm)': seismic_results['Overturning_Moment_kNm']
        }
        report.add_data("Ch_5_Loads", ch5_data)

        # 7. Internal Pressure & Frangibility (Appendix F)
        print("\n[7] Checking Internal Pressure & Frangibility...")
        w_roof_total_kN = W_roof_N / 1000.0
        w_shell_total_kN = W_shell_N / 1000.0
        
        # Convert P_design from mmH2O to kPa (1 mmH2O = 0.00980665 kPa)
        p_design_kPa = (params.get('P_design', 0) * 9.80665) / 1000.0
        
        app_f = AppendixF(
            diameter=params['D'],
            roof_weight=w_roof_total_kN,
            shell_weight=w_shell_total_kN,
            design_pressure=p_design_kPa
        )
        app_f.run_check()
        
        frangible = FrangibleCheck(
            diameter=params['D'],
            slope=params.get('Roof_Slope', 0.0625),
            roof_weight=w_roof_total_kN
        )
        frangible.run_check()
        
        report.add_data("Ch_6_Pressure_Frangibility", {
            'Design Pressure (kPa)': f"{p_design_kPa:.4f}",
            'Gravity Resist Pressure (kPa)': f"{app_f.results.get('Gravity Resist Pressure (kPa)', 0):.4f}",
            'Status': app_f.results.get('Status', 'N/A'),
            'Action': app_f.results.get('Action', 'N/A'),
            'Frangible Slope Check': frangible.results.get('Slope Check', 'N/A'),
            'Frangible Joint Area': frangible.results.get('Assumed Joint Area (A)', 'N/A')
        })
        
        # 8. Anchor Design
        print("\n[8] Designing Anchor Bolts...")
        # Wind Uplift: U = 4 * M_wind / D
        M_wind_kN = M_wind
        U_wind = (4 * M_wind_kN) / params['D']
        
        # Seismic Uplift: U = 4 * M_seismic / D
        M_seismic_kN = seismic_results['Overturning_Moment_kNm']
        U_seismic = (4 * M_seismic_kN) / params['D']
        
        anchor_design = AnchorBoltDesign(
            diameter=params['D'],
            design_pressure=p_design_kPa,
            uplift_load_wind=U_wind,
            uplift_load_seismic=U_seismic,
            shell_weight=w_shell_total_kN,
            roof_weight=w_roof_total_kN,
            vertical_acceleration_Av=seismic_results.get('Av', 0.0)
        )
        anchor_design.run_design()
        
        
        report.add_data("Ch_7_Anchor_Design", anchor_design.results)
        
        # 9. Summary Sheet
        print("\n[9] Generating Summary Sheet...")
        summary_data = {
            'Project': 'API 650 Tank Design',
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Input File': os.path.basename(input_file),
            'Diameter (D)': f"{params['D']} m",
            'Height (H)': f"{params['H']} m",
            'Design Pressure': f"{p_design_kPa:.4f} kPa",
            'Wind Velocity': f"{params.get('Wind_Velocity', 0)} m/s",
            'Seismic Site Class': params.get('Site_Class', 'D'),
            'Internal Pressure Check': app_f.results.get('Status', 'N/A'),
            'Frangible Roof': frangible.results.get('Slope Check', 'N/A'),
            'Anchor Bolt Design Status': anchor_design.results.get('Status', 'N/A'),
            'Net Uplift Force': f"{anchor_design.results.get('Net Uplift Force (kN)', 0):.2f} kN",
            'Required Anchors': f"{anchor_design.results.get('Number of Bolts', 0)} x M{anchor_design.results.get('Bolt Diameter (mm)', 0)}" if anchor_design.results.get('Number of Bolts', 0) > 0 else "None"
        }
        report.add_data("Ch_1_Summary", summary_data)
        
        # Save Report
        report.save()
        
        print("\n============================================================")
        print("Calculation Complete.")
        print(f"Report Saved to: {report_file}")
        print("============================================================")

    except Exception as e:
        print(f"Error in Main Execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
