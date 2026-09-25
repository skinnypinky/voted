import os
import json
import psycopg

def dir_iterator(current_dir, cur):
    for file_name in os.listdir(current_dir):
        file_path = os.path.join(current_dir, file_name)
        if file_path.endswith(".json"):
            parse_file(file_path, cur)

def parse_file(file_path, cur):
    with open(file_path) as f:
        json_d = json.load(f)
        votes = json_d["dokvotering"]["votering"]
        for vote in votes:
            db_add(vote, cur)

def db_add(vote, cur):
    full_name = vote["namn"]
    constituency = vote["valkrets"]

    cur.execute(
        """
        INSERT INTO voter (full_name, constituency)
        VALUES (%s, %s)
        """,
        (full_name, constituency)
        )

# populate_db
def main():
    conn = psycopg.connect(
        "postgresql://postgres:postgres@localhost:5433/voted")

    cur = conn.cursor()

    current_dir = os.path.join(os.getcwd() + "/data")
    
    for dir_name in os.listdir(current_dir):
        dir_path = os.path.join(current_dir, dir_name)
        if os.path.isdir(dir_path):
            dir_iterator(dir_path, cur)

    conn.commit()
    cur.close()
    conn.close()


if __name__=='__main__':
    main()
