from Shell_Design import ShellDesign

def test_1ft():
    print("--- Test 1: Small Tank (D=30m) - Auto Selection ---")
    # Mock courses
    courses = [{'Course': '1', 'Material': 'A 283 C', 'Width': 2.4, 'Thickness_Used': 10}] * 5
    
    tank_small = ShellDesign(
        diameter=30.0,
        height=12.0,
        design_liquid_level=12.0,
        test_liquid_level=12.0,
        specific_gravity=1.0,
        corrosion_allowance=1.5,
        p_design=0,
        p_test=0,
        courses_input=courses
    )
    tank_small.run_design(method='auto')
    
    print("\n--- Test 2: Large Tank (D=78m) - Forced 1-Foot Method ---")
    # Using same inputs as main project but forcing 1ft
    courses_large = [{'Course': '1', 'Material': 'A 573 70', 'Width': 2.95, 'Thickness_Used': 32}] * 6
    
    tank_large = ShellDesign(
        diameter=78.0,
        height=17.6,
        design_liquid_level=17.6,
        test_liquid_level=17.6,
        specific_gravity=0.897,
        corrosion_allowance=1.5,
        p_design=76.5,
        p_test=76.5,
        courses_input=courses_large
    )
    tank_large.run_design(method='1ft')

if __name__ == "__main__":
    test_1ft()
