from transformers import pipeline
from database import connect_to_db

def update_sentiment():
    analyser = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
    )
    
    print("Updating sentiment for all records...")
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("select id, title, sentiment_score from articles")

    rows = cursor.fetchall()

    for id, title, sentiment_score in rows:
        if sentiment_score:
            continue

        result = analyser(title,truncation=True,max_length=512)[0]

        label = result["label"]
        confidence = result["score"]

        if label == "negative":
            sentiment_score = -confidence

        elif label == "positive":
            sentiment_score = confidence

        else:
            sentiment_score = 0
        
        cursor.execute(
            "UPDATE articles SET sentiment_score = %s where id = %s",
            (round(sentiment_score,3), id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("Updated sentiment for all records.")