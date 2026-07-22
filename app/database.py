import psycopg2
import json

latest_article_timestamp = ""

def connect_to_db():
    with open("app/misc/database_params.json","r") as file:
        latest_article_date = json.load(file)["latest_article_date"]

    return psycopg2.connect(
        host = "localhost",
        database = "RaRIM DB",
        user = "postgres",
        password = "1234",
        port = "5432"
    )

def insert_article(article):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO articles
    (title, company, link, source, description, collected_at)
    VALUES (%s,%s,%s,%s,%s,%s)
    ON CONFLICT (link) DO NOTHING;
    """

    cursor.execute(
        query,
        (
            article["title"],
            article["company"],
            article["link"],
            article["source"],
            article["description"],
            article["date"]
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

def get_latest_collected_at():
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
    SELECT MAX(collected_at)
    FROM articles;
    """

    cursor.execute(query)
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()

    return result[0]


def update_sentiment_and_confidence():
    pass
