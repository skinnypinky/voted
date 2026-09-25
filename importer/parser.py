import os
import json

def dir_iterator(current_dir):
    for file_name in os.listdir(current_dir):
        file_path = os.path.join(current_dir, file_name)
        if file_path.endswith(".json"):
            parse_file(file_path)

def parse_file(file_path):
    with open(file_path) as f:
        json_d = json.load(f)
        print(json_d)

def main():
    current_dir = os.path.join(os.getcwd() + "/data")
    
    for dir_name in os.listdir(current_dir):
        dir_path = os.path.join(current_dir, dir_name)
        if os.path.isdir(dir_path):
            dir_iterator(dir_path)


if __name__=='__main__':
    main()
