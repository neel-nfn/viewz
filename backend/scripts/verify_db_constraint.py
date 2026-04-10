import os

import psycopg


def main() -> None:
    dsn = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    print(f"Connecting to: {dsn}")
    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute("select current_database(), inet_server_addr(), inet_server_port();")
            print("Connected:", cur.fetchone())

            cur.execute("select table_schema, table_name from information_schema.tables where table_name='youtube_channels';")
            print("Table check:", cur.fetchall())

            cur.execute("select column_name from information_schema.columns where table_name='youtube_channels';")
            cols = [r[0] for r in cur.fetchall()]
            print("Columns:", cols)

            cur.execute("select conname from pg_constraint where conrelid='youtube_channels'::regclass;")
            constraints = [r[0] for r in cur.fetchall()]
            print("Constraints:", constraints)
    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    main()


