from connection import get_db_connection

def get_search_results(valkrets_id=None, utskott_id=None, q=None):
    """Search votes. Every filter is optional: None means "all"."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
<<<<<<< HEAD
        query = (
            "SELECT distinct v.votering_id, v.votering_date, u.utskott_name, vk.valkrets_name, vk.valkrets_id, v.title, a.notisrubrik, a.summary, a.url " 
            "FROM votering v " 
            "JOIN rost r ON v.votering_id = r.votering_id " 
            "JOIN valkrets vk ON r.valkrets_id = vk.valkrets_id " 
            "JOIN arende a ON v.hangar_id = a.hangar_id " 
            "JOIN utskott u ON a.utskott_id = u.utskott_id " 
            "WHERE 1=1 " 
        )
        params = []

        if valkrets_id is not None:
            query += " AND vk.valkrets_id = %s "
            params.append(valkrets_id)
        if utskott_id is not None:
            query += " AND u.utskott_id = %s "
            params.append(utskott_id)

        query += "ORDER BY v.votering_date DESC;"
        cur.execute(query, tuple(params))
        search = cur.fetchall()
=======
        cur.execute(
            """
            SELECT v.votering_id, -- row[0]
                   v.votering_date, -- row[1]
                   u.utskott_name, -- row[2]
                   a.notisrubrik, -- row[3]
                   a.title, -- row[4]
                   v.title, -- row[5]
                   a.notation, -- row[6]
                   a.riksmote, -- row[7]
                   ts_rank(a.search_vector, websearch_to_tsquery('swedish', %(q)s::text)) AS rank
            FROM votering v
            JOIN arende a       ON a.hangar_id  = v.hangar_id
            LEFT JOIN utskott u ON u.utskott_id = a.utskott_id
            WHERE (%(utskott_id)s::text IS NULL OR a.utskott_id = %(utskott_id)s::text)
              AND (%(q)s::text IS NULL
                   OR a.search_vector @@ websearch_to_tsquery('swedish', %(q)s::text))
              AND (%(valkrets_id)s::int IS NULL OR EXISTS (
                       SELECT 1 FROM rost r
                       WHERE r.votering_id = v.votering_id
                         AND r.valkrets_id = %(valkrets_id)s::int))
            ORDER BY (to_tsvector('swedish', coalesce(v.title, ''))
            @@ websearch_to_tsquery('swedish', %(q)s::text)) DESC NULLS LAST,
            rank DESC NULLS LAST,
            v.votering_date DESC;
            """,
            {"valkrets_id": valkrets_id, "utskott_id": utskott_id, "q": q},
        )
        rows = cur.fetchall()
>>>>>>> 281c81b88b9a0769573498d99365725a1ecd8dc1
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error retrieving search results: {e}")
        return []

def get_valkrets_id(valkrets_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT valkrets_id FROM valkrets WHERE valkrets_name = %s;",
            (valkrets_name,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"Error retrieving valkrets_id: {e}")
        return None

def get_utskott_id(utskott_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT utskott_id FROM utskott WHERE utskott_name = %s;",
            (utskott_name,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"Error retrieving utskott_id: {e}")
        return None

if __name__ == "__main__":
    valkrets_id = get_valkrets_id("Stockholms län")
    utskott_id = get_utskott_id("Civilutskottet")
    search_results = get_search_results(valkrets_id, utskott_id)
    print(search_results)