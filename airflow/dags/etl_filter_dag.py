"""
DAG ETL : extraction des livres depuis PostgreSQL, filtrage, chargement.
Pipeline : Machine -> CRUD -> GitHub -> ArgoCD -> K8S -> Airflow Job -> ETL (filtre)
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    "owner": "devsecops",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def extract_books(**context):
    """Extraction des livres depuis PostgreSQL."""
    hook = PostgresHook(postgres_conn_id="library_postgres")
    records = hook.get_records(
        "SELECT id, title, author, isbn, genre, price, available FROM books"
    )
    context["ti"].xcom_push(key="raw_books", value=records)
    print(f"Extracted {len(records)} books")
    return len(records)


def filter_books(**context):
    """Filtre : livres disponibles avec prix > 0."""
    records = context["ti"].xcom_pull(key="raw_books", task_ids="extract")
    filtered = [
        r for r in records if r[6] is True and r[5] > 0  # available=True, price>0
    ]
    context["ti"].xcom_push(key="filtered_books", value=filtered)
    print(f"Filtered {len(filtered)} books (available, price > 0)")
    return len(filtered)


def load_filtered(**context):
    """Chargement des livres filtrés dans une table de reporting."""
    filtered = context["ti"].xcom_pull(key="filtered_books", task_ids="filter")
    hook = PostgresHook(postgres_conn_id="library_postgres")

    hook.run(
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
        hook.run(
            """
            INSERT INTO books_report (id, title, author, isbn, genre, price, available)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                price = EXCLUDED.price,
                available = EXCLUDED.available,
                processed_at = NOW()
            """,
            parameters=book,
        )

    print(f"Loaded {len(filtered)} books into books_report")


with DAG(
    dag_id="books_etl_filter",
    default_args=default_args,
    description="ETL pipeline: extract books, filter available, load report",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["books", "etl", "devsecops"],
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_books,
    )

    filter_task = PythonOperator(
        task_id="filter",
        python_callable=filter_books,
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load_filtered,
    )

    extract >> filter_task >> load
