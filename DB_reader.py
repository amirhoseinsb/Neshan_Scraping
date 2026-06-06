import sqlite3

DB_PATH = 'تهران_districts.db'


TABLE_NAME = 'places'   

def get_last_id_and_count():
    try:
       
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        total_count = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT MAX(id) FROM {TABLE_NAME}")
        last_id = cursor.fetchone()[0]
        
        if last_id is None:
            print("⚠️ Table is empty!")
        else:
            print(f"✅ All Data: {total_count}")
            print(f"🔢 Last id: {last_id}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Error to database connection: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_last_id_and_count()