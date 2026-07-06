import os
import asyncio
import mysql.connector
import asyncpg
from dotenv import load_dotenv

load_dotenv()

# Configuration
MYSQL_CONFIG = {
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'database': os.getenv('MYSQL_DATABASE', 'legacy_db'),
}

PG_DSN = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:pass@localhost/adapt_engine')

async def migrate_data():
    print("🚀 Starting Migration: MySQL -> PostgreSQL")
    
    # 1. Connect to MySQL
    try:
        mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor(dictionary=True)
    except Exception as e:
        print(f"❌ MySQL Connection Error: {e}")
        return

    # 2. Connect to PostgreSQL
    try:
        pg_conn = await asyncpg.connect(PG_DSN)
    except Exception as e:
        print(f"❌ PostgreSQL Connection Error: {e}")
        return

    try:
        # Extract legacy index data
        # Assuming old table name was 'index'
        mysql_cursor.execute("SELECT url, title, description, content FROM `index`")
        rows = mysql_cursor.fetchall()
        print(f"📦 Found {len(rows)} records to migrate...")

        # Batch insert into Postgres
        # We use a simple loop here, but for 1M+ records, copy_records_to_table is better
        for row in rows:
            await pg_conn.execute(
                """
                INSERT INTO page_index (id, url, title, description, content, url_hash) 
                VALUES (gen_random_uuid(), $1, $2, $3, $4, encode(digest($1, 'sha256'), 'hex'))
                ON CONFLICT (url) DO NOTHING
                """,
                row['url'], row['title'], row['description'], row['content']
            )
        
        print("✅ Migration completed successfully.")

    except Exception as e:
        print(f"❌ Migration Error: {e}")
    finally:
        mysql_cursor.close()
        mysql_conn.close()
        await pg_conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_data())
