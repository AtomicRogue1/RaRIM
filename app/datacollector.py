import feedparser
from newspaper import Article
from googlenewsdecoder import gnewsdecoder
# import nltk
# nltk.download('punkt_tab')
from misc.feed_sources import FEEDS
from database import insert_article
import json

from datetime import datetime
from email.utils import parsedate_to_datetime

companies = ["Wayve","Revolut","Deliveroo","Darktrace","Monzo","Octopus+Energy","Google","Signal+AI","H&M","Meta"]

articles = []

def parse_to_date_string(value):
    if not value:
        return None

    value = value.strip()

    try:
        # handles: 2012-06-26T03:10:27+00:00
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    try:
        # handles: Tue, 21 Jul 2026 18:48:38 +0000
        dt = parsedate_to_datetime(value)
        if dt:
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    return None

def collect_from_feed(current_latest_article_date_dt_object):
    for company in companies:
        for feed_source in FEEDS:
            print(f"Collecting from {feed_source} about {company}...")
            formatted_url = FEEDS[feed_source]
            formatted_url = formatted_url.format(company = company)
                
            fp = feedparser.parse(formatted_url)
            for entry in fp.entries:
                try:
                    # Reddit check for articles where date is None
                    fixed_date = parse_to_date_string(entry.get("published"))
                    if(fixed_date is None):
                        continue

                    # date check. if article is before date variable that means its outdated and that the DB probably has stuff on it.
                    article_date_for_check = datetime.strptime(fixed_date,"%Y-%m-%d")
                    if(article_date_for_check <= current_latest_article_date_dt_object):
                        print("Date check failed.")
                        continue

                    # If its Reddit and the title does not have company name in its title properly, its useless as some articles that come up
                    # are not related to company in the first place. This is a check for that.
                    if(feed_source == "Reddit" and company not in entry.get("title")):
                        print("Reddit check failed.")
                        continue

                    url = entry.get("link")
                    decoded = gnewsdecoder(url)

                    if(feed_source == "Google News"):
                        real_url = decoded["decoded_url"]
                    else:
                        real_url = url


                    article = Article(real_url)
                    article.download()
                    article.parse()
                    
                    articles.append({
                        "title": entry.get("title"),
                        "company": company,
                        "link": real_url,
                        "description": entry.get("title") if feed_source == "Reddit" else article.summary, # For handling the reddit title issue
                        "date": fixed_date,
                        "source": feed_source
                    })

                except Exception as e:
                    continue 

if __name__ == "__main__":
    with open("app/misc/database_params.json","r") as file:
        latest_article_date = json.load(file)["latest_article_date"]

    current_latest_article_date_dt_object = datetime.strptime(latest_article_date,"%Y-%m-%d")
    collect_from_feed(current_latest_article_date_dt_object)

    print(f"Now pushing articles into database...")
    for article in articles:

        # If I am running data collector again, I want to not repeat previously added stuff again. So I need a date I can compare articles published date with.

        if(datetime.strptime(article["date"],"%Y-%m-%d") > current_latest_article_date_dt_object):
            current_latest_article_date_dt_object = datetime.strptime(article["date"],"%Y-%m-%d")                                                       

        insert_article(article)

    print(str(len(articles)) + " articles pushed...")

    with open("app/misc/database_params.json","w") as file:
        json.dump(
            {
                "latest_article_date": current_latest_article_date_dt_object.strftime("%Y-%m-%d")
            },
            file
        )