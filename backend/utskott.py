from connection import get_db_connection

def get_all_category():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT utskott_name FROM utskott ORDER BY utskott_name;"
        )
        category = cur.fetchall()
        cur.close()
        conn.close()
        return category
    except Exception as e:
        print(f"Error retrieving category: {e}")
        return []

if __name__ == "__main__":
    utskott = get_all_category()
    print(utskott)