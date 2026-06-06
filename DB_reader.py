import sqlite3

# آدرس فایل دیتابیس خودت رو اینجا بزار (مثال: 'my_database.db')
DB_PATH = 'تهران_districts.db'  # <--- اسم فایل دیتابیست رو عوض کن

# اسم جدولت رو اینجا بزن (مثال: 'users' یا 'products')
TABLE_NAME = 'places'  # <--- اسم جدول رو عوض کن

def get_last_id_and_count():
    try:
        # اتصال به دیتابیس
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. تعداد کل رکوردها
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        total_count = cursor.fetchone()[0]
        
        # 2. آخرین id (بزرگترین مقدار ستون id)
        cursor.execute(f"SELECT MAX(id) FROM {TABLE_NAME}")
        last_id = cursor.fetchone()[0]
        
        if last_id is None:
            print("⚠️ جدول خالی است!")
        else:
            print(f"✅ تعداد کل دیتاها: {total_count}")
            print(f"🔢 آخرین ID: {last_id}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ خطا در اتصال به دیتابیس: {e}")
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    get_last_id_and_count()