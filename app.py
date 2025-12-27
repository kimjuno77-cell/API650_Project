import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import math
from io import BytesIO

from HTMLReportGenerator import HTMLReportGenerator
from Shell_Design import ShellDesign
from Roof_Design import RoofDesign
import Loads
import importlib
importlib.reload(Loads)
from Loads import WindLoad, SeismicLoad, calculate_seismic_design_params, KDSSeismicLoad
from Venting_Design import VentingDesign
from Wind_Girder_Design import WindGirderDesign
from Nozzle_Design import NozzleDesign
from Visualization import generate_shell_svg, generate_nozzle_orientation_svg, generate_wind_moment_svg, generate_roof_detail_svg
from Anchor_Chair_Design import AnchorChairDesign
from Annex_F_Design import AnnexFDesign
import Structure_Design
import importlib
importlib.reload(Structure_Design)
from Structure_Design import StructureDesign 
from EFRT_Design import EFRTDesign 
from Anchor_Design import AnchorBoltDesign
from Report_v2026 import ReportGenerator2026
from Appendix_F import AppendixF, FrangibleCheck
from Materials import CARBON_STEEL_MATERIALS, STAINLESS_STEEL_MATERIALS
from Bottom_Design import BottomDesign

# Page Configuration
st.set_page_config(page_title="API 650 Tank Design", page_icon="🛢️", layout="wide")

# --- Helper Functions for State Management ---
def save_project_to_json():
    """
    Serializes current session state inputs to JSON.
    returns: JSON string
    """
    # Keys to save
    keys_to_save = [
        "project_name", "designer_name", "shell_method_ui", 
        "ID_input", "H", "liquid_name", "G", "HD", "min_level",
        "design_temp", "mdmt", "joint_efficiency",
        "roof_type", "roof_slope", "roof_material", "dome_radius_ui",
        "struct_mat_yield", "top_angle", "detail_type",
        "efrt_b_pontoon", "efrt_h_outer", "efrt_h_inner", "efrt_gap_rim",
        "efrt_t_deck", "efrt_t_rim", "efrt_t_pontoon", "efrt_n_pontoons",
        "efrt_rafter_size", "efrt_leg_size", "efrt_leg_od", "efrt_leg_thk",
        "pump_in", "pump_out", "flash_point_opt", "insulation_opt",
        "nozzle_schedule_data",
        "V_wind", "snow_load", "live_load", "dead_load_add",
        "sug", "seismic_method", "site_class", "Ss", "S1", "SDS", "SD1", "Sp", "TL",
        "use_kds", 
        "kds_v0", "kds_terrain", "kds_risk_wind", "kds_iw_input",
        "kds_zone_input", "kds_s_input", "kds_soil", "kds_risk_seismic", "kds_ie_input",
        "shell_courses_data", "std_plate_width",
        "mat_bottom", "use_annular", "ann_width", "ann_thk", "P_external"
    ]
    
    data = {}
    for k in keys_to_save:
        if k in st.session_state:
            data[k] = st.session_state[k]
            
    return json.dumps(data, indent=4)

def load_project_from_json(uploaded_file):
    """
    Updates session state from uploaded JSON file.
    """
    try:
        uploaded_file.seek(0) # Ensure reading from start
        data = json.load(uploaded_file)
        
        # Robust Update
        for k, v in data.items():
            st.session_state[k] = v
            
        st.success(f"Project '{uploaded_file.name}' Loaded! ({len(data)} items updated)")
    except Exception as e:
        st.error(f"Error loading file: {e}")

# --- Authentication & State Management ---
from AuthManager import AuthManager

# Hide Menu and Footer for Security (Source Protection)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize Auth Manager
if 'auth_manager' not in st.session_state:
    st.session_state['auth_manager'] = AuthManager()

def login_screen():
    st.header("🔐 Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        success, msg, role = st.session_state['auth_manager'].check_login(username, password)
        if success:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['role'] = role
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None
    # Callback automatically triggers rerun

# --- Main App Logic ---

# Check Login State
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.title("🛢️ API 650 Tank Design Calculator")
    login_screen()
    st.info("Log in to access the design tool.")
    st.stop() # Stop execution if not logged in

# --- Authenticated App ---
st.sidebar.button("Logout", on_click=logout)

# Show User Info
user_role = st.session_state.get('role', 'user')
username = st.session_state.get('username', 'Unknown')
st.sidebar.info(f"Logged in as: **{username}** ({user_role})")

# Admin Panel (Only for Admin)
if user_role == 'admin':
    with st.sidebar.expander("🔒 Admin Panel"):
        st.write("### User Management")
        am = st.session_state['auth_manager']
        all_users = am.get_all_users()
        
        selected_user = st.selectbox("Select User", list(all_users.keys()))
        
        if selected_user:
            u_info = all_users[selected_user]
            st.caption(f"Role: {u_info['role']} | Expires: {u_info['expires_at']}")
            
            # Renew
            if st.button("Renew 30 Days"):
                am.renew_user(selected_user, 30)
                st.success(f" renewed to {am.users[selected_user]['expires_at']}")
            
            # Password Reset
            new_pass = st.text_input("New Password", type="password", key="new_pass_admin")
            if st.button("Reset Password"):
                if len(new_pass) > 4:
                    am.update_password(selected_user, new_pass)
                    st.success("Password Updated")
                else:
                    st.warning("Password too short")
        
        st.write("---")
        st.write("### Create User")
        new_username = st.text_input("Username", key="create_user_name")
        new_user_pass = st.text_input("Password", type="password", key="create_user_pass")
        new_user_role = st.selectbox("Role", ["user", "admin"], key="create_user_role")
        
        if st.button("Create Account"):
            if len(new_username) > 0 and len(new_user_pass) > 4:
                if new_username in all_users:
                    st.error("User already exists")
                else:
                    am.create_user(new_username, new_user_pass, role=new_user_role)
                    st.success(f"User {new_username} created!")
                    st.rerun()
            else:
                st.warning("Invalid Input")

st.title("🛢️ API 650 Tank Design Calculator (13th Ed)")
st.markdown("---")

# Prepare Material Options Globally
all_materials = list(CARBON_STEEL_MATERIALS.keys()) + list(STAINLESS_STEEL_MATERIALS.keys())

# Sidebar for Global Project Settings
with st.sidebar:
    st.header("Project Settings")
    
    # Save/Load Section
    st.subheader("📁 Project Files")
    
    # Load
    uploaded_file = st.file_uploader("Load Project (JSON)", type=["json"])
    if uploaded_file is not None:
        if "last_loaded" not in st.session_state or st.session_state["last_loaded"] != uploaded_file.name:
            load_project_from_json(uploaded_file)
            st.session_state["last_loaded"] = uploaded_file.name
            st.rerun()

    # Save
    project_name = st.text_input("Project Name", "New Tank Project", key="project_name")
    designer_name = st.text_input("Designer", "Engineer", key="designer_name")
    curr_date = datetime.now().strftime("%Y-%m-%d")
    st.write(f"Date: {curr_date}")
    
    # Download Button (Always available)
    json_str = save_project_to_json()
    st.download_button(
        label="💾 Save Project (JSON)",
        data=json_str,
        file_name=f"{project_name.replace(' ','_')}_data.json",
        mime="application/json"
    )
        
    st.header("Design Settings")
    shell_method_ui = st.selectbox("Shell Design Method", 
                                ["Auto", "1-Foot Method", "Variable Design Point (VDM)", "Annex A (Small Tank)"],
                                key="shell_method_ui")
    
    method_map = {
        "Auto": "auto", 
        "1-Foot Method": "1ft", 
        "Variable Design Point (VDM)": "vdm", 
        "Annex A (Small Tank)": "annex_a"
    }
    shell_method = method_map[shell_method_ui]

    # Tabs for Workflow
tab1, tab2, tab3, tab4 = st.tabs(["1. Design Input", "2. Load Conditions", "3. Calculation Results", "4. Report Download"])

# --- Tab 1: Design Input ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Geometry & Operation")
        ID_input = st.number_input("Inside Diameter (ID) [m]", value=31.0, step=0.1, key="ID_input")
        D = ID_input # Approximation for initial thickness calculation (Effect of t on D is negligible for design)
        H = st.number_input("Tank Height (H) [m]", value=20.0, step=0.1, key="H")
        liquid_name = st.text_input("Liquid Name", "Water / Crude Oil", key="liquid_name")
        G = st.number_input("Specific Gravity (G) of Contents", value=0.664, step=0.001, format="%.3f", key="G")
        max_level = st.number_input("Max Liquid Level [m]", value=19.0, step=0.1, key="HD") # Overrides default HD
        if max_level > H:
            st.warning(f"⚠️ Max Liquid Level ({max_level} m) exceeds Tank Height ({H} m). Please check.")
        min_level = st.number_input("Min Liquid Level [m]", value=1.2, step=0.1, key="min_level")
        
        st.subheader("Temperature & Efficiency")
        design_temp = st.number_input("Design Temperature [°C]", value=65.0, step=1.0, key="design_temp")
        mdmt = st.number_input("MDMT [°C]", value=-18.0, step=1.0, key="mdmt")
        joint_efficiency = st.number_input("Tank Joint Efficiency (E)", value=1.0, min_value=0.5, max_value=1.0, step=0.05, key="joint_efficiency")
        st.subheader("Roof Configuration")
        roof_type = st.selectbox("Roof Type", ["Supported Cone Roof", "Self-Supported Cone Roof", "Self-Supported Dome Roof", "Self-Supported Umbrella Roof", "External Floating Roof"], key="roof_type")
        
        efrt_params_ui = {}
        if roof_type == "External Floating Roof":
            st.info("API 650 Annex C: External Floating Roof Design")
            with st.expander("EFRT Configuration", expanded=True):
                # Pontoon Geometry
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    efrt_params_ui['B_pontoon'] = st.number_input("Pontoon Width [m]", value=1.7, step=0.1, key="efrt_b_pontoon")
                    efrt_params_ui['H_outer'] = st.number_input("Outer Rim Height [mm]", value=800.0, step=10.0, key="efrt_h_outer")
                    efrt_params_ui['H_inner'] = st.number_input("Inner Rim Height [mm]", value=650.0, step=10.0, key="efrt_h_inner")
                    efrt_params_ui['Gap_Rim'] = st.number_input("Rim Gap [mm]", value=200.0, step=10.0, key="efrt_gap_rim")
                with col_e2:
                    efrt_params_ui['T_Deck'] = st.number_input("Deck Thickness [mm]", value=5.0, step=0.5, key="efrt_t_deck") # Default 5 (Min 4.8)
                    efrt_params_ui['T_Rim'] = st.number_input("Rim Thickness [mm]", value=6.0, step=0.5, key="efrt_t_rim")
                    efrt_params_ui['T_Pontoon'] = st.number_input("Pontoon Plate Thk [mm]", value=6.0, step=0.5, key="efrt_t_pontoon")
                    efrt_params_ui['N_Pontoons'] = st.number_input("Number of Pontoons", value=16, step=2, key="efrt_n_pontoons")

                st.markdown("---")
                # Structural members
                col_e3, col_e4 = st.columns(2)
                with col_e3:
                    efrt_params_ui['Rafter_Size'] = st.text_input("Rafter Size (e.g. L 75 x 75 x 6)", value="L 75 x 75 x 6", key="efrt_rafter_size")
                with col_e4:
                    efrt_params_ui['Leg_Size'] = st.text_input("Leg Size (Pipe OD x Thk)", value="88.9 x 7.62", key="efrt_leg_size")
                    efrt_params_ui['Leg_OD'] = 88.9 # Default for now, parsing text is harder in simple UI
                    efrt_params_ui['Leg_Thk'] = 7.62
                    # Advanced: Parse string or add separate inputs? 
                    # Let's add separate inputs for Leg OD/Thk to be safe for calculation
                    efrt_leg_spec = st.columns(2)
                    efrt_params_ui['Leg_OD'] = efrt_leg_spec[0].number_input("Leg OD [mm]", value=88.9, key="efrt_leg_od")
                    efrt_params_ui['Leg_Thk'] = efrt_leg_spec[1].number_input("Leg Thk [mm]", value=7.62, key="efrt_leg_thk")
                    
        
        dome_radius_input = 0.0
        if 'Dome' in roof_type or 'Umbrella' in roof_type:
            st.info(f"API 650 5.10.6: Radius of curvature range: {0.8*D:.2f}m - {1.2*D:.2f}m")
            dome_radius_input = st.number_input("Dome/Umbrella Radius (m)", value=D, min_value=0.8*D, max_value=1.2*D, step=0.1, key="dome_radius_ui")
        
        roof_material = st.selectbox("Roof Material", all_materials, index=2, key="roof_material") # Default A 36
        roof_slope = st.number_input("Roof Slope (Rise/Run) - Not used for Dome", value=0.0625, format="%.4f", step=0.01, key="roof_slope")
        
        # Structure Design Inputs (Conditional)
        struct_yield = 235.0
        if "Supported" in roof_type:
            st.markdown("---")
            st.write("### Structure Design Inputs")
            
            # Yield Strength Mapping
            yield_map = {
                235: "SS400 / S235 (235 MPa)",
                250: "ASTM A36 (250 MPa)",
                345: "ASTM A572-50 / S355 (345 MPa)"
            }
            
            # Helper to handle custom values if loaded from JSON
            def format_yield(val):
                return yield_map.get(val, f"Custom ({val} MPa)")

            struct_mat_Fy = st.selectbox(
                "Structure Material Yield (MPa)", 
                options=[235, 250, 345], 
                format_func=format_yield,
                index=0, 
                key="struct_mat_yield"
            )
            struct_yield = float(struct_mat_Fy)
        
        # Top Angle & Detail (Annex F / 5.10.2.6)
        angle_options = ['L50x50x4', 'L50x50x5', 'L50x50x6', 'L65x65x5', 'L65x65x6', 'L65x65x8', 
                         'L75x75x6', 'L75x75x9', 'L100x100x6', 'L100x100x8', 'L100x100x10']
        top_angle_size = st.selectbox("Top Angle Size", angle_options, index=6, key="top_angle") # Default L75x75x6
        
        detail_options = ['Detail a (Top Angle)', 'Detail c (Butt Weld)', 'Detail d (Lap)', 'Detail e (Knuckle)']
        detail_type = st.selectbox("Roof-to-Shell Detail (Fig F.2)", detail_options, index=0, key="detail_type")
        
        st.subheader("Applicable Annexes (API 650)")
        # Auto-detected (Logic to be run during calc, but displayed here)
        # Purchaser Options
        purchaser_annexes = st.multiselect(
            "Purchaser Specified Annexes",
            ['Annex A (Small Tanks)', 'Annex J (Shop-Assembled)', 
             'Annex U (Ultrasonic)', 'Annex W (Commercial Cert)', 'Annex Y (Proof Testing)'],
            default=[],
            key="purchaser_annexes"
        )
        
        P_external_kPa = st.number_input("Design External Pressure (Vacuum) [kPa]", value=0.0, step=0.1, key="P_external")
        
    with col2:
        st.subheader("Plate & Corrosion")
        CA = st.number_input("Shell Corrosion Allowance [mm]", value=1.5, step=0.5, key="CA")
        CA_roof = st.number_input("Roof Corrosion Allowance [mm]", value=0.0, step=0.5, key="CA_roof")
        CA_bottom = st.number_input("Bottom Corrosion Allowance [mm]", value=0.0, step=0.5, key="CA_bottom")

        st.subheader("Pressures")
        P_design_mm = st.number_input("Design Pressure [mmH2O]", value=250.0, step=10.0, key="P_design_mm")
        P_test_mm = st.number_input("Test Pressure [mmH2O]", value=300.0, step=10.0, key="P_test_mm")
        # Hydrotest SG is typically 1.0
        
        st.subheader("Bottom Plate")
        mat_bottom = st.selectbox("Bottom Material", all_materials, index=0, key="mat_bottom")
        use_annular = st.checkbox("Use Annular Plate?", value=False, key="use_annular")
        
        # Placeholder for dynamic warning (updated after calc)
        ann_warning_placeholder = st.empty()

        ann_width_input = 0.0
        ann_thk_input = 0.0
        
        if use_annular:
            st.caption("Annular Plate Parameters")
            col_ann1, col_ann2 = st.columns(2)
            ann_width_input = col_ann1.number_input("Annular Width [mm]", value=600.0, step=10.0, key="ann_width")
            ann_thk_input = col_ann2.number_input("Annular Thickness [mm]", value=8.0, step=0.5, key="ann_thk")
        
    # --- Nozzle Schedule (Tab 1 Main) ---
    with st.expander("Appurtenances & Nozzle Schedule", expanded=False):
        st.info("Define Shell/Roof Nozzles. Dimensions are indicative.")
        
        # Default Data with Extended Fields
        default_nozzles = [
            {"Mark": "N1", "Size (NPS)": "24", "Service": "Shell Manway", "Elevation (m)": 0.9, "Orientation (deg)": 0, "Pipe Thk (mm)": 12.7, "Repad": True, "Remarks": "Standard"},
            {"Mark": "N2", "Size (NPS)": "10", "Service": "Inlet", "Elevation (m)": 1.5, "Orientation (deg)": 90, "Pipe Thk (mm)": 9.27, "Repad": True, "Remarks": ""},
            {"Mark": "N3", "Size (NPS)": "10", "Service": "Outlet", "Elevation (m)": 0.5, "Orientation (deg)": 270, "Pipe Thk (mm)": 9.27, "Repad": True, "Remarks": ""},
            {"Mark": "N4", "Size (NPS)": "4", "Service": "Drain", "Elevation (m)": 0.2, "Orientation (deg)": 180, "Pipe Thk (mm)": 6.02, "Repad": False, "Remarks": ""},
            {"Mark": "R1", "Size (NPS)": "24", "Service": "Roof Manway", "Elevation (m)": 20.0, "Orientation (deg)": 45, "Pipe Thk (mm)": 9.5, "Repad": False, "Remarks": ""},
            {"Mark": "V1", "Size (NPS)": "8", "Service": "Gooseneck Vent", "Elevation (m)": 20.0, "Orientation (deg)": 225, "Pipe Thk (mm)": 8.18, "Repad": False, "Remarks": ""}
        ]
        
        # Persistence logic similar to Shell Courses
        if "nozzle_schedule_data" in st.session_state and st.session_state["nozzle_schedule_data"]:
             # Check if old format, update if needed?
             # Pandas handles extra columns gracefully (fill NaN).
             df_nozzles_in = pd.DataFrame(st.session_state["nozzle_schedule_data"])
        else:
            df_nozzles_in = pd.DataFrame(default_nozzles)
        
        edited_nozzles_df = st.data_editor(
            df_nozzles_in,
            key="nozzles_editor",
            num_rows="dynamic",
            column_config={
                 "Size (NPS)": st.column_config.SelectboxColumn(
                    "Size (NPS)",
                    options=["2", "3", "4", "6", "8", "10", "12", "14", "16", "18", "20", "24", "30", "36"],
                    required=True
                ),
                "Elevation (m)": st.column_config.NumberColumn(
                    "Elevation (m)", step=0.1
                ),
                "Orientation (deg)": st.column_config.NumberColumn(
                    "Orientation (deg)", min_value=0, max_value=360, step=5
                ),
                "Pipe Thk (mm)": st.column_config.NumberColumn(
                    "Pipe Thk (mm)", min_value=1.0, step=0.1
                ),
                "Repad": st.column_config.CheckboxColumn(
                    "Repad", default=True
                )
            }
        )
        st.session_state["nozzle_schedule_data"] = edited_nozzles_df.to_dict('records')
        
# Initialize SVG variables
shell_svg = ""
nozzle_svg = ""
wind_moment_svg = ""
roof_detail_svg = ""
seismic_graph_b64 = ""
        
# --- Tab 2: Loads ---
with tab2:
    col_wind, col_seismic = st.columns(2)
    
    with col_wind:
        st.subheader("Wind & Roof Loads")
        V_wind = st.number_input("Wind Speed (3-sec gust) [m/s]", value=65.0, step=1.0, key="V_wind") # 234 kph = 65 m/s
        # Additional Loads
        snow_load = st.number_input("Ground Snow Load [kPa]", value=0.0, step=0.1, key="snow_load")
        live_load = st.number_input("Roof Live Load [kPa]", value=1.2, step=0.1, key="live_load")
        dead_load_add = st.number_input("Add. Roof Dead Load [kPa]", value=0.0, step=0.1, key="dead_load_add")
        
    with col_seismic:
        st.subheader("Seismic Loads (API 650 Annex E)")
        # Seismic Use Group & Importance Factor (Table E.5)
        sug_options = ["SUG I (Normal)", "SUG II (Essential)", "SUG III (Toxic/Explosive)"]
        sug_ui = st.selectbox("Seismic Use Group (SUG)", sug_options, index=0, key="sug")
        
        # Map SUG to I
        i_map = {"SUG I (Normal)": 1.0, "SUG II (Essential)": 1.25, "SUG III (Toxic/Explosive)": 1.5}
        I_seismic = i_map[sug_ui]
        st.info(f"Importance Factor (I): {I_seismic}")
        
        # Input Method
        seismic_method = st.radio("Seismic Input Method", 
                                  ["Mapped Acceleration (Ss, S1)", 
                                   "Design Acceleration (SDS, SD1)", 
                                   "Single Parameter (Sp)"], 
                                  key="seismic_method")
        
        SDS = 0.0
        SD1 = 0.0
        S1 = 0.0 # Initialize to avoid NameError
        site_class = 'D'
        
        if "Mapped" in seismic_method:
            site_class = st.selectbox("Site Class (Table E.1/E.2)", ['A', 'B', 'C', 'D', 'E'], index=3, key="site_class")
            Ss = st.number_input("Ss (Short Period Mapped) [g]", value=0.0, step=0.01, key="Ss")
            S1 = st.number_input("S1 (1-Sec Period Mapped) [g]", value=0.0, step=0.01, key="S1")
            if Ss > 0:
                SDS, SD1 = calculate_seismic_design_params('MAPPED', Ss, S1, site_class)
                st.write(f"Calculated: SDS={SDS:.3f} g, SD1={SD1:.3f} g")
        
        elif "Design" in seismic_method:
            SDS = st.number_input("SDS (Design Short Period) [g]", value=0.0, step=0.01, key="SDS")
            SD1 = st.number_input("SD1 (Design 1-Sec Period) [g]", value=0.0, step=0.01, key="SD1")
            # Calc logic just passes them
            
        elif "Single" in seismic_method:
            Sp = st.number_input("Sp (Design Parameter) [g]", value=0.0, step=0.01, key="Sp")
            if Sp > 0:
                SDS, SD1 = calculate_seismic_design_params('Sp', Sp)
                st.write(f"Assumed: SDS={SDS:.3f} g (Sp), SD1={SD1:.3f} g")

        T_L = st.number_input("Long-Period Transition Period (TL) [s]", value=4.0, step=1.0, key="TL")
        seismic_group = sug_ui # For params

# --- KDS Standards Input (New) ---
# --- KDS Standards Input (New) ---
with st.expander("🇰🇷 KDS Standard Options (Advanced)", expanded=False):
    use_kds = st.checkbox("Apply KDS 41 12/17 Standards for Comparison", value=False, key="use_kds")
    
    # Initialize defaults
    kds_V0 = 26.0
    kds_Terrain = 'B'
    kds_Iw = 1.0
    kds_Zone = 'I'
    kds_Soil = 'SD'
    kds_Risk = 'II'
    kds_S = 0.22
    kds_SDS = 0.50
    kds_IE_seis = 1.2
    
    if use_kds:
        c_kds1, c_kds2 = st.columns(2)
        with c_kds1:
            st.markdown("#### KDS 41 12 00 (Wind)")
            kds_V0 = st.number_input("Basic Wind Speed V0 (m/s)", value=26.0, step=1.0, help="Seoul: 26, Busan: 40, Jeju: 44", key="kds_v0")
            kds_Terrain = st.selectbox("Terrain Category", ['A', 'B', 'C', 'D'], index=1, help="A: City, B: Urban, C: Open, D: Sea/Coastal", key="kds_terrain")
            
            # Risk Category for Importance Factor
            kds_Risk_Wind = st.selectbox("Risk Category (Wind)", ["I (Low)", "II (Normal)", "III (Substantial)", "IV (Critical)"], index=1, key="kds_risk_wind")
            
            # Iw Lookup Table (KDS 41 12 00 Table 2.5-1)
            iw_map = {"I (Low)": 0.87, "II (Normal)": 1.0, "III (Substantial)": 1.15, "IV (Critical)": 1.15} # Approx KDS
            kds_Iw = st.number_input("Wind Importance Factor (Iw)", value=iw_map.get(kds_Risk_Wind, 1.0), step=0.01, key="kds_iw_input")
            
        with c_kds2:
            st.markdown("#### KDS 41 17 00 (Seismic)")
            # S value (Effective Ground Acceleration)
            kds_Zone_Input = st.selectbox("Seismic Zone", ['I (Central/South)', 'II (North/Jeju)'], index=0, key="kds_zone_input")
            kds_Zone = kds_Zone_Input.split(' ')[0]
            
            s_default = 0.22 if 'I' in kds_Zone else 0.14
            kds_S = st.number_input("Effective Ground Accel (S) [g]", value=s_default, step=0.01, key="kds_s_input")
            
            kds_Soil = st.selectbox("Site Class (Soil)", ['SA (Hard Rock)', 'SB (Rock)', 'SC (Dense Soil)', 'SD (Stiff Soil)', 'SE (Soft Soil)'], index=3, key="kds_soil")
            site_short = kds_Soil.split(' ')[0]
            
            # Risk Category for Seismic Importance
            kds_Risk_Seis = st.selectbox("Risk Category (Seismic)", ["I (Low)", "II (Normal)", "Special (1st)", "Special (Limited)"], index=1, key="kds_risk_seismic")
            ie_map = {"I (Low)": 1.0, "II (Normal)": 1.2, "Special (1st)": 1.5, "Special (Limited)": 1.5}
            kds_IE_seis = st.number_input("Seismic Importance (Ie)", value=ie_map.get(kds_Risk_Seis, 1.2), step=0.1, key="kds_ie_input")
            
            # Simple SDS Calc for Display
            # Fa lookup (KDS Table 4.1-1, simplified for S=0.22/0.14)
            # S < 0.25: Fa varies SA=0.8, SB=1.0, SC=1.2, SD=1.6
            # Use logic or placeholder. 
            # Implemented simplified lookup for display:
            fa_table = {'SA': 0.8, 'SB': 1.0, 'SC': 1.2, 'SD': 1.6, 'SE': 2.5} # For S < 0.25 approx
            fa = fa_table.get(site_short, 1.6)
            sds_calc = kds_S * 2.5 * fa * (2/3)
            st.caption(f"Calculated SDS ≈ {sds_calc:.3f} g (Based on Fa={fa})")
        
    with st.expander("API 2000 Venting Parameters", expanded=True):
        st.info("Inputs for Normal and Emergency Venting Calculation (7th Ed).")
        c1, c2 = st.columns(2)
        with c1:
            pump_in = st.number_input("Max Pump-In Rate (m3/h)", value=100.0, step=10.0, key="pump_in")
            pump_out = st.number_input("Max Pump-Out Rate (m3/h)", value=100.0, step=10.0, key="pump_out")
        with c2:
            flash_point_opt = st.selectbox("Liquid Flash Point", ["High (>= 40°C)", "Low (< 40°C)"], key="flash_point_opt")
            insulation_opt = st.selectbox("Insulation Factor (F)", [1.0, 0.5, 0.3], key="insulation_opt")
            
        flash_point_cat = 'High' if '>=' in flash_point_opt else 'Low'
        
    with st.expander("Annex F & Roof Detail Options", expanded=False):
        detail_type = st.selectbox("Roof-to-Shell Detail (Fig F.2)", 
            ["Angle (Detail a)", "Butt Weld (Generic)", "Angle w/ Plate (Detail c)", "Internal Angle (Detail d)"], index=0)
        
        angle_opts = ["L50x50x4", "L50x50x5", "L50x50x6", "L65x65x5", "L65x65x6", "L65x65x8", "L75x75x6", "L75x75x9", "L100x100x8", "L100x100x10"]
        top_angle_size = st.selectbox("Top Angle Size", angle_opts, index=6)

# Run Calculation
# Prepare params dictionary similar to InputReader
params = {
    'D': D, 'H': H, 'G': G, 'CA': CA, 'CA_roof': CA_roof,
    'HD': max_level, # Use max liquid level
    'P_design': P_design_mm, 'P_test': P_test_mm,
    'Wind_Velocity': V_wind, 'Site_Class': site_class,
    'SDS': SDS, 
    'SD1': SD1, # Explicitly pass SD1
    'S1': SD1 if SD1 > 0 else S1, # Pass Design Value SD1 as S1 for Loads.py logic
    'I_seismic': I_seismic,
    'Efficiency': joint_efficiency, # New
    'Design_Temp': design_temp, 'MDMT': mdmt,
    'Snow_Load': snow_load, 'Live_Load': live_load, 'Dead_Load_Add': dead_load_add,
    'Seismic_Group': seismic_group, 'T_L': T_L,
    'Seismic_Method': seismic_method,
    'Ss': Ss if 'Ss' in locals() else 0.0,
    'S1_Input': S1 if 'S1' in locals() else 0.0,
    # Defaults
    'Kzt': 1.0, 'Kd': 0.95, 'G_wind': 0.85, 'Cf': 0.5,
    'Roof_Type': 'Supported Cone Roof', 'Roof_Slope': roof_slope,
    'Roof_Material': 'A 36', 'Roof_Thickness': 6.0,
    'S0': 0.5
}

# 1. Shell Design


# 1. Shell Design
st.subheader("Shell Thickness Details")

# Standard Plate Width Input & Auto-Calc
def reset_courses_on_width_change():
    if "shell_courses_data" in st.session_state and st.session_state["shell_courses_data"]:
        st.session_state['preserved_shell_material'] = st.session_state["shell_courses_data"][0].get('Material', 'A 283 C')
    st.session_state.pop("shell_courses_data", None)

c_sh1, c_sh2 = st.columns([2, 1])
std_width = c_sh1.number_input("Standard Plate Width (m)", value=2.438, step=0.001, key="std_plate_width", on_change=reset_courses_on_width_change)
# Button still useful for explicit reset, but input change now handles it too
if c_sh2.button("Auto-Generate Courses", help="Reset shell courses based on height and plate width"):
    # Clear existing data to force regeneration
    if "shell_courses_data" in st.session_state and st.session_state["shell_courses_data"]:
        st.session_state['preserved_shell_material'] = st.session_state["shell_courses_data"][0].get('Material', 'A 283 C')
        
    st.session_state.pop("shell_courses_data", None)
    # Store trigger to use standard width logic below
    st.session_state['force_recalc_width'] = True
    st.rerun()

# Setup initial dataframe for courses
# Use session state standard width if available, or default
calc_width = std_width
num_courses_est = math.ceil(H / calc_width) 

default_data = []
current_h_calc = 0
# Use preserved material if available, else default
default_mat = st.session_state.get('preserved_shell_material', 'A 283 C')

for i in range(num_courses_est):
    w_remain = H - current_h_calc
    width = min(calc_width, w_remain)
    # Avoid tiny top course if possible? API 650 doesn't strictly forbid, but practicality.
    if w_remain < 0.01: break # Done
    
    default_data.append({
        "Course": f"Course {i+1}",
        "Material": default_mat,
        "Width (m)": float(f"{width:.3f}"),
        "Thickness Used (mm)": 0.0,
        "Req Thickness (mm)": 0.0,
        "Rec Thickness (mm)": 0.0
    })
    current_h_calc += width

# Height Change Detection for Auto-Reset
if 'last_H' not in st.session_state:
    st.session_state['last_H'] = H
    
height_changed = False
if abs(st.session_state['last_H'] - H) > 0.001:
    st.session_state['last_H'] = H
    height_changed = True
    st.session_state.pop("shell_courses_data", None)
    st.session_state['last_loaded'] = datetime.now().strftime("%Y%m%d%H%M%S")

df_shell_input = pd.DataFrame(default_data)

# If loaded data exists (and height didn't just change), use it
# CRITICAL FIX for 2.438 vs 2.418 mismatch:
# Check if the existing data matches the current 'std_width' input.
# If the user sees 2.438 in the box, but the table has stale 2.418 data, use the box value.
if "shell_courses_data" in st.session_state and isinstance(st.session_state["shell_courses_data"], list):
     stale_data = st.session_state["shell_courses_data"]
     if len(stale_data) > 0:
         first_width = stale_data[0].get("Width (m)", 0.0)
         
         # ROBUST FIX: Check for mismatch but DO NOT discard data.
         if abs(first_width - std_width) > 0.001:
              st.warning(f"⚠️ Table width ({first_width}m) differs from Input ({std_width}m). Value preserved to avoid data loss. Click 'Auto-Generate' to reset.")
         
         # ALWAYS Load saved data (User might have custom edits)
         saved_df = pd.DataFrame(stale_data)
         # Ensure new columns exist in saved data
         if "Req Thickness (mm)" not in saved_df.columns: saved_df["Req Thickness (mm)"] = 0.0
         if "Rec Thickness (mm)" not in saved_df.columns: saved_df["Rec Thickness (mm)"] = 0.0
         df_shell_input = saved_df
     else:
         # Empty list, use default
         pass
     
# Update with Latest Calculation Results (Contextual Help)
if "latest_shell_results" in st.session_state:
    results = st.session_state["latest_shell_results"]
    # Map results to df_shell_input by index (assuming course order preserved)
    # Note: If user added/removed rows, this might mismatch. Index safe-guard needed.
    for idx, row in df_shell_input.iterrows():
        if idx < len(results):
            res = results[idx]
            df_shell_input.at[idx, "Req Thickness (mm)"] = res.get('t_req', 0.0)
            df_shell_input.at[idx, "Rec Thickness (mm)"] = res.get('t_rec', 0.0)

# Use Data Editor with dynamic key
editor_key = f"shell_courses_input_{st.session_state.get('last_loaded', 'default')}"

with st.form("shell_course_form"):
    edited_df = st.data_editor(
        df_shell_input,
        key=editor_key, # Key for persistence
        column_config={
            "Material": st.column_config.SelectboxColumn(
                "Material",
                help="Select API 650 Material",
                width="medium",
                options=all_materials,
                required=True,
            ),
            "Width (m)": st.column_config.NumberColumn(
                "Width (m)",
                min_value=0.1,
                max_value=5.0,
                step=0.001,
            ),
            "Req Thickness (mm)": st.column_config.NumberColumn(
                "Req Thickness (mm)",
                disabled=True, # Read-only
                format="%.2f"
            ),
            "Rec Thickness (mm)": st.column_config.NumberColumn(
                "Rec Thickness (mm)",
                disabled=True, # Read-only
                format="%.0f"
            ),
        },
        hide_index=True,
        num_rows="dynamic"
    )
    st.form_submit_button("일괄 적용 (Apply Updates)")

# Update the persistence key 'shell_courses_data' with serializable format
# This ensures save_project_to_json gets the latest edited data
st.session_state["shell_courses_data"] = edited_df.to_dict('records')

# Validation: Compare Total Course Height with Tank Height
total_course_h = edited_df['Width (m)'].sum()
if abs(total_course_h - H) > 0.01:
    st.warning(f"⚠️ Total Shell Course Height ({total_course_h:.3f} m) does not match Tank Height ({H} m). Please adjust course widths.")

# Convert edited DF back to list format expected by ShellDesign
courses_input = []
for index, row in edited_df.iterrows():
    courses_input.append({
        'Course': row['Course'],
        'Material': row['Material'],
        'Width': row['Width (m)'],
        'Thickness_Used': row['Thickness Used (mm)']
    })
    
shell_design = ShellDesign(
    diameter=D, 
    height=H, 
    design_liquid_level=max_level, 
    test_liquid_level=H, 
    specific_gravity=G, 
    corrosion_allowance=CA, 
    p_design=P_design_mm, 
    p_test=P_test_mm, 
    efficiency=joint_efficiency,
    courses_input=courses_input
)
shell_design.run_design(method=shell_method)
W_shell_kg, W_shell_N = shell_design.calculate_shell_weight()

# Save Results for Input Editor Feedback Loop
st.session_state['latest_shell_results'] = shell_design.shell_courses

# 2. Roof Design
efrt_design_res = None
roof_design = None
struct_data = {}
if roof_type == "External Floating Roof":
    # --- EFRT Design ---
    efrt = EFRTDesign(diameter=D, material_yield=struct_yield, specific_gravity=G)
    
    # Set Geometry (UI Inputs are in mixed units, convert to Design expectations)
    # D is meters. B_pontoon is meters in UI, convert to mm.
    # Heights are mm.
    b_pont_mm = efrt_params_ui.get('B_pontoon', 1.7) * 1000.0
    h_out_mm = efrt_params_ui.get('H_outer', 800.0)
    h_in_mm = efrt_params_ui.get('H_inner', 650.0)
    gap_mm = efrt_params_ui.get('Gap_Rim', 200.0)
    
    # Correct Method Call
    n_pontoons_val = efrt_params_ui.get('N_Pontoons', 16)
    efrt.set_pontoon_geometry(width=b_pont_mm, h_out=h_out_mm, h_in=h_in_mm, n_pontoons=n_pontoons_val)
    efrt.gap_rim = gap_mm / 1000.0
    
    # Set Thicknesses
    # Set Thicknesses
    efrt.set_thickness(
        t_rim_out=efrt_params_ui.get('T_Rim', 6.0),
        t_rim_in=efrt_params_ui.get('T_Rim', 6.0),
        t_pon_top=efrt_params_ui.get('T_Pontoon', 6.0),
        t_pon_btm=efrt_params_ui.get('T_Pontoon', 6.0),
        t_deck=efrt_params_ui.get('T_Deck', 5.0)
    )
    
    # Run Checks
    efrt.check_deck_thickness()
    efrt.calculate_buoyancy()
    
    # Rafter Check
    raf_str = efrt_params_ui.get('Rafter_Size', '')
    if raf_str:
        efrt.check_pontoon_rafter(raf_str)
        
    # Leg Check
    leg_od = efrt_params_ui.get('Leg_OD', 0.0)
    leg_thk = efrt_params_ui.get('Leg_Thk', 0.0)
    n_pont = efrt_params_ui.get('N_Pontoons', 16)
    if leg_od > 0:
        efrt.check_roof_leg(leg_od, leg_thk, length_m=2.0, num_legs=n_pont)
        
    W_roof_kg = efrt.results.get('Weight_kg', 0.0)
    W_roof_N = W_roof_kg * 9.81
    efrt_design_res = efrt

else:
    # --- Standard Cone/Dome Roof Design ---
    # Use selected type and slope
    # Use local var dome_radius_input if defined, else None? 
    dr_val = locals().get('dome_radius_input', None)
    
    roof_design = RoofDesign(D, roof_type, roof_slope, CA_roof, roof_material, 6.0, dome_radius=dr_val)
    roof_design.check_roof_plate(total_load_kPa=(live_load + snow_load + dead_load_add + 0.0)) # Approximate check
    roof_design.run_design() # Run standard design (which might repeat check)
    W_roof_kg, W_roof_N = roof_design.calculate_roof_weight()
    
    # Structure Design (If Supported)
    struct_data = {}
    if "Supported" in roof_type and "Self" not in roof_type:
        # Load Inputs
        # Dead Plate = Uses 7850 * t_used
        t_roof_m = roof_design.t_used / 1000.0
        q_plate = 7850.0 * 9.81 * t_roof_m / 1000.0 # kPa
        
        loads = {
            'Live': live_load,
            'Snow': snow_load,
            'Dead_Plate': q_plate,
            'Dead_Add': dead_load_add
        }
        
        # st.write(f"DEBUG: D passed to Struct = {D} m") # DEBUG
        struct = StructureDesign(D, loads, material_yield=struct_yield)
        struct.set_height(H)
        struct.run_design()
        struct_data = struct.results
        # st.write("DEBUG: Struct Results:", struct_data) # DEBUG
        
        # Generate Plot
        try:
             # Returns SVG string now
             svg_content = struct.generate_structure_plot()
             struct_data['Plot SVG'] = svg_content
        except Exception as e:
             st.error(f"Error generating structure plot: {e}")
             struct_data['Plot SVG'] = None
        
        # Structure Weight (Calculated)
        W_struct_real = struct_data.get('Total Struct Weight (kg)', 0.0)
        
        W_roof_kg += W_struct_real
        W_roof_N = W_roof_kg * 9.81

# Bottom Design
# Get First Course Stress & Thickness
mat_first = courses_input[0]['Material'] if courses_input else 'A 283 C'
t_shell_bot_mm = courses_input[0]['Thickness_Used'] if courses_input else 0.0 # From user input or calc
# Actually 'Thickness_Used' in courses_input is 0.0 initially if auto?
# No, shell_design.shell_courses has results.
if shell_design.shell_courses:
    t_shell_bot_mm = shell_design.shell_courses[0]['t_used']

props_first = shell_design.get_material_stress(mat_first)
Sd_first = props_first[0]

bottom_design = BottomDesign(D, CA_bottom, mat_bottom, stress_first_course=Sd_first)
bottom_design.run_design(H=H, G=G, use_annular=use_annular, t_shell_bot_mm=t_shell_bot_mm, user_width=ann_width_input, user_thk=ann_thk_input)

# 3. Loads
# Wind
wind_load = WindLoad(params)
P_wind_kPa = wind_load.calculate_pressure()
M_wind_kNm = wind_load.calculate_overturning_moment()

# KDS Wind Calculation
kds_wind_P = 0.0
kds_wind_M = 0.0
if 'use_kds' in locals() and use_kds:
    # Prepare KDS Params
    kds_params = params.copy()
    kds_params.update({
        'KDS_V0': kds_V0,
        'KDS_Terrain': kds_Terrain,
        'KDS_Iw': kds_Iw,
        'KDS_Zone': kds_Zone,
        'KDS_Soil': kds_Soil,
        'KDS_S': kds_S,
        'KDS_IE': kds_IE_seis,
        'H': H, 'D': D
    })
    kds_wind = Loads.KDSWindLoad(kds_params)
    kds_wind_P = kds_wind.calculate_pressure()
    kds_wind_M = kds_wind.calculate_moment()


# Wind Girder Design (Intermediate)
wind_girder_design = WindGirderDesign(D, H, shell_design.shell_courses, V_wind * 3.6) # Convert m/s to km/h
wind_girder_res = wind_girder_design.calculate_intermediate_girders()

# Nozzle Design (Schedule Only in Phase 2)
# Get nozzles list from session state or editor ??
# We persisted it to st.session_state["nozzle_schedule_data"]
# But also edited_nozzles_df is available in local scope if Tab 1 ran.
# Safe to use session state if available, else default.
# Note: st.date_editor updates session state automatically? No, we set it manually in Tab 1.

nozzle_list_in = st.session_state.get("nozzle_schedule_data", [])
nozzle_design = NozzleDesign(nozzle_list_in)
nozzle_design.process_nozzles()
nozzle_res = nozzle_design.check_reinforcement(shell_design.shell_courses)

# Seismic
# Need Liquid Weight
radius = D / 2.0
vol_liquid = math.pi * (radius ** 2) * H
W_liquid_kg = vol_liquid * G * 1000.0

seismic_load = SeismicLoad(params)
seismic_res = seismic_load.calculate_loads(W_shell_kg, W_roof_kg, W_liquid_kg)

# KDS Seismic Calculation
kds_seismic_res = {}
if 'use_kds' in locals() and use_kds:
    # KDS Params prepared above
    kds_seismic = Loads.KDSSeismicLoad(kds_params)
    kds_seismic_res = kds_seismic.calculate_loads(W_shell_kg, W_roof_kg, W_liquid_kg)

# --- Governing Loads Determination ---
gov_wind_P = P_wind_kPa
gov_wind_M = M_wind_kNm
gov_wind_code = "API 650 (ASCE 7)"

gov_seismic_res = seismic_res
gov_seismic_load_obj = seismic_load
gov_seismic_code = "API 650 (Annex E)"

if 'use_kds' in locals() and use_kds:
    # Wind Comparison (Pressure for Stiffeners)
    if kds_wind_P > P_wind_kPa:
        gov_wind_P = kds_wind_P
        gov_wind_code = "KDS 41"
        
    # Wind Comparison (Moment for Anchors)
    if kds_wind_M > M_wind_kNm:
        gov_wind_M = kds_wind_M
        # Code might differ for Moment, but usually consistent. 
        # Update code based on Moment if it governs stability/anchors
        if kds_wind_M > M_wind_kNm: gov_wind_code = "KDS 41" 

    # Seismic Comparison
    kds_V = kds_seismic_res.get('Base_Shear_kN', 0)
    api_V = seismic_res.get('Base_Shear_kN', 0)
    
    if kds_V > api_V:
        gov_seismic_res = kds_seismic_res
        gov_seismic_load_obj = kds_seismic
        gov_seismic_code = "KDS 41"

    # --- Integrate Seismic Annular Requirement into Bottom Design ---
    seismic_ann_status = gov_seismic_res.get('Annular_Check', 'Not Required')
    if "Required" in seismic_ann_status:
         # Update Bottom Design Result
         ann_res = bottom_design.results.get('Annular Plate', {})
         
         # If already required by Stress, just append reason
         if ann_res.get('Required?') == 'Yes':
             if "Seismic" not in ann_res.get('Required?', ''):
                 ann_res['Required?'] += " / Seismic"
         else:
             ann_res['Required?'] = "Yes (Seismic)"
             
         # If NOT Applied, Trigger Warning
         if not ann_res.get('Applied', False):
             ann_res['Warning'] = f"Annular Plate is REQUIRED by Seismic Stability ({gov_seismic_code}) but is NOT applied."
             ann_res['Status'] = "MISSING (REQUIRED)"
             
         bottom_design.results['Annular Plate'] = ann_res



# 6. Venting Design (API 2000)
# Wetted Area for Fire: Typically bottom 9m of shell (API 2000 4.3.3.2.3) or H if < 9m
# A_wetted = Pi * D * H_wetted
h_wetted_fire = min(H, 9.14) # 30ft
A_wetted_fire = math.pi * D * h_wetted_fire

# Calculate Net Capacity for Venting (and Report)
# Ensure variables valid
calc_max_level = max_level
calc_min_level = 1.2 # Default min level? Or fetch from input if available.
# Actually min_level is defined in Tab 2 UI?
# No, min_level is not in Tab 2 currently! It was hardcoded in Report Data before??
# In Step 2039 Report: Min Liq Level: 1.2 m.
# Where does it come from?
# It was in the ORIGINAL code.
# Let's assume min_level = 0 for venting conservatism or define it.
# Actually, vol_net_m3 was calculated as (max - min) * Area.
# If min_level is missing in scope, define it.

if 'min_level' not in locals(): min_level = 0.0 # Safety

effective_HD = float(calc_max_level) - float(min_level)
if effective_HD < 0: effective_HD = 0.0
vol_net_m3 = math.pi * ((D/2.0)**2) * effective_HD

venting_design = VentingDesign(
    volume_m3=vol_net_m3, 
    surface_area_m2=math.pi*(D/2)**2 + math.pi*D*H, # Rough surface area (Roof+Shell)
    wetted_area_m2=A_wetted_fire,
    pump_in_rate=pump_in,
    pump_out_rate=pump_out,
    flash_point_category=flash_point_cat,
    insulation_factor=insulation_opt
)
venting_res = venting_design.calculate_all()

# 4. Appendix F & Anchor
w_roof_kN = W_roof_N / 1000.0
w_shell_kN = W_shell_N / 1000.0
p_design_kPa = (P_design_mm * 9.80665) / 1000.0

app_f = AppendixF(D, w_roof_kN, w_shell_kN, p_design_kPa)
app_f.run_check()

M_seismic_kN = gov_seismic_res['Overturning_Moment_kNm']
U_wind = (4 * gov_wind_M) / D
U_seismic = (4 * M_seismic_kN) / D

anchor_design = AnchorBoltDesign(D, p_design_kPa, U_wind, U_seismic, w_shell_kN, w_roof_kN)
anchor_design.run_design()

# Anchor Chair Calculation
net_uplift_res = anchor_design.results.get('Net Uplift Force (kN)', 0)
num_bolts_res = anchor_design.results.get('Number of Bolts', 0)
bolt_dia_res = anchor_design.results.get('Bolt Diameter (mm)', 0)
Sy_shell = 205.0 # Basic assumption or fetch from material props

anchor_chair = AnchorChairDesign(
    net_uplift_kN=net_uplift_res,
    num_bolts=num_bolts_res,
    bolt_diameter_mm=bolt_dia_res,
    shell_t_bot_mm=t_shell_bot_mm,
    shell_yield_MPa=Sy_shell
)
# Anchor Chair
# ... (existing)
anchor_chair.run_design()

# Annex F (Top Angle)
annex_f = AnnexFDesign(
    D=D, 
    W_roof_total_kN=w_roof_kN, 
    W_shell_kN=w_shell_kN, 
    P_design_kPa=p_design_kPa, 
    roof_slope=roof_slope, 
    top_angle_size=top_angle_size, 
    detail_type=detail_type
)
annex_f.run_check()
annex_f_res = annex_f.results

# --- Validation ---
def validate_api650(D, H, G, T, shell_courses):
    warnings = []
    # 1. Dimension Checks (API 650 1.1)
    # Note: API 650 covers specific range, but typically used for larger tanks.
    if D < 0 or H < 0:
        warnings.append("Dimensions must be positive.")
        
    # 2. Shell Thickness Check (API 650 5.6.1.1)
    # Min thickness based on D (Nominal Tank Diameter)
    # < 15m: 5mm, 15-36: 6mm, 36-60: 8mm, >60: 10mm
    min_shell_allowed = 5.0
    if D >= 15 and D < 36: min_shell_allowed = 6.0
    elif D >= 36 and D < 60: min_shell_allowed = 8.0
    if D >= 60: min_shell_allowed = 10.0
    
    # Check used thickness
    for course in shell_courses:
        if course['t_used'] < min_shell_allowed:
             warnings.append(f"Warning: {course['Course']} thickness ({course['t_used']}mm) is less than API 650 Min ({min_shell_allowed}mm).")
    
    # 3. Method Check (API 650 5.6.3.1)
    # 1-Foot Method limited to D <= 61m (200ft)
    # Note: shell_method variable needed.
    # It's not passed to function.
    # But we can access it from outer scope if needed, or better, pass it.
    # Since I can't easily change signature in all calls without viewing them, I will use check in Tab 3 directly if function signature change is risky.
    # Actually I can change the signature here and the call below.
    
    return warnings

api_warnings = validate_api650(D, H, G, design_temp, shell_design.shell_courses)

# Extra check for Method (Inline)
if D > 61.0 and shell_method == '1ft':
    api_warnings.append("Warning: 1-Foot Method is invalid for D > 61m (API 650 5.6.3.1). Use VDM.")

# --- Wind Girder Results ---
with st.expander("Wind Girder (Intermediate) Check", expanded=False):
    st.write(f"Transformed Height (Htr): {wind_girder_res.get('Transformed Height H_tr (m)', 0):.2f} m")
    st.write(f"Max Unstiffened Height (H1): {wind_girder_res.get('Max Unstiffened H1 (m)', 0):.2f} m")
    st.write(f"Status: **{wind_girder_res.get('Status')}**")
    if wind_girder_res.get('Num Girders', 0) > 0:
        c_wg1, c_wg2 = st.columns(2)
        c_wg1.metric("Min Section Modulus (Z)", f"{wind_girder_res.get('Min Z (cm3)', 0):.2f} cm3")
        rec_s = wind_girder_res.get('Recommended Section', 'N/A')
        rec_w = wind_girder_res.get('Section Weight (kg/m)', 0.0)
        c_wg2.metric("Recommended Section", f"{rec_s}", f"{rec_w:.2f} kg/m")

# --- Nozzle Schedule Display ---
# --- Nozzle Schedule Display ---
with st.expander("Nozzle Schedule & Reinforcement Check (API 650 5.7)", expanded=False):
    if nozzle_res:
         # Format for better display
         df_nozzle = pd.DataFrame(nozzle_res)
         # Reorder cols if possible?
         cols_order = ['Mark', 'Size', 'Service', 'Elevation', 'Status', 'Check_Course', 'A_req_mm2', 'A_avail_mm2']
         # Check if cols exist
         available_cols = [c for c in cols_order if c in df_nozzle.columns]
         st.dataframe(df_nozzle[available_cols], hide_index=True)
         st.caption("A_req = Required Area (d x tr), A_avail = Available Area (Shell Excess + Pad)")
    else:
         st.info("No nozzles defined.")

# --- Visualization Generation ---
t_top_mm = shell_design.shell_courses[-1]['t_used'] if shell_design.shell_courses else 0
t_roof_mm = roof_design.t_used if roof_design else 0.0 

# Generate SVGs
try:
    shell_svg = generate_shell_svg(D, shell_design.shell_courses)
    nozzle_svg = generate_nozzle_orientation_svg(D, nozzle_res)
    wind_moment_svg = generate_wind_moment_svg(D, H, P_wind_kPa, M_wind_kNm)
    roof_detail_svg = generate_roof_detail_svg(detail_type, top_angle_size, t_top_mm, t_roof_mm)
except Exception as e:
    # Fallback for errors
    err_svg = f"<svg><text>Error: {e}</text></svg>"
    if not shell_svg: shell_svg = err_svg
    if not nozzle_svg: nozzle_svg = err_svg
    wind_moment_svg = err_svg
    roof_detail_svg = err_svg


# --- Venting Results Display ---
with st.expander("7. Venting Design (API 2000)", expanded=False):
    st.write("### Normal Venting")
    st.write(f"Inbreathing (Liquid): {venting_res['Inbreathing_Liquid_Nm3h']:.2f} Nm3/h")
    st.write(f"Inbreathing (Thermal): {venting_res['Inbreathing_Thermal_Nm3h']:.2f} Nm3/h")
    st.metric("Total Inbreathing Required", f"{venting_res['Total_Inbreathing_Nm3h']:.2f} Nm3/h")
    
    st.write("---")
    st.write(f"Outbreathing (Liquid): {venting_res['Outbreathing_Liquid_Nm3h']:.2f} Nm3/h")
    st.write(f"Outbreathing (Thermal): {venting_res['Outbreathing_Thermal_Nm3h']:.2f} Nm3/h")
    st.metric("Total Outbreathing Required", f"{venting_res['Total_Outbreathing_Nm3h']:.2f} Nm3/h")
    
    st.write("### Emergency Venting (Fire Case)")
    st.write(f"Wetted Area: {venting_res['Wetted_Area_m2']:.2f} m2 (Bottom 9.14m)")
    st.metric("Required Emergency Venting", f"{venting_res['Emergency_Venting_Nm3h']:.0f} Nm3/h (Air)")


# --- Tab 3: Results ---
with tab3:
    st.subheader("Calculation Summary")
    
    # Display Warnings
    if api_warnings:
         st.warning("### API 650 Compliance Check")
         for w in api_warnings:
             st.write(f"- {w}")

    # --- Visualization (Inside Tab 3) ---
    st.markdown("### Visualization")
    c_vis1, c_vis2 = st.columns(2)
    with c_vis1:
        st.caption("Shell Course Stackup")
        if shell_svg and shell_svg.strip():
            st.markdown(shell_svg, unsafe_allow_html=True)
        else:
            st.text("No Data")
    with c_vis2:
        st.caption("Nozzle Orientation")
        if nozzle_svg and nozzle_svg.strip():
            st.markdown(nozzle_svg, unsafe_allow_html=True)
        else:
            st.text("No Nozzles")
        
    c_vis3, c_vis4 = st.columns(2)
    with c_vis3:
        st.caption("Wind Moment Diagram")
        if wind_moment_svg and wind_moment_svg.strip():
            st.markdown(wind_moment_svg, unsafe_allow_html=True)
        else:
            st.text("No Data")
    with c_vis4:
        st.caption("Roof-to-Shell Detail")
        if roof_detail_svg and roof_detail_svg.strip():
            st.markdown(roof_detail_svg, unsafe_allow_html=True)
        else:
            st.text("No Data")
        # Calculate logic if missing? No, assume available.
        # But if we move it here, local 'shell_svg' variable is updated.
        # Fallback will handle missing case.
        
        st.markdown(shell_svg, unsafe_allow_html=True)
        
    with c_vis2:
        st.caption("Nozzle Orientation")
        if nozzle_svg and nozzle_svg.strip():
            st.markdown(nozzle_svg, unsafe_allow_html=True)
        else:
             st.text("No Nozzles")
    
    st.divider()
    
    # Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Shell Weight", f"{W_shell_kg/1000:.1f} ton")
    m2.metric("Roof Weight", f"{W_roof_kg/1000:.1f} ton")
    m3.metric("Uplift Force", f"{anchor_design.results.get('Net Uplift Force (kN)', 0):.1f} kN")
    m4.metric("Anchor Required?", anchor_design.results.get('Status', 'N/A'))

    # --- EFRT Specific Results ---
    if efrt_design_res:
         st.write("---")
         st.subheader("External Floating Roof Checks")
         
         col_ef1, col_ef2, col_ef3 = st.columns(3)
         col_ef1.metric("Buoyancy Safety Factor", f"{efrt_design_res.results.get('Safety_Factor', 0):.2f}", help="Min 1.0 (Operating)")
         
         deck_status = efrt_design_res.results.get('Deck_Thickness_Check', {}).get('Status', '-')
         col_ef2.metric("Deck Thickness Check", deck_status)
         
         raf_res = efrt_design_res.results.get('Rafter_Check', {})
         if raf_res:
             raf_status = raf_res.get('Status', '-')
             raf_stress = raf_res.get('Stress_MPa', 0)
             col_ef3.metric("Rafter Stress Check", raf_status, f"{raf_stress} MPa")
         
         leg_res = efrt_design_res.results.get('Leg_Check', {})
         if leg_res:
             leg_status = leg_res.get('Status', '-')
             leg_cap = leg_res.get('Capacity_kN', 0)
             st.caption(f"Leg Check: {leg_status} (Cap {leg_cap} kN for 2m Length)")

    # --- Bill of Materials (BOM) ---
    with st.expander("📝 Detailed Bill of Materials (BOM)", expanded=False):
        bom_data = []
        
        # 1. Shell Data
        bom_data.append({
            "Component": "Shell Plates",
            "Detail": f"{len(shell_design.shell_courses)} Courses",
            "Material": shell_design.shell_courses[0]['Material'] if shell_design.shell_courses else "-",
            "Weight (kg)": W_shell_kg,
            "Notes": "Includes all courses"
        })
        
        # 2. Roof Data
        if roof_type == "External Floating Roof":
             bom_data.append({
                "Component": "Ext Floating Roof",
                "Detail": "Deck + Pontoon",
                "Material": roof_material,
                "Weight (kg)": W_roof_kg,
                "Notes": f"Deck Thk: {efrt_params_ui.get('T_Deck')}mm"
             })
        else:
             w_plate = W_roof_kg
             if 'struct_data' in locals() and struct_data:
                 w_plate -= struct_data.get('Total Struct Weight (kg)', 0.0)
            
             bom_data.append({
                "Component": "Roof Plates",
                "Detail": roof_type,
                "Material": roof_material,
                "Weight (kg)": w_plate,
                "Notes": f"Thk: {roof_design.t_used}mm" if 'roof_design' in locals() else "-"
             })
        
        # 3. Structure (if any)
        if 'struct_data' in locals() and struct_data.get('Total Struct Weight (kg)', 0) > 0:
            bom_data.append({
                "Component": "Roof Structure",
                "Detail": "Rafters/Girders",
                "Material": f"Yield {struct_yield} MPa",
                "Weight (kg)": struct_data['Total Struct Weight (kg)'],
                "Notes": "See Structure Design"
            })
            
        # 4. Wind Girder
        wg_num = wind_girder_res.get('Num Girders', 0)
        if wg_num > 0:
            wg_sect = wind_girder_res.get('Recommended Section', '-')
            wg_unit_w = wind_girder_res.get('Section Weight (kg/m)', 0.0)
            wg_len = math.pi * D * wg_num # Approx length (centerline D)
            wg_total_w = wg_len * wg_unit_w
            
            bom_data.append({
                "Component": "Wind Girder",
                "Detail": f"{wg_num} x {wg_sect}",
                "Material": "As per Shell", # Assume same
                "Weight (kg)": wg_total_w,
                "Notes": "Intermediate Stiffeners"
            })
            
        # 5. Anchor Bolts
        # Approx weight: Count * Length * Area * Density
        # Length approx: 50 * Dia (embedment) + 200mm (projection) + ...?
        # Let's assume 1.0m average length for M30-M50 bolts for BOM estimation.
        # Density 7850 kg/m3.
        num_bolts = anchor_design.results.get('Number of Bolts', 0)
        if num_bolts > 0:
            dia_mm = anchor_design.results.get('Bolt Diameter (mm)', 0)
            bolt_area_mm2 = math.pi * (dia_mm/2)**2
            bolt_vol_m3 = (bolt_area_mm2 / 1e6) * 1.0 # 1m length
            bolt_weight_ea = bolt_vol_m3 * 7850.0
            total_bolt_w = num_bolts * bolt_weight_ea
            
            bom_data.append({
                "Component": "Anchor Bolts",
                "Detail": f"{num_bolts} x M{dia_mm}",
                "Material": "Carbon Steel",
                "Weight (kg)": total_bolt_w,
                "Notes": "Est. 1m Length each"
            })
        
        # Create DataFrame
        df_bom = pd.DataFrame(bom_data)
        
        # Formatting
        st.dataframe(
            df_bom,
            column_config={
                "Weight (kg)": st.column_config.NumberColumn("Weight (kg)", format="%.1f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        total_weight = df_bom['Weight (kg)'].sum()
        st.metric("Total Estimated Tank Weight", f"{total_weight/1000:.2f} ton")

    # --- KDS Comparison Table ---
    if 'use_kds' in locals() and use_kds:
        st.write("---")
        st.subheader("🇰🇷 Standard Comparison (API 650 vs KDS 41)")
        
        # Prepare Data
        # Wind
        api_wind_P = P_wind_kPa
        # kds_wind_P available
        
        # Seismic
        api_V = seismic_res.get('Base_Shear_kN', 0)
        kds_V = kds_seismic_res.get('Base_Shear_kN', 0)
        
        api_M = seismic_res.get('Overturning_Moment_kNm', 0)
        kds_M = kds_seismic_res.get('Overturning_Moment_kNm', 0)
        
        # Safe Division
        def calc_diff(a, b):
            if b == 0: return "-"
            return f"{(a - b)/b*100:.1f}%"
            
        comp_data = {
            "Item": ["Wind Pressure (kPa)", "Wind Moment (kNm)", "Seismic Base Shear (kN)", "Seismic Moment (kNm)"],
            "API 650 (ASCE 7)": [f"{api_wind_P:.3f}", f"{M_wind_kNm:.1f}", f"{api_V:.1f}", f"{api_M:.1f}"],
            "KDS 41 12/17": [f"{kds_wind_P:.3f}", f"{kds_wind_M:.1f}", f"{kds_V:.1f}", f"{kds_M:.1f}"],
            "Difference (%)": [
                calc_diff(kds_wind_P, api_wind_P),
                calc_diff(kds_wind_M, M_wind_kNm),
                calc_diff(kds_V, api_V),
                calc_diff(kds_M, api_M)
            ]
        }
        st.table(pd.DataFrame(comp_data))
        
        # --- Seismic Spectrum Visualization ---
        st.subheader("Seismic Response Spectrum (Design)")
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Parameters from calculation (API 650 Use)
            # We need SDS, SD1, TL.
            # They are available from Tab 2 inputs or seismic_load object (if passed)
            # Actually, seismic_load.calculate_loads doesn't return them explicit, but they are in 'params'.
            
            # Retrieve from params dict used for calc
            p_sds = params.get('SDS', 0.0)
            p_sd1 = params.get('SD1', 0.0)
            p_tl = params.get('TL', 4.0)
            
            if p_sds <= 0 or p_sd1 <= 0:
                 raise ValueError("SDS or SD1 is zero. Please check inputs.")

            # Generate T values
            t_max = p_tl + 2.0
            t_vals = np.linspace(0, t_max, 100)
            sa_vals = []
            
            Ts = p_sd1 / p_sds
            T0 = 0.2 * Ts
            
            for t in t_vals:
                if t < T0:
                    sa = p_sds * (0.4 + 0.6 * (t / T0))
                elif t < Ts:
                    sa = p_sds
                elif t < p_tl:
                    sa = p_sd1 / t
                else:
                    sa = (p_sd1 * p_tl) / (t**2)
                sa_vals.append(sa)
                
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot(t_vals, sa_vals, label=f"API 650 (SDS={p_sds:.2f}, SD1={p_sd1:.2f})", color='blue')
            
            # KDS Plot
            if use_kds and 'kds_params' in locals():
                try:
                    kds_obj = KDSSeismicLoad(kds_params)
                    k_sds = kds_obj.SDS
                    k_sd1 = kds_obj.S1
                    
                    sa_kvals = []
                    k_Ts = k_sd1 / k_sds if k_sds > 0 else 0
                    k_T0 = 0.2 * k_Ts
                    
                    for t in t_vals:
                        if t < k_T0: sa = k_sds * (0.4 + 0.6 * (t / k_T0))
                        elif t < k_Ts: sa = k_sds
                        elif t < p_tl: sa = k_sd1 / t
                        else: sa = (k_sd1 * p_tl) / (t**2)
                        sa_kvals.append(sa)
                    
                    ax.plot(t_vals, sa_kvals, label=f"KDS 41 17 (SDS={k_sds:.2f}, SD1={k_sd1:.2f})", color='red', linestyle='--')
                except Exception as ex:
                    # st.write(f"Debug: KDS Plot Error - {ex}")
                    pass

            ax.set_xlabel("Period T (s)")
            ax.set_ylabel("Spectral Acceleration Sa (g)")
            ax.set_title("Design Response Spectrum")
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend()
            
            st.pyplot(fig)
            
            # Save for Report
            import io
            import base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            seismic_graph_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()
            
        except Exception as e:
            st.error(f"Could not plot spectrum: {e}")
            seismic_graph_b64 = None
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.markdown("### Shell Thickness Details")
        # Shell Checks
        shell_info = getattr(shell_design, 'design_report_info', {'Method': shell_method_ui, 'Formula': ''})
        st.info(f"Method Applied: **{shell_info['Method']}**")
        if shell_info.get('Formula'):
            st.caption(f"Formula: {shell_info['Formula']}")
        st.dataframe(pd.DataFrame(shell_design.shell_courses))
        
    with col_res2:
        st.markdown("### Component Design Check")
        
        st.write("**Roof Design**")
        st.write(f"- Type: {roof_type}")
        
        if roof_design:
            # Fixed Roof Display
            roof_res = roof_design.results.get('Roof Plate', {})
            st.write(f"- Min Thk (Std/Calc): {roof_res.get('Min Thk (Std)',0):.2f} mm")
            st.write(f"- Status: {roof_res.get('Status', 'N/A')}")
        elif efrt_design_res:
            # EFRT Display
            e_res = efrt_design_res.results
            deck_chk = e_res.get('Deck_Thickness_Check', {})
            st.write(f"- Deck Thk Provided: {deck_chk.get('Provided', 0):.1f} mm")
            st.write(f"- Deck Status: {deck_chk.get('Status', 'N/A')}")
            st.write(f"- Buoyancy Safety Factor: {e_res.get('Safety_Factor', 0):.2f}")
        else:
            st.write("No Design Results")
        
        st.write("**Bottom Design**")
        bot_res = bottom_design.results.get('Bottom Plate', {})
        st.write(f"- Required Thk: {bot_res.get('Req Thk (mm)',0):.2f} mm")
        
        ann_res = bottom_design.results.get('Annular Plate', {})
        st.write(f"**Annular Plate**: {ann_res.get('Required?', 'N/A')}")
        if ann_res.get('Min Width (mm)', 0) > 0:
             st.write(f"- Min Width: {ann_res.get('Min Width (mm)', 0):.1f} mm")
        if ann_res.get('Warning'):
             st.error(f"⚠️ {ann_res['Warning']}")
             
        if roof_design:
            st.write("**Annex F (Top Angle)**")
            ann_f = annex_f.results
            st.write(f"- Size: {ann_f.get('Top Angle', '-')}")
            st.write(f"- Junction Area: {ann_f.get('Junction Area (mm2)', 0):.0f} mm2")
            st.caption(f"Ref: {ann_f.get('Detail', 'Generic')}")
            
            # Frangibility Check
            area_junc = ann_f.get('Junction Area (mm2)', 0)
            # Weights
            w_shell_tot = W_shell_kg
            w_roof_plates_tot, _ = roof_design.calculate_roof_weight()
            w_roof_struct_tot = struct_data.get('Total_Struct_Weight', 0)
            
            frangible_res = roof_design.check_frangibility(w_shell_tot, w_roof_plates_tot, w_roof_struct_tot, area_junc)
            
            st.write("**Frangible Roof Check**")
            st.write(f"- Participating Area: {frangible_res.get('Participating_Area_mm2', 0):.0f} mm2")
            ft_status = "Frangible" if frangible_res.get('Is_Frangible') else "Not Frangible"
            st.write(f"- Status: **{ft_status}**")
            if not frangible_res.get('Is_Frangible'):
                 st.warning(f"⚠️ {frangible_res.get('Warning', 'Check Failed')}")
                 st.error("🚨 Emergency Venting is REQUIRED.")
        else:
             # EFRT Case
             frangible_res = {} # Not applicable


    st.markdown("### Seismic Results (Annex E - 13th Ed)")
    
    # Seismic Hoop Stress Check (Max of API/KDS)
    st.write("**Seismic Hoop Stress Check (E.6.2.4)**")
    
    # Calculate API Stress
    api_hoop = seismic_load.check_hoop_stress(t_shell_bot_mm, max_level, Sd_first, joint_efficiency)
    
    final_hoop_res = api_hoop
    applied_std = "API 650 Annex E"
    
    if 'use_kds' in locals() and use_kds:
        kds_hoop = kds_seismic.check_hoop_stress(t_shell_bot_mm, max_level, Sd_first, joint_efficiency)
        
        # Compare
        if kds_hoop['Stress_MPa'] > api_hoop['Stress_MPa']:
            final_hoop_res = kds_hoop
            applied_std = "KDS 41 17 (Governing)"
        else:
            applied_std = "API 650 (Governing > KDS)"
            
        st.caption(f"Comparing API ({api_hoop['Stress_MPa']:.1f} MPa) vs KDS ({kds_hoop['Stress_MPa']:.1f} MPa)")

    # Display Result
    c_s1, c_s2, c_s3 = st.columns(3)
    c_s1.metric("Applied Standard", applied_std)
    c_s2.metric("Seismic Hoop Stress", f"{final_hoop_res['Stress_MPa']:.1f} MPa", f"Allow: {final_hoop_res['Allow_MPa']:.1f} MPa")
    c_s3.metric("Status", final_hoop_res['Status'])
    
    st.write(f"**Base Shear V**: {seismic_res['Base_Shear_kN']:.1f} kN | **Overturning M**: {seismic_res['Overturning_Moment_kNm']:.1f} kNm")
    
    # Anchor Results
    with st.expander("Anchor Bolt & Chair Design", expanded=False):
        st.subheader("Anchor Bolt Check (API 650 5.12 / F.7)")
        st.write(f"Status: **{anchor_design.results.get('Status')}**")
        st.write(f"Net Uplift Force: {anchor_design.results.get('Net Uplift Force (kN)',0):.1f} kN")
        
        if anchor_design.results.get('Number of Bolts', 0) > 0:
            st.success(f"Required: {anchor_design.results['Number of Bolts']} bolts, M{anchor_design.results['Bolt Diameter (mm)']}")
            st.write(f"Required Bolt Area: {anchor_design.results['Required Bolt Area (mm2)']:.0f} mm2")
            
            st.divider()
            st.subheader("Anchor Chair Design Check")
            st.info("Simplified design based on generic guidelines (Bednar/AISI).")
            c_ac1, c_ac2 = st.columns(2)
            c_ac1.write(f"Top Plate Thk: **{anchor_chair.results.get('Top Plate Thk (mm)',0):.1f} mm**")
            c_ac1.write(f"Chair Height: **{anchor_chair.results.get('Chair Height (mm)',0):.0f} mm**")
            c_ac2.write(f"Top Plate Width: **{anchor_chair.results.get('Top Plate Width (mm)',0):.0f} mm**")
            c_ac2.write(f"Eccentricity: {anchor_chair.results.get('Eccentricity (mm)',0):.1f} mm")

    # --- PREPARE DATA FOR REPORT (PERSISTENCE) ---
    # Calculate Capacities
    import math
    R_calc = D / 2.0
    vol_gross_m3 = math.pi * (R_calc**2) * H
    
    # Ensure max_level is valid
    # Use simple variable reference - they are defined in scope
    calc_max_level = max_level
    calc_min_level = min_level
    
    st.write(f"DEBUG: Levels used -> Max: {calc_max_level}, Min: {calc_min_level}")
    st.write(f"DEBUG: Vars -> max_level: {max_level}, min_level: {min_level}")
    
    effective_HD = float(calc_max_level) - float(calc_min_level)
    if effective_HD < 0: effective_HD = 0.0
    
    vol_net_m3 = math.pi * (R_calc**2) * effective_HD
    
    # Estimate Bottom Weight
    bot_res_dict = bottom_design.results.get('Bottom Plate', {})
    t_bot_c = bot_res_dict.get('Used Thk (mm)', 6.0) / 1000.0
    W_bot_est = math.pi * (R_calc**2) * t_bot_c * 7850.0
    
    # Total Empty Weight
    # W_shell_kg is available local
    # W_roof_kg is available local (includes struct if supported)
    W_empty_total = W_shell_kg + W_roof_kg + W_bot_est
    
    # Operation Weight
    dens_liq = G * 1000.0
    W_op_total = W_empty_total + (vol_net_m3 * dens_liq)
    
    # Package Data
    # Ensure Importance Factor exists
    if 'Importance Factor' not in seismic_res and 'I_seismic' in locals():
             seismic_res['Importance Factor'] = I_seismic
             
    # Prepare Standard Comparison Data
    std_comp_data = {}
    if 'use_kds' in locals() and use_kds:
        def calc_safe_diff(val_k, val_a):
             if val_a == 0: return 0.0
             return ((val_k - val_a) / val_a) * 100.0
             
        std_comp_data = {
            'Wind': {
                'API_Pressure': P_wind_kPa,
                'KDS_Pressure': locals().get('kds_wind_P', 0),
                'Diff_Pressure': calc_safe_diff(locals().get('kds_wind_P',0), P_wind_kPa),
                'API_Moment': M_wind_kNm,
                'KDS_Moment': locals().get('kds_wind_M', 0),
                'Diff_Moment': calc_safe_diff(locals().get('kds_wind_M',0), M_wind_kNm)
            },
            'Seismic': {
                'API_BaseShear': seismic_res.get('Base_Shear_kN', 0),
                'KDS_BaseShear': locals().get('kds_seismic_res', {}).get('Base_Shear_kN', 0),
                'Diff_BaseShear': calc_safe_diff(locals().get('kds_seismic_res',{}).get('Base_Shear_kN',0), seismic_res.get('Base_Shear_kN', 0)),
                'API_Moment': seismic_res.get('Overturning_Moment_kNm', 0),
                'KDS_Moment': locals().get('kds_seismic_res', {}).get('Overturning_Moment_kNm', 0),
                 'Diff_Moment': calc_safe_diff(locals().get('kds_seismic_res',{}).get('Overturning_Moment_kNm',0), seismic_res.get('Overturning_Moment_kNm', 0))
            }
        }
    
    report_data = {
        'standard_comparison': std_comp_data,
        'project_info': {'name': project_name, 'designer': designer_name},
        'design_data': {
            'D': D, 'H': H, 'G': G, 'P_design': P_design_mm, 
            'CA': CA, 'CA_roof': CA_roof, 'CA_bottom': CA_bottom, 
            'Shell_Method': getattr(shell_design, 'design_report_info', {}).get('Method', shell_method_ui),
            'roof_type': roof_type,
            'roof_slope': roof_slope
        },
        'weights': {
            'W_shell_kg': W_shell_kg,
            'W_roof_kg': W_roof_kg,
        },
        'anchor': anchor_design.results,
        'nozzle_data': nozzle_res, # Required for legacy report call
        'wind_girder': wind_girder_res, # Required for legacy report call
        'capacities': {
            'Gross Capacity (m3)': vol_gross_m3,
            'Net Capacity (m3)': vol_net_m3, # Keep for backward compatibility if any
            'Vol_Net_m3': vol_net_m3, # SAFE KEY
            'Gross Capacity (bbl)': vol_gross_m3 * 6.2898,
            'Net Capacity (bbl)': vol_net_m3 * 6.2898,
            'Empty Weight (kg)': W_empty_total,
            'Operation Weight (kg)': W_op_total
        },
        'gov_codes': {'Wind': gov_wind_code, 'Seismic': gov_seismic_code}, # Pass codes at root
        'results': {
            'shell_courses': shell_design.shell_courses,
            'shell_res': {'Shell Courses': shell_design.shell_courses}, # Mapper for Report_v2026/Classic checks
            'roof_res': roof_design.results if roof_design else {},
            'efrt_res': efrt_design_res.results if efrt_design_res else {},
            'struct_data': struct_data, # Use local var
            'bottom_res': bottom_design.results,
            'seismic_res': gov_seismic_res, # Use Governing Seismic Data
            'seismic_hoop_res': final_hoop_res if 'final_hoop_res' in locals() else {}, # Explicit Hoop Stress
            'venting_res': venting_res, # New API 2000 Data
            'wind_girder_res': wind_girder_res, # New API 650 5.9
            'nozzle_res': nozzle_res, # New Nozzle Schedule
            'annex_f_res': annex_f.results if 'annex_f' in locals() else {},
            'anchor_res': anchor_design.results,
            'anchor_chair_res': anchor_chair.results,
            'top_member': top_member_res if 'top_member_res' in locals() else {},
            'frangibility_res': frangible_res if 'frangible_res' in locals() else {},
            'wind_res': {
                'V': V_wind,
                'P_wind_kPa': gov_wind_P, # Use Governing
                'M_wind_kNm': gov_wind_M, # Use Governing
                'Kz': getattr(wind_load, 'Kz', 1.0),
                'Kzt': getattr(wind_load, 'Kzt', 1.0),
                'Kd': getattr(wind_load, 'Kd', 0.95),
                'G': getattr(wind_load, 'G', 0.85),
                'I': getattr(wind_load, 'I', 1.0),
                'Snow Load': snow_load,
                'Live Load': live_load,
                'Dead Load Add': dead_load_add
            }
        },

        'mawp': {'MAWP': f"{P_design_mm} mmH2O", 'MAWV': "25 mmH2O (std)"},
        'extended': {
            'shell_svg': shell_svg,
            'nozzle_svg': nozzle_svg
        }
    }
    
    # Extended data
    # Calculate OD, Nominal D
    t_bot_mm = shell_design.shell_courses[0]['t_used']
    t_bot_m = t_bot_mm / 1000.0
    D_nominal_real = ID_input + t_bot_m
    OD_calc = ID_input + 2 * t_bot_m
    
    # Seismic Check Loop (Recreated here for persistence)
    seismic_shell_checks = []
    eff_H_seismic = max_level 
    current_h_for_seismic = 0.0
    for course in shell_design.shell_courses:
        c_name = course['Course']
        mat = course['Material']
        t_used_mm = course['t_used']
        t_used_m = t_used_mm / 1000.0
        width = course['Width']
        check_y = current_h_for_seismic
        gamma_water = 9.80665
        gamma_liq = G * gamma_water
        head = eff_H_seismic - check_y
        if head < 0: head = 0
        P_stat = gamma_liq * head 
        Pi, Pc = gov_seismic_load_obj.calculate_hydrodynamic_pressure(check_y, eff_H_seismic)
        P_dyn = math.sqrt(Pi**2 + Pc**2)
        P_total = P_stat + P_dyn
        Sig_total_kPa = (P_total * D) / (2 * t_used_m)
        Sig_total_MPa = Sig_total_kPa / 1000.0
        Sd, St = shell_design.get_material_stress(mat)
        Allowable_Seismic = 1.333 * Sd * joint_efficiency
        status = "OK"
        ratio = Sig_total_MPa / Allowable_Seismic
        if ratio > 1.0: status = "FAIL"
        seismic_shell_checks.append({
            'Course': c_name, 'y (m)': check_y, 't_used (mm)': t_used_mm,
            'P_stat (kPa)': P_stat, 'P_dyn (kPa)': P_dyn,
            'Stress (MPa)': Sig_total_MPa, 'Allow (MPa)': Allowable_Seismic,
            'Ratio': ratio, 'Status': status
        })
        current_h_for_seismic += width
        
    extended_design_data = {
        'OD': OD_calc,
        'ID': ID_input,
        'D_Nominal': D_nominal_real,
        'Max_Level': max_level,
        'Min_Level': min_level,
        'Design_Temp': design_temp,
        'MDMT': mdmt,
        'Joint_Efficiency': joint_efficiency,
        'Liquid_Name': liquid_name,
        'Annex_F_Data': annex_f_res,
        'Anchor_Data': anchor_design.results,
        'Seismic_Shell_Check': seismic_shell_checks
    }
    
    # Applied Annexes
    applied_annexes = ["Annex L (Data Sheet)"]
    if p_design_kPa > 0 : applied_annexes.append("Annex F (Internal Pressure)")
    if P_external_kPa > 0.25: applied_annexes.append("Annex V (External Pressure)")
    if design_temp > 93.0: applied_annexes.append("Annex M (High Temperature)")
    is_seismic = False
    if "Mapped" in seismic_method and (Ss > 0 or S1 > 0): is_seismic = True
    elif "Design" in seismic_method and (SDS > 0 or SD1 > 0): is_seismic = True
    elif "Single" in seismic_method and (Sp > 0): is_seismic = True
    if is_seismic: applied_annexes.append("Annex E (Seismic)")
    mats_used = [c['Material'] for c in shell_design.shell_courses]
    if any('304' in m or '316' in m for m in mats_used): applied_annexes.append("Annex S (Stainless Steel)")
    if any('2205' in m for m in mats_used): applied_annexes.append("Annex X (Duplex Stainless)")
    if any('5083' in m or '6061' in m for m in mats_used): applied_annexes.append("Annex AL (Aluminum)")
    for ann in purchaser_annexes:
        short_name = ann.split(' ')[0] + ' ' + ann.split(' ')[1]
        is_dup = False
        for existing in applied_annexes:
            if short_name in existing:
                is_dup = True
                break
        if not is_dup: applied_annexes.append(ann)
    if shell_method == 'annex_a':
         if "Annex A (Small Tanks)" not in applied_annexes: applied_annexes.append("Annex A (Small Tanks)")
    
    extended_design_data['Applied_Annexes'] = applied_annexes
    report_data['extended'] = extended_design_data

    st.session_state['report_data'] = report_data
    st.session_state['report_data'] = report_data
    
    # --- Update Dynamic Warning Placeholder in Tab 1 ---
    # This must run AFTER calculations but BEFORE script exit.
    try:
        ann_plate_final = bottom_design.results.get('Annular Plate', {})
        warn_final = ann_plate_final.get('Warning')
        if warn_final and ann_warning_placeholder:
             # Filtering: Only show if RELEVANT to current input state?
             # Actually, if BottomDesign logic is correct, this warning IS relevant.
             # e.g. "Insufficient Width" if checked, or "Missing" if unchecked.
             ann_warning_placeholder.error(f"⚠️ {warn_final}")
        elif ann_warning_placeholder:
             ann_warning_placeholder.empty() # Clear if no warning
    except Exception as e:
        pass # Placeholder might not be accessible if Tab 1 not rendered? (Scope issue not expected)

    st.success("Calculations completed. Go to 'Report' tab to download.")
    
# --- Tab 4: Report ---
with tab4:
    st.subheader("Download Report")
    
    report_type = st.radio("Select Report Type", 
                           ["Summary Report", "Full Calculation Report (Detailed 50+ Pages)", "Ver.2026 (Professional)"], 
                           index=0, horizontal=True)
    
    template_to_use = "report_template.html"
    if report_type == "Summary":
        template_to_use = "report_template.html"
    elif "Full" in report_type:
        template_to_use = "full_report_template.html"
    # Note: Ver.2026 does not use template_name, it generates HTML programmatically

    st.write("Generate professional HTML report.")
        
    if 'report_data' not in st.session_state:
        st.warning("⚠️ No calculation results found. Please go to the **Calculations** tab and click **Run Calculations** first.")
        st.info("The report module relies on the latest calculation data.")
        html_content = None
    else:
        rd = st.session_state['report_data']
        res = rd['results']
            
        # --- STALE DATA CHECK ---
        if 'weights' not in rd:
             st.error("⚠️ Data structure is outdated (from previous code version).")
             st.warning("👉 Please go to '3. Calculation Results' tab and click **'Run Calculations'** again to refresh the data.")
             st.stop()
            
        st.success(f"✅ Report System Updated: Ready to Generate ({report_type})")
            
        # Display Summary
        st.markdown("#### Design Summary")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Net Capacity", f"{rd['capacities']['Net Capacity (m3)']:.1f} m3")
        with c2:
            st.metric("Empty Weight", f"{rd['capacities']['Empty Weight (kg)']:.0f} kg")
        with c3:
            st.metric("Structure Weight", f"{rd['results']['struct_data'].get('Total_Struct_Weight', 0):.0f} kg")

        # --- PREPARE EXTENDED DATA (SVGs & Graphs) ---
        extended_context = {}
        if 'extended' in rd:
            extended_context.update(rd['extended'])
            
        # Update with fresh SVGs (ensures latest state)
        extended_context.update({
            'shell_svg': shell_svg,
            'nozzle_svg': nozzle_svg,
            'wind_moment_svg': wind_moment_svg,
            'roof_detail_svg': roof_detail_svg,
            'seismic_graph': seismic_graph_b64,
            'anchor': rd.get('anchor', {}),
            'annex_f': res.get('annex_f_res', {}),
            'anchor_chair': res.get('anchor_chair_res', {}),
            'standard_comparison': rd.get('standard_comparison', {}),
            'gov_codes': rd.get('gov_codes', {}),
            'seismic_hoop_res': res.get('seismic_hoop_res', {}),
            'capacities': rd.get('capacities', {}),
            'weights': rd.get('weights', {})
        })

        # --- GENERATE HTML ---
        if "Ver.2026" in report_type:
            # NEW ENGINE (Professional 17-Chapter)
            gen_2026 = ReportGenerator2026(
                project_info=rd['project_info'],
                design_data=rd['design_data'],
                calculation_results=rd['results'],
                extended_data=extended_context
            )
            html_content = gen_2026.generate_html()
                
        else:
            # CLASSIC ENGINE
            html_gen = HTMLReportGenerator(template_name=template_to_use)
                
            # Inject Extended Data
            html_gen.data_context.update(extended_context)
                
            # Set Info & Data
            info = rd['project_info']
            dd = rd['design_data']
            html_gen.set_project_info(info['name'], info['designer'])
            html_gen.set_design_data(dd['D'], dd['H'], dd['G'], dd['P_design'], dd['CA'], dd['CA_roof'], dd['CA_bottom'], dd['Shell_Method'])
                
            # Set Results
            res = rd['results']
                
            roof_data_dict = res['roof_res'].get('Roof Plate', {})
            bottom_data_dict = res['bottom_res'].get('Bottom Plate', {})
            annular_data_dict = res['bottom_res'].get('Annular Plate', {})
                
            wind_data_in = res.get('wind_res', {})
            if not wind_data_in:
                p_w_kpa = rd['design_data'].get('P_design', 0) / 100 
                wind_data_in = {'P_wind_kPa': p_w_kpa} 

            html_gen.set_results(
                W_shell_kg=rd['weights']['W_shell_kg'],
                W_roof_kg=rd['weights']['W_roof_kg'],
                net_uplift=rd['anchor'].get('Net Uplift Force (kN)', 0),
                wind_moment=rd['anchor'].get('Wind Overturning Moment (kN-m)', 0),
                seismic_moment=rd['anchor'].get('Seismic Overturning Moment (kN-m)', 0),
                shell_data=res['shell_res'],
                roof_data=roof_data_dict,
                bottom_data=bottom_data_dict,
                annular_data=annular_data_dict,
                wind_data=wind_data_in,
                seismic_data={
                    **res['seismic_res'],
                    'Base Shear V (kN)': res['seismic_res'].get('Base_Shear_kN', 0),
                    'Mrw (kNm)': res['seismic_res'].get('Ringwall_Moment_kNm', 0),
                    'Ms (kNm)': res['seismic_res'].get('Slab_Moment_kNm', 0), 
                    'Ms_kNm': res['seismic_res'].get('Slab_Moment_kNm', 0),
                    'J': res['seismic_res'].get('Anchorage_Ratio_J', 0),
                    'd_max (m)': res['seismic_res'].get('d_max_m', 0),
                    'Sliding_Res (kN)': res['seismic_res'].get('Sliding_Friction_Res_kN', 0),
                    'Importance Factor': res['seismic_res'].get('Importance Factor', 1.0),
                    'Importance_Factor': I_seismic if 'I_seismic' in locals() else res['seismic_res'].get('Importance Factor', 1.0)
                },
                nozzle_data=rd['nozzle_data'],
                wind_girder=rd['wind_girder'],
                top_angle=rd.get('top_angle', {}),
                structure=rd['results'].get('struct_data', {}),
                efrt=res.get('efrt_res', {}),
                capacity=rd.get('capacities', {}),
                venting=res.get('venting_res', {}),
                frangibility=res.get('frangibility_res', {}),
                roof_detail_svg=rd.get('roof_detail_svg', ""),
                seismic_graph=rd.get('seismic_graph', ""),
                anchor=rd.get('anchor', {}),
                annex_f=res.get('annex_f_res', {}),
                anchor_chair=res.get('anchor_chair_res', {}),
                standard_comparison=rd.get('standard_comparison', {}),
                gov_codes=rd.get('gov_codes', {}),
                seismic_hoop_res=res.get('seismic_hoop_res', {}),
                anchor_status=rd['anchor'].get('Status', 'N/A'),
                anchor_data=rd['anchor'],
                shell_courses=res['shell_courses'],
                roof_type=rd['design_data'].get('roof_type', 'Supported Cone Roof'),
                roof_slope=rd['design_data'].get('roof_slope', 0.0625),
                struct_data=res['struct_data'],
                top_member_data=res['top_member'],
                capacities_data=rd['capacities'],
                mawp_data=rd['mawp'],
                venting_data=res.get('venting_res', {}),
                wind_girder_data=res.get('wind_girder_res', {}),
                nozzle_data_res=res.get('nozzle_res', []),
                efrt_data=res.get('efrt_res', {})
            )
                
            # Generate content (Classic)
            html_content = html_gen.generate_html()

    # Check for content before showing download
    if html_content:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Re-introduce Filename Sanitization
        import re
        safe_project_name = re.sub(r'[<>:"/\\|?*]', '_', project_name)
        safe_project_name = safe_project_name.strip().replace(' ', '_')
        file_name_dl = f"Calc_Report_{safe_project_name}_{ts}.html"
        
        st.divider()
        st.subheader("Download Report")

        # Standard Web Download (Works on Cloud & Local)
        st.download_button(
            label="📄 Download HTML Report",
            data=html_content,
            file_name=file_name_dl,
            mime="text/html",
            key="download_html_btn"
        )
        
        st.caption("Click the button above to save the report to your device.")
