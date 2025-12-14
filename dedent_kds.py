
import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Check if this is one of our inserted lines (KDS logic)
    # They started with 4 spaces in the patch script
    # Pattern: Starts with 4 spaces AND contains "kds_" or "KDS" or "Loads.KDS"
    if line.startswith('    ') and ('kds_' in line or 'KDS' in line or 'use_kds' in line or 'if \'use_kds\'' in line):
        # Additional check: exclude lines that SHOULD be indented (inside if/def)
        # But my patch script indented the IF statement itself too.
        # "    if 'use_kds' in locals() and use_kds:"
        # This line should be at 0.
        # Lines INSIDE it ("        kds_params = ...") are at 8 spaces.
        # They should be at 4 spaces.
        # So essentially, I want to dedent ALL KDS-related lines by 4 spaces.
        
        # Safe heuristic: If line has 'kds' related content, dedent 4 spaces.
        new_lines.append(line[4:])
    elif line.lower().startswith('    # kds'): # Comment
         new_lines.append(line[4:])
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("KDS logic dedented.")
