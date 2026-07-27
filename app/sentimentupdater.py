from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from database import connect_to_db

analyser = SentimentIntensityAnalyzer()

def update_sentiment():
    print("Updating sentiment for all records...")
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("select id, description, sentiment_score from articles")

    rows = cursor.fetchall()

    for id, description, sentiment_score in rows:
        if sentiment_score:
            continue

        sentiment_score = analyser.polarity_scores(description)["compound"]
        cursor.execute(
            "UPDATE articles SET sentiment_score = %s where id = %s",
            (sentiment_score, id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("Updated sentiment for all records.")