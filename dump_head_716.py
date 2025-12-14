
def dump_head():
    f_path = "dump_716.txt"
    try:
        try:
            with open(f_path, 'r', encoding='utf-16') as f:
                lines = f.readlines()
        except:
            with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        for i, line in enumerate(lines[:200]):
            print(f"{i}: {line.strip()}")
            
    except Exception as e:
        print(e)
if __name__ == "__main__":
    dump_head()
