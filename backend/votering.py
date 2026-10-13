from connection import get_db_connection

def get_all_voting(votering_id, valkrets_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = (
            "SELECT rost, COUNT(*) " \
            "FROM rost " \
            "WHERE votering_id = %s "
        )
        params = [votering_id]
        if valkrets_id is not None:
            query += " AND valkrets_id = %s "
            params.append(valkrets_id)

        query += "GROUP BY rost;"
        cur.execute(query, tuple(params))
        voting = cur.fetchall()
        cur.close()
        conn.close()
        return voting
    except Exception as e:
        print(f"Error retrieving voting: {e}")
        return []

def get_specific_voting(votering_id, valkrets_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = (
            "SELECT l.full_name, p.parti_name, r.rost " \
            "FROM rost r " \
            "JOIN ledamot l ON r.intressent_id = l.intressent_id " \
            "JOIN parti p ON l.parti_id = p.parti_id " \
            "WHERE r.votering_id = %s " \
        )
        params = [votering_id]
        if valkrets_id is not None:
            query += " AND r.valkrets_id = %s ORDER BY l.full_name;"
            params.append(valkrets_id)
        else:
            query += "ORDER BY l.full_name LIMIT 500;"
        cur.execute(query, tuple(params))
        voting = cur.fetchall()
        cur.close()
        conn.close()
        return voting
    except Exception as e:
        print(f"Error retrieving voting: {e}")
        return []

if __name__ == "__main__":
    voting = get_all_voting("14B90381-2745-4F7F-9A08-E6AF4F8B493C", "28")
    print(voting)