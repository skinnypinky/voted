import os
import json
import psycopg
from riksdagen import get_document

seen_valkrets = set()
seen_parti = set()
seen_ledamot = set()
seen_utskott = set()
weird_ids = set()
seen_arende = set()
seen_votering = set()

document_cache = {}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

with open(os.path.join(DATA_DIR, "parties.json")) as f:
    parties = json.load(f)["parties"]

with open(os.path.join(DATA_DIR, "utskott.json")) as f:
    committees = json.load(f)["committees"]

def get_document_cached(notation, riksmote):
    key = (notation, riksmote)

    if key not in document_cache:
        document_cache[key] = get_document(notation, riksmote)

    return document_cache[key]

def dir_iterator(current_dir, cur, conn):
    for file_name in os.listdir(current_dir):
        file_path = os.path.join(current_dir, file_name)
        if file_path.endswith(".json"):
            parse_file(file_path, cur)
            conn.commit()

def parse_file(file_path, cur):
    with open(file_path) as f:
        json_d = json.load(f)
        votes = json_d["dokvotering"]["votering"]
        for vote in votes:
            db_add(vote, cur)

def db_add(vote, cur):
    valkrets_id = vote["valkretsnummer"]

    if valkrets_id not in seen_valkrets:
        cur.execute(
            """
            INSERT INTO valkrets (valkrets_id, valkrets_name)
            VALUES (%s, %s)
            ON CONFLICT (valkrets_id) DO NOTHING;
            """,
            (valkrets_id, vote["valkrets"])
            )
        seen_valkrets.add(valkrets_id)

    parti_id = vote["parti"]
    if parti_id not in seen_parti:
        cur.execute(
            """
            INSERT INTO parti (parti_id, parti_name)
            VALUES (%s, %s)
            ON CONFLICT (parti_id) DO NOTHING;
            """,
            (parti_id, parties[parti_id])
            )
        seen_parti.add(parti_id)
        

    ledamot = vote["intressent_id"]
    if ledamot not in seen_ledamot:
        cur.execute(
            """
            INSERT INTO ledamot (intressent_id, full_name, valkrets_id, parti_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (intressent_id) DO NOTHING;
            """,
            (vote["intressent_id"], vote["namn"],vote["valkretsnummer"],vote["parti"])
            )
        seen_ledamot.add(ledamot)


    beteckning = vote["beteckning"]

    if beteckning and beteckning[0].isalpha():
        utskott_id = beteckning.rstrip("0123456789")

        if utskott_id not in seen_utskott:
            try:
                utskott_name = committees[utskott_id]
            except KeyError:
                utskott_name = "Okänt eller ej klassificerat"

            cur.execute(
                """
                INSERT INTO utskott (utskott_id, utskott_name)
                VALUES (%s, %s)
                ON CONFLICT (utskott_id) DO NOTHING;
                """,
                (utskott_id, utskott_name)
                )
            seen_utskott.add(utskott_id)

    else:
        # if the id is in the wrong format it is a revote or some other weird shit
        # dont know how to handle that atm
        utskott_id = None
        utskott_name = None

        if beteckning not in weird_ids:
            print("Unknown designation:", vote["beteckning"])
            weird_ids.add(beteckning)


    arende_id = vote["hangar_id"]

    if arende_id not in seen_arende:
        notisrubrik = None
        summary = None
        organ = None
        url = None

        if beteckning and beteckning[0].isalpha():
            doc = get_document_cached(vote["beteckning"], vote["rm"])

            if doc:
                title = doc["title"]
                notisrubrik = doc["notisrubrik"]
                summary = doc["summary"]
                organ = doc["organ"]
                url = doc["url"]
            else:
                title = "Okänt ärende"

        else:
            title = "Okänt ärende"

            if beteckning not in weird_ids:
                print("Unknown designation:", beteckning)
                weird_ids.add(beteckning)

        cur.execute(
            """
            INSERT INTO arende
            (hangar_id, notation, riksmote, title, utskott_id, notisrubrik, summary, organ, url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (hangar_id) DO NOTHING;
            """,
            (
                arende_id,
                vote["beteckning"],
                vote["rm"],
                title,
                utskott_id,
                notisrubrik,
                summary,
                organ,
                url
            )
        )

        seen_arende.add(arende_id)


    votering_id = vote["votering_id"]

    if votering_id not in seen_votering:

        votering_title = None

        if beteckning and beteckning[0].isalpha():
            doc = get_document_cached(beteckning, vote["rm"])

            if doc:
                votering_title = doc["votering_titles"].get(votering_id.upper())

        cur.execute(
            """
            INSERT INTO votering
                (votering_id, hangar_id, point, title, votering_type, votering_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (votering_id) DO UPDATE
            SET title = EXCLUDED.title;
            """,
            (
                votering_id,
                vote["hangar_id"],
                vote["punkt"],
                votering_title,
                vote["votering"],
                vote["datum"]
            )
        )

        seen_votering.add(votering_id)


    cur.execute(
        """
        INSERT INTO rost (votering_id, intressent_id, rost, parti_id, valkrets_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (votering_id, intressent_id) DO NOTHING;
        """,
        (vote["votering_id"], vote["intressent_id"], vote["rost"], vote["parti"],vote["valkretsnummer"])
        )

# populate_db
def main():
    conn = psycopg.connect(
        "postgresql://postgres:postgres@localhost:5433/voted")

    cur = conn.cursor()
    
    for dir_name in os.listdir(DATA_DIR):
        dir_path = os.path.join(DATA_DIR, dir_name)
        if os.path.isdir(dir_path):
            dir_iterator(dir_path, cur, conn)

    conn.commit()
    cur.close()
    conn.close()

if __name__=='__main__':
    main()
