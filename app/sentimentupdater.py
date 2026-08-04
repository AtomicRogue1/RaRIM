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
        # if sentiment_score:
        #     continue

        results = analyser(
            title,
            truncation=True,
            max_length=512,
            top_k=3
        )

        positive_score = 0
        negative_score = 0
        neutral_score = 0

        for result in results:

            label = result["label"]
            score = result["score"]

            if label == "positive":
                positive_score = score

            elif label == "negative":
                negative_score = score

            elif label == "neutral":
                neutral_score = score

        highest_label = max(
            {
                "positive": positive_score,
                "negative": negative_score,
                "neutral": neutral_score
            },
            key=lambda x: {
                "positive": positive_score,
                "negative": negative_score,
                "neutral": neutral_score
            }[x]
        )

        if highest_label == "positive":
            sentiment_score = positive_score

        elif highest_label == "negative":
            sentiment_score = -negative_score

        else:
            sentiment_score = positive_score - negative_score
        
        cursor.execute(
            "UPDATE articles SET sentiment_score = %s where id = %s",
            (round(sentiment_score,3), id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("Updated sentiment for all records.")

# update_sentiment()