
import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Target lines with c_kds1 or c_kds2 if indented by 12 spaces
    if line.startswith('            ') and ('c_kds1' in line or 'c_kds2' in line):
        # 12 spaces -> 8 spaces
        new_lines.append(line[4:])
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("UI indentation fixed.")
