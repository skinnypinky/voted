from connection import get_db_connection

def get_all_ledamoter():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT l.intressent_id, l.full_name, p.parti_name, v.valkrets_name "
            "FROM ledamot l "
            "JOIN parti p ON l.parti_id = p.parti_id "
            "JOIN valkrets v ON l.valkrets_id = v.valkrets_id "
            "ORDER BY l.full_name;"
        )
        ledamoter = cur.fetchall()
        cur.close()
        conn.close()
        return ledamoter
    except Exception as e:
        print(f"Error retrieving ledamoter: {e}")
        return []

def get_ledamot_details(intressent_id):
    try: 
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT l.intressent_id, l.full_name, p.parti_name, v.valkrets_name, l.birth_year, l.image_url
            FROM ledamot l
            JOIN parti p ON l.parti_id = p.parti_id
            JOIN valkrets v ON l.valkrets_id = v.valkrets_id
            WHERE l.intressent_id = %(id)s;
            """,
            {"id": intressent_id}
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except Exception as e:
        print(f"Error retrieving ledamot details: {e}")
        return None

def get_ledamot_stats(intressent_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*),
                COUNT(*) FILTER (WHERE rost = 'Ja'),
                COUNT(*) FILTER (WHERE rost = 'Nej'),
                COUNT(*) FILTER (WHERE rost = 'Avstår'),
                COUNT(*) FILTER (WHERE rost = 'Frånvarande')
            FROM rost
            WHERE intressent_id = %(id)s;
            """,
            {"id": intressent_id}
        )
        rows = cur.fetchone()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error retrieving ledamot stats: {e}")
        return None

def get_ledamot_votes(intressent_id, limit=50):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT v.votering_id, v.votering_date, v.title, a.notisrubrik, 
                     u.utskott_name, r.rost
            FROM rost r
            JOIN votering v ON r.votering_id = v.votering_id
            JOIN arende a ON v.hangar_id = a.hangar_id
            LEFT JOIN utskott u ON a.utskott_id = u.utskott_id
            WHERE r.intressent_id = %(id)s
            ORDER BY v.votering_date DESC NULLS LAST
            LIMIT %(limit)s;
            """,
            {"id": intressent_id, "limit": limit}
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error retrieving ledamot votes: {e}")
        return []