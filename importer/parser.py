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
    valkrets_id = vote["valkretsnummer"]
    valkrets_name = vote["valkrets"]

    cur.execute(
        """
        INSERT INTO valkrets (valkrets_id, valkrets_name)
        VALUES (%s, %s)
        ON CONFLICT (valkrets_id) DO NOTHING;
        """,
        (valkrets_id, valkrets_name)
        )

# populate_db
def main():
    conn = psycopg.connect(
        "postgresql://postgres:postgres@localhost:5433/voted")

    cur = conn.cursor()

    current_dir = os.path.join(os.getcwd(), "importer", "data")
    print(current_dir)
    
    for dir_name in os.listdir(current_dir):
        dir_path = os.path.join(current_dir, dir_name)
        if os.path.isdir(dir_path):
            dir_iterator(dir_path, cur)

    conn.commit()
    cur.close()
    conn.close()


if __name__=='__main__':
    main()
