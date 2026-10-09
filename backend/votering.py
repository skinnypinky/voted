from connection import get_db_connection

def get_all_voting(votering_id, valkrets_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT rost, COUNT(*) " \
            "FROM rost " \
            "WHERE votering_id = %s "
            "AND valkrets_id = %s "
            "GROUP BY rost;",
            (votering_id, valkrets_id)
        )
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
        cur.execute(
            "SELECT l.full_name, p.parti_name, r.rost " \
            "FROM rost r " \
            "JOIN ledamot l ON r.intressent_id = l.intressent_id " \
            "JOIN parti p ON l.parti_id = p.parti_id " \
            "WHERE r.votering_id = %s " \
            "AND r.valkrets_id = %s;",
            (votering_id, valkrets_id)
        )
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