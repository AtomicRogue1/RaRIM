from database import connect_to_db

def update_impact():
    print("Updating impact for all records...")
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("select id, source, sentiment_score, time_decay from articles")

    rows = cursor.fetchall()

    for id, source, sentiment_score, time_decay in rows:
        if sentiment_score:
            continue

        impact = sentiment_score * time_decay * (
            0.8 if source == "Reddit"
            else 1.0 if source == "Google News"
            else 1.2 if source == "BBC Business" or source == "TechCrunch"
            else 1.0 
        )
        cursor.execute(
            "UPDATE articles SET impact = %s where id = %s",
            (impact, id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("Updated impact for all records.")