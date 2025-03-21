import requests
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from openai import OpenAI

from utils import send_telegram_message

# Configuration
load_dotenv()

TOPICS = ["AI"]
# TOPICS = ["AI", "Stock Market", "Quantum Computing"]

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

SUMMARY_LENGTH = 4  # Number of news items per topic

client = OpenAI(api_key=OPENAI_API_KEY)

def fetch_news(topic, count=SUMMARY_LENGTH):
    url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&pageSize={count}&apiKey={NEWS_API_KEY}&language=en"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and data.get("status") == "ok":
            return data.get("articles", [])
        else:
            print(f"Error fetching news for {topic}: {data.get('message', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"Exception when fetching news for {topic}: {str(e)}")
        return []

def get_chatgpt_summary(articles):
    """Get a concise summary of articles using ChatGPT"""
    if not articles:
        return "No recent news found."
    
    articles_text = "\n\n".join([
        f"Title: {article.get('title', '')}\nDescription: {article.get('description', '')}"
        for article in articles
    ])
    
    try:
        print("Attempting to create OpenAI API call...")
        print(f"Articles text length: {len(articles_text)}")
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "system", "content": "Could you please act as a news summarizer. Please provide a concise 2-3 sentence summary of the following news articles. Please translate the summary to Hebrew."},
                {"role": "user", "content": articles_text}
            ],
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Detailed error in get_chatgpt_summary: {str(e)}")
        return "Error generating summary."

def create_summary(articles, topic):
    """Create a summary of news articles"""
    if not articles:
        return f"No recent news found for {topic}."
    
    # Get ChatGPT summary
    chatgpt_summary = get_chatgpt_summary(articles)
    
    summary = f"📰 *Latest {topic} Summary*\n\n"
    summary += f"{chatgpt_summary}\n\n"

    return summary

# TODO: Split it. Don't do 2 things in same function
def generate_and_send_news_summary():
    """Main function to generate and send news summaries"""
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    full_message = f"*Daily News Summary*\n{current_date}\n\n"
    
    for topic in TOPICS:
        articles = fetch_news(topic)
        topic_summary = create_summary(articles, topic)
        full_message += topic_summary + "\n"
    
    # Split message if too long (WhatsApp has a character limit)
    if len(full_message) > 4096:
        messages = [full_message[i:i+4000] for i in range(0, len(full_message), 4000)]
        for msg in messages:
            send_telegram_message(msg)
            time.sleep(1)
    else:
        send_telegram_message(full_message)

if __name__ == "__main__":
    generate_and_send_news_summary()
