import os
import json
import psycopg
from riksdagen import get_document
from riksdagen import get_ledamot_image
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import local
import requests

from time import perf_counter
from collections import defaultdict
from contextlib import contextmanager

timings = defaultdict(float)
counts = defaultdict(int)

@contextmanager
def measure(name):
    start = perf_counter()
    try:
        yield
    finally:
        timings[name] += perf_counter() - start

seen_valkrets = set()
seen_parti = set()
seen_ledamot = set()
seen_utskott = set()
seen_arende = set()
seen_votering = set()

document_cache = {}
image_cache = {}
thread_state = local()

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

with open(os.path.join(DATA_DIR, "parties.json")) as f:
    parties = json.load(f)["parties"]

with open(os.path.join(DATA_DIR, "utskott.json")) as f:
    committees = json.load(f)["committees"]

def get_document_cached(notation, riksmote):
    key = (notation, riksmote)

    counts["document_cache_hits"] += 1

    return document_cache[key]

def collect_api_keys():
    document_keys = set()
    member_ids = set()

    with measure("key_scan"):
        for dir_name in sorted(os.listdir(DATA_DIR)):
            dir_path = os.path.join(DATA_DIR, dir_name)

            if not os.path.isdir(dir_path):
                continue

            for file_name in sorted(os.listdir(dir_path)):
                if not file_name.endswith(".json"):
                    continue

                file_path = os.path.join(dir_path, file_name)

                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                votes = data["dokvotering"]["votering"]

                if isinstance(votes, dict):
                    votes = [votes]

                for vote in votes:
                    member_ids.add(vote["intressent_id"])

                    beteckning = vote["beteckning"]

                    if beteckning and beteckning[0].isalpha():
                        document_keys.add((
                            beteckning,
                            vote["rm"]
                        ))

    return document_keys, member_ids

def fetch_document(key):
    notation, riksmote = key

    start = perf_counter()

    result = get_document(
        notation,
        riksmote,
        get_worker_session()
    )

    elapsed = perf_counter() - start

    return result, elapsed


def fetch_image(member_id):
    start = perf_counter()

    result = get_ledamot_image(
        member_id,
        get_worker_session()
    )

    elapsed = perf_counter() - start

    return result, elapsed

def prefetch_api_data():
    document_keys, member_ids = collect_api_keys()

    with measure("prefetch_wall"):
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {}

            for key in document_keys:
                future = executor.submit(fetch_document, key)
                futures[future] = ("document", key)

            for member_id in member_ids:
                future = executor.submit(fetch_image, member_id)
                futures[future] = ("image", member_id)

            for future in as_completed(futures):
                kind, key = futures[future]

                result, elapsed = future.result()

                if kind == "document":
                    document_cache[key] = result
                    timings["document_api"] += elapsed
                    counts["document_requests"] += 1

                else:
                    image_cache[key] = result
                    timings["image_api"] += elapsed
                    counts["image_requests"] += 1

def dir_iterator(current_dir, cur):
    batch = []

    for file_name in sorted(os.listdir(current_dir)):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(current_dir, file_name)

        votes = parse_file(file_path, cur)
        batch.extend(votes)

        if len(batch) >= 10_000:
            add_rost(batch, cur)
            batch.clear()

    if batch:
        add_rost(batch, cur)

def parse_file(file_path, cur):
    with measure("json_parsing"):
        with open(file_path, encoding="utf-8") as f:
            json_d = json.load(f)

    votes = json_d["dokvotering"]["votering"]

    if isinstance(votes, dict):
        votes = [votes]

    with measure("metadata_total"):
        for vote in votes:
            populate_db(vote, cur)

    counts["files"] += 1

    return votes

def add_valkrets(vote, cur):
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

def add_parti_id(vote, cur):
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

def add_ledamot(vote, cur):
    ledamot = vote["intressent_id"]
    
    if ledamot not in seen_ledamot:
        image_url = image_cache[ledamot]

        cur.execute(
            """
            INSERT INTO ledamot (intressent_id, full_name, valkrets_id, parti_id, birth_year, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (intressent_id) DO NOTHING;
            """,
            (vote["intressent_id"], vote["namn"],vote["valkretsnummer"],vote["parti"], vote["fodd"], image_url)
            )
        seen_ledamot.add(ledamot)

def add_utskott(utskott_id, cur):
    if utskott_id not in seen_utskott:
        utskott_name = committees.get(
            utskott_id,
            "Okänt eller ej klassificerat"
        )
    
        cur.execute(
            """
            INSERT INTO utskott (utskott_id, utskott_name)
            VALUES (%s, %s)
            ON CONFLICT (utskott_id) DO NOTHING;
            """,
            (utskott_id, utskott_name)
            )
        seen_utskott.add(utskott_id)

def add_arende(vote, cur):
    arende_id = vote["hangar_id"]
    beteckning = vote["beteckning"]

    if arende_id not in seen_arende:
        title = "Okänt ärende"
        notisrubrik = None
        summary = None
        organ = None
        url = None
        utskott_id = None

        if beteckning and beteckning[0].isalpha():
            doc = get_document_cached(beteckning, vote["rm"])

            if doc:
                title = doc["title"]
                notisrubrik = doc["notisrubrik"]
                summary = doc["summary"]
                organ = doc["organ"]

                if not organ or organ == "-":
                    utskott_id = None
                else:
                    utskott_id = organ
                    add_utskott(utskott_id, cur)

                url = doc["url"]


        cur.execute(
            """
            INSERT INTO arende
            (hangar_id, notation, riksmote, title, utskott_id, notisrubrik, summary, url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
                url
            )
        )

        seen_arende.add(arende_id)

def add_votering(vote, cur):
    votering_id = vote["votering_id"]
    beteckning = vote["beteckning"]

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
            SET title = COALESCE(EXCLUDED.title, votering.title);
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

def add_rost(votes, cur):
    with measure("staging_truncate"):
        cur.execute("TRUNCATE staging_rost")

    with measure("copy"):
        with cur.copy("""
            COPY staging_rost (
                votering_id,
                intressent_id,
                rost,
                parti_id,
                valkrets_id
            )
            FROM STDIN
        """) as copy:

            for vote in votes:
                copy.write_row((
                    vote["votering_id"],
                    vote["intressent_id"],
                    vote["rost"],
                    vote["parti"],
                    vote["valkretsnummer"]
                ))

    with measure("merge"):
        cur.execute("""
            INSERT INTO rost (
                votering_id,
                intressent_id,
                rost,
                parti_id,
                valkrets_id
            )
            SELECT
                votering_id,
                intressent_id,
                rost,
                parti_id,
                valkrets_id
            FROM staging_rost
            WHERE TRUE
            ON CONFLICT (votering_id, intressent_id)
            DO NOTHING
        """)

    counts["batches"] += 1
    counts["votes"] += len(votes)

def populate_db(vote, cur):
    add_valkrets(vote, cur)
    add_parti_id(vote, cur)
    add_ledamot(vote, cur)
    add_arende(vote, cur)
    add_votering(vote, cur)
    
def print_profile():
    total = timings["import_total"]

    bulk = (
        timings["staging_truncate"]
        + timings["copy"]
        + timings["merge"]
    )

    accounted = (
        timings["key_scan"]
        + timings["prefetch_wall"]
        + timings["json_parsing"]
        + timings["metadata_total"]
        + bulk
    )

    other = total - accounted

    print("\n========== IMPORT PROFILE ==========")

    print(f"Total importer time:  {total:.2f}s")
    print()
    print(f"API key scan:         {timings['key_scan']:.2f}s")
    print(f"API prefetch (wall):  {timings['prefetch_wall']:.2f}s")
    print(f"Document API (sum):   {timings['document_api']:.2f}s")
    print(f"MP image API (sum):   {timings['image_api']:.2f}s")
    print(f"Metadata processing:  {timings['metadata_total']:.2f}s")
    print(f"JSON parsing:         {timings['json_parsing']:.2f}s")
    print(f"Staging TRUNCATE:     {timings['staging_truncate']:.2f}s")
    print(f"COPY:                 {timings['copy']:.2f}s")
    print(f"INSERT from staging:  {timings['merge']:.2f}s")
    print(f"Other / commits:      {other:.2f}s")

    print()
    print(f"API prefetch share:   {timings['prefetch_wall'] / total * 100:.1f}%")
    print(f"Bulk DB share:        {bulk / total * 100:.1f}%")

    print()
    print(f"Document requests:    {counts['document_requests']}")
    print(f"Image requests:       {counts['image_requests']}")
    print(f"JSON files:           {counts['files']}")
    print(f"COPY batches:         {counts['batches']}")
    print(f"Votes processed:      {counts['votes']}")

    print("====================================\n")

def get_worker_session():
    if not hasattr(thread_state, "session"):
        thread_state.session = requests.Session()

    return thread_state.session

def main():
    with measure("import_total"):

        prefetch_api_data()

        with psycopg.connect(
            os.environ["DATABASE_URL"]
        ) as conn:

            with conn.cursor() as cur:

                cur.execute("""
                    CREATE TEMP TABLE staging_rost AS
                    SELECT
                        votering_id,
                        intressent_id,
                        rost,
                        parti_id,
                        valkrets_id
                    FROM rost
                    WITH NO DATA
                """)

                requests.Session()

                for dir_name in sorted(os.listdir(DATA_DIR)):
                    dir_path = os.path.join(DATA_DIR, dir_name)

                    if os.path.isdir(dir_path):
                        dir_iterator(dir_path, cur)
                        conn.commit()

    print_profile()


if __name__ == "__main__":
    main()