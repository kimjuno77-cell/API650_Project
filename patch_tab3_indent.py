
import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

clean_block = [
    "\n",
    "    # --- KDS Comparison Table ---\n",
    "    if 'use_kds' in locals() and use_kds:\n", # 4 spaces
    "        st.write(\"---\")\n", # 8 spaces
    "        st.subheader(\"🇰🇷 Standard Comparison (API 650 vs KDS 41)\")\n",
    "        \n",
    "        # Prepare Data\n",
    "        # Wind\n",
    "        api_wind_P = P_wind_kPa\n",
    "        # kds_wind_P available\n",
    "        \n",
    "        # Seismic\n",
    "        api_V = seismic_res.get('Base_Shear_kN', 0)\n",
    "        kds_V = kds_seismic_res.get('Base_Shear_kN', 0)\n",
    "        \n",
    "        api_M = seismic_res.get('Overturning_Moment_kNm', 0)\n",
    "        kds_M = kds_seismic_res.get('Overturning_Moment_kNm', 0)\n",
    "        \n",
    "        # Safe Division\n",
    "        def calc_diff(a, b):\n",
    "            if b == 0: return \"-\"\n",
    "            return f\"{(a - b)/b*100:.1f}%\"\n",
    "            \n",
    "        comp_data = {\n",
    "            \"Item\": [\"Wind Pressure (kPa)\", \"Wind Moment (kNm)\", \"Seismic Base Shear (kN)\", \"Seismic Moment (kNm)\"],\n",
    "            \"API 650 (ASCE 7)\": [f\"{api_wind_P:.3f}\", f\"{M_wind_kNm:.1f}\", f\"{api_V:.1f}\", f\"{api_M:.1f}\"],\n",
    "            \"KDS 41 12/17\": [f\"{kds_wind_P:.3f}\", f\"{kds_wind_M:.1f}\", f\"{kds_V:.1f}\", f\"{kds_M:.1f}\"],\n",
    "            \"Difference (%)\": [\n",
    "                calc_diff(kds_wind_P, api_wind_P),\n",
    "                calc_diff(kds_wind_M, M_wind_kNm),\n",
    "                calc_diff(kds_V, api_V),\n",
    "                calc_diff(kds_M, api_M)\n",
    "            ]\n",
    "        }\n",
    "        st.table(pd.DataFrame(comp_data))\n",
    "    \n"
]

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "m4.metric(\"Anchor Required?\"" in line:
        start_idx = i
    if "col_res1, col_res2 = st.columns(2)" in line:
        end_idx = i
        break # Stop at first occurrence? Wait, might be multiple? No, col_res1 is unique usually.

if start_idx != -1 and end_idx != -1:
    # Replace lines between start_idx and end_idx (exclusive of anchors)
    # We keep lines[start_idx] (m4) and lines[end_idx] (col_res1)
    # We replace slice lines[start_idx+1 : end_idx]
    
    # Check if lines between them are the corrupted block
    # Assuming yes.
    
    final_lines = lines[:start_idx+1] + clean_block + lines[end_idx:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    print(f"Replaced block between lines {start_idx+1} and {end_idx+1}.")
else:
    print(f"Anchors not found. Start: {start_idx}, End: {end_idx}")
