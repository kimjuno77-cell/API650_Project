
import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
wind_duplicate_removed = False

kds_wind_logic = [
    "\n",
    "    # KDS Wind Calculation\n",
    "    kds_wind_P = 0.0\n",
    "    kds_wind_M = 0.0\n",
    "    if 'use_kds' in locals() and use_kds:\n",
    "        # Prepare KDS Params\n",
    "        kds_params = params.copy()\n",
    "        kds_params.update({\n",
    "            'KDS_V0': kds_V0,\n",
    "            'KDS_Terrain': kds_Terrain,\n",
    "            'KDS_Iw': kds_Iw,\n",
    "            'KDS_Zone': kds_Zone,\n",
    "            'KDS_Soil': kds_Soil,\n",
    "            'H': H, 'D': D\n",
    "        })\n",
    "        kds_wind = Loads.KDSWindLoad(kds_params)\n",
    "        kds_wind_P = kds_wind.calculate_pressure()\n",
    "        kds_wind_M = kds_wind.calculate_moment()\n",
    "\n"
]

kds_seismic_logic = [
    "\n",
    "    # KDS Seismic Calculation\n",
    "    kds_seismic_res = {}\n",
    "    if 'use_kds' in locals() and use_kds:\n",
    "        # KDS Params prepared above\n",
    "        kds_seismic = Loads.KDSSeismicLoad(kds_params)\n",
    "        kds_seismic_res = kds_seismic.calculate_loads(W_shell_kg, W_roof_kg, W_liquid_kg)\n",
    "\n"
]

for i, line in enumerate(lines):
    # Remove Duplicate P_wind Line
    if "P_wind_kPa = wind_load.calculate_pressure()" in line:
        if not wind_duplicate_removed:
            new_lines.append(line)
            wind_duplicate_removed = True # Keep first
        else:
            continue # Skip second
    else:
        new_lines.append(line)
        
    # Insert KDS Wind Logic
    if "M_wind_kNm = wind_load.calculate_overturning_moment()" in line:
        new_lines.extend(kds_wind_logic)

    # Insert KDS Seismic Logic
    if "seismic_res = seismic_load.calculate_loads(W_shell_kg, W_roof_kg, W_liquid_kg)" in line:
        new_lines.extend(kds_seismic_logic)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Referenced Loads.py logic injected.")
