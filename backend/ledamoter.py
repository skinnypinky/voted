from connection import get_db_connection

def get_all_ledamoter():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT l.full_name, p.parti_name, v.valkrets_name "
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