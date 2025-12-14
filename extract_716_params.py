
import re

def extract():
    f_path = "dump_716.txt"
    try:
        try:
            with open(f_path, 'r', encoding='utf-16') as f:
                content = f.read()
        except:
            with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        # Regex to find "Wtr_X = [Number] * SQRT"
        # Example: Wtr_1 = 2900.0 * SQRT
        
        keywords = ["102", "716-D-102", "D-102"]
        
        for k in keywords:
            idx = content.find(k)
        
    except Exception as e:
        print(e)

if __name__ == "__main__":
    extract()
