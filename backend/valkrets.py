from connection import get_db_connection

def get_all_constituency():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT distinct constituency FROM voter ORDER BY constituency;"
        )
        constituency = cur.fetchall()
        cur.close()
        conn.close()
        return constituency
    except Exception as e:
        print(f"Error retrieving constituency: {e}")
        return []

if __name__ == "__main__":
    constituency = get_all_constituency()
    print(constituency)