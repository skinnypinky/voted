from connection import get_db_connection

def get_search_results(valkrets_id, utskott_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT v.hangar_id " \
            "FROM votering v " \
            "JOIN rost r ON v.votering_id = r.votering_id " \
            "JOIN valkrets vk ON r.valkrets_id = vk.valkrets_id " \
            "JOIN arende a ON v.hangar_id = a.hangar_id " \
            "JOIN utskott u ON a.utskott_id = u.utskott_id " \
            "WHERE r.valkrets_id = %s " \
            "AND a.utskott_id = %s;",
            (valkrets_id, utskott_id)
        )
        search = cur.fetchall()
        cur.close()
        conn.close()
        return search
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
        valkrets_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        return valkrets_id
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
        utskott_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        return utskott_id
    except Exception as e:
        print(f"Error retrieving utskott_id: {e}")
        return None

if __name__ == "__main__":
    valkrets_id = get_valkrets_id("Stockholms län")
    utskott_id = get_utskott_id("Civilutskottet")
    search_results = get_search_results(valkrets_id, utskott_id)
    print(search_results)