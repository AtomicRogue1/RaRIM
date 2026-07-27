from database import connect_to_db

def update_time_decay():
    print("Updating time decay for all records...")
    """Update the `time_decay` value for each article row based on age."""
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
    UPDATE articles
    SET time_decay = CASE
        WHEN CURRENT_DATE - collected_at::date < 7 THEN 1.0
        WHEN CURRENT_DATE - collected_at::date < 14 THEN 0.85
        WHEN CURRENT_DATE - collected_at::date < 21 THEN 0.5
        ELSE 0.2
    END
    WHERE collected_at IS NOT NULL;
    """

    cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()

    print("Time decay updated for all records.")
