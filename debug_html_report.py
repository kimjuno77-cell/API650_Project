
import re

def find_context():
    f_path = r"c:\Users\User\Desktop\API650_Project\Calc_Report_New_Tank_Project_20251214_164150.html"
    try:
        with open(f_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"File size: {len(content)}")
        
        # Search for 2.418
        iter = re.finditer(r"2\.418", content)
        found = False
        for m in iter:
            found = True
            start = max(0, m.start() - 200)
            end = min(len(content), m.end() + 200)
            print(f"\n--- Found at {m.start()} ---")
            print(content[start:end])
            
        if not found:
            print("2.418 not found in file.")
            
    except Exception as e:
        print(e)

if __name__ == "__main__":
    find_context()
