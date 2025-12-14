
import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # 0-indexed in list, but line numbers in editor are 1-indexed.
    line_num = i + 1
    
    if 188 <= line_num <= 200:
        # Dedent by 4 spaces (8 -> 4)
        if line.startswith('    '):
            new_lines.append(line[4:])
        else:
            new_lines.append(line)
    elif line_num >= 202:
        # Dedent by 4 spaces (4 -> 0)
        # Note: Some lines might be indented further (nested blocks).
        # We just remove the FIRST 4 spaces if they exist.
        if line.startswith('    '):
            new_lines.append(line[4:])
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Indentation fixed.")
