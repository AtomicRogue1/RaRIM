from database import connect_to_db
import os

def classify_with_llm(title, risk_categories):
    if not title:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    client = OpenAI(api_key=api_key)

    prompt = (
        "You are a risk classification assistant. "
        "Classify the article title into exactly one of these categories: "
        + ", ".join(risk_categories)
        + ". Return only the category name. The title is : "
        + title
    )

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": "You classify article titles into one of the provided risk categories.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        category = response.choices[0].message.content.strip()
        if category in risk_categories:
            return category
    except Exception as e:
        print(e)
        return None

    print("None")
    return None


def classify_risk_category(title, risk_categories):
    llm_category = classify_with_llm(title, risk_categories)
    if llm_category:
        return llm_category

    title_lower = (title or "").lower()

    keyword_map = {
        "Financial Risks": ["finance", "bank", "debt", "revenue", "stock", "payment", "market"],
        "Product Risks": ["product", "defect", "safety", "recall", "quality", "failure"],
        "Legal Risks": ["law", "legal", "lawsuit", "regulation", "compliance", "court"],
        "Reputational Risks": ["brand", "scandal", "reputation", "public", "boycott", "controversy"],
        "Governance Risks": ["governance", "board", "corruption", "ethics", "fraud", "misconduct"],
        "Political Unrest": ["protest", "riot", "election", "war", "strike", "unrest", "politics"],
    }

    for category, keywords in keyword_map.items():
        if any(keyword in title_lower for keyword in keywords):
            return category

    return None

def update_risk_category():
    risk_categories = ["Financial Risks","Product Risks","Legal Risks","Reputational Risks","Governance Risks","Political Unrest"]
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("select id, title, risk_category from articles")
    rows = cursor.fetchall()

    for id, title, risk_category in rows:
        if risk_category:
            continue

        new_risk_category = classify_risk_category(title, risk_categories)

        cursor.execute(
            "UPDATE articles SET risk_category = %s where id = %s",
            (new_risk_category,id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("Updated risk categories.")