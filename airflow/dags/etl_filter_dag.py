from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "devsecops",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://library:library@postgres-service:5432/library",
)


def _connect():
    import psycopg2

    return psycopg2.connect(DATABASE_URL)


def extract_books(**context):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, author, isbn, genre, price, available FROM books"
    )
    records = cur.fetchall()
    cur.close()
    conn.close()
    # XCom: list of tuples
    context["ti"].xcom_push(key="raw_books", value=[list(r) for r in records])
    print(f"Extracted {len(records)} books")
    return len(records)


def filter_books(**context):
    records = context["ti"].xcom_pull(key="raw_books", task_ids="extract")
    filtered = [r for r in records if r[6] is True and float(r[5]) > 0]
    context["ti"].xcom_push(key="filtered_books", value=filtered)
    print(f"Filtered {len(filtered)} books (available, price > 0)")
    return len(filtered)


def load_filtered(**context):
    filtered = context["ti"].xcom_pull(key="filtered_books", task_ids="filter")
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS books_report (
            id INTEGER PRIMARY KEY,
            title VARCHAR(255),
            author VARCHAR(255),
            isbn VARCHAR(20),
            genre VARCHAR(100),
            price FLOAT,
            available BOOLEAN,
            processed_at TIMESTAMP DEFAULT NOW()
        )
        """
    )
    for book in filtered:
        cur.execute(
            """
            INSERT INTO books_report (id, title, author, isbn, genre, price, available)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                price = EXCLUDED.price,
                available = EXCLUDED.available,
                processed_at = NOW()
            """,
            book,
        )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {len(filtered)} books into books_report")


with DAG(
    dag_id="librairy_etl_filter",
    default_args=default_args,
    description="ETL livres: extract → filter → load (Ariary)",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["librairy", "etl", "books"],
) as dag:
    extract = PythonOperator(task_id="extract", python_callable=extract_books)
    filter_task = PythonOperator(task_id="filter", python_callable=filter_books)
    load = PythonOperator(task_id="load", python_callable=load_filtered)
    extract >> filter_task >> load
