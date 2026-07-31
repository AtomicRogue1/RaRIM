from database import connect_to_db

def update_impact():
    print("Updating impact for all records...")
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("select id, source, sentiment_score, time_decay, impact from articles")
    rows = cursor.fetchall()

    for id, source, sentiment_score, time_decay, impact in rows:
        if impact:
            continue

        sentiment_value = float(sentiment_score or 0)
        time_decay_value = float(time_decay or 0)

        multiplier = (
            0.8 if source == "Reddit"
            else 1.0 if source == "Google News"
            else 1.2 if source == "BBC Business" or source == "TechCrunch"
            else 1.0
        )

        impact = sentiment_value * time_decay_value * multiplier
        impact = round(impact, 3)

        cursor.execute(
            "UPDATE articles SET impact = %s where id = %s",
            (impact, id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("Updated impact for all records.")