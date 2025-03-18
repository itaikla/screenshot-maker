import requests
import json
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# Configuration
load_dotenv()

# TOPICS = ["AI", "Technology", "Science", "Business"]
TOPICS = ["Israel"]
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
WHATSAPP_API_URL = "YOUR_WHATSAPP_API_URL"  # To be replaced with your actual WhatsApp API endpoint
WHATSAPP_AUTH_TOKEN = "YOUR_AUTH_TOKEN"  # Replace with your WhatsApp API auth token
RECIPIENT_NUMBER = "YOUR_WHATSAPP_NUMBER"  # Format: country code + number, e.g., "14155238886"
SUMMARY_LENGTH = 3  # Number of news items per topic

def fetch_news(topic, count=SUMMARY_LENGTH):
    print(NEWS_API_KEY)
    """Fetch news for a specific topic using News API"""
    url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&pageSize={count}&apiKey={NEWS_API_KEY}"
    
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

def create_summary(articles, topic):
    """Create a summary of news articles"""
    if not articles:
        return f"No recent news found for {topic}."
    
    summary = f"📰 *Latest {topic} News*\n\n"
    
    for i, article in enumerate(articles[:SUMMARY_LENGTH], 1):
        title = article.get("title", "No title")
        source = article.get("source", {}).get("name", "Unknown source")
        published = article.get("publishedAt", "")
        url = article.get("url", "")
        
        # Format the date if available
        if published:
            try:
                pub_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
                date_str = pub_date.strftime("%b %d, %Y")
            except:
                date_str = published
        else:
            date_str = "Recent"
        
        summary += f"*{i}. {title}*\n"
        summary += f"Source: {source} | {date_str}\n"
        summary += f"Read more: {url}\n\n"
    
    return summary

def send_whatsapp_message(message):
    """Send a message via WhatsApp Business API"""
    headers = {
        'Authorization': f'Bearer {WHATSAPP_AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": RECIPIENT_NUMBER,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("Message sent successfully!")
            return True
        else:
            print(f"Failed to send message: {response.text}")
            return False
    except Exception as e:
        print(f"Exception when sending WhatsApp message: {str(e)}")
        return False

def generate_and_send_news_summary():
    """Main function to generate and send news summaries"""
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    full_message = f"*Daily News Summary*\n{current_date}\n\n"
    
    for topic in TOPICS:
        articles = fetch_news(topic)
        topic_summary = create_summary(articles, topic)
        full_message += topic_summary + "\n"
    
    # Add footer
    full_message += "Generated by your News Summary Service"
    
    # Split message if too long (WhatsApp has a character limit)
    if len(full_message) > 4096:
        messages = [full_message[i:i+4000] for i in range(0, len(full_message), 4000)]
        print(messages)
        for msg in messages:
            send_whatsapp_message(msg)
            time.sleep(1)  # Pause between messages
    else:
        print(full_message)
        send_whatsapp_message(full_message)

if __name__ == "__main__":
    generate_and_send_news_summary()
