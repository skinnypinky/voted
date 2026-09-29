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

def party_name(party_abbreviation):
    with open(os.path.join(os.getcwd(), "importer", "data", "parties.json")) as f:
        parties = json.load(f)

    return parties["parties"][party_abbreviation]

def db_add(vote, cur):
    cur.execute(
        """
        INSERT INTO valkrets (valkrets_id, valkrets_name)
        VALUES (%s, %s)
        ON CONFLICT (valkrets_id) DO NOTHING;
        """,
        (vote["valkretsnummer"], vote["valkrets"])
        )

    cur.execute(
        """
        INSERT INTO parti (parti_id, parti_name)
        VALUES (%s, %s)
        ON CONFLICT (parti_id) DO NOTHING;
        """,
        (vote["parti"], party_name(vote["parti"]))
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
