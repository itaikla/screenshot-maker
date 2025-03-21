import requests
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from openai import OpenAI

from utils import send_telegram_message

load_dotenv()

TOPICS = ["AI", "Stock Market", "Quantum Computing"]

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

def generate_content_with_openai(prompt, content, creative_mode=False):
    """Generic function to generate content using OpenAI with optional creative elements"""
    try:
        base_prompt = prompt
        if creative_mode:
            base_prompt += "\nBe creative and feel free to add metaphors, analogies, or interesting perspectives. You can include emojis, word play, or cultural references when appropriate."
        
        # TODO: Make it dynmically defined by user
        base_prompt += "\nIMPORTANT: Your response must be limited to a maximum of 4 short paragraphs."
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "system", "content": base_prompt},
                {"role": "user", "content": content}
            ],
            max_tokens=500  # Limit token length for shorter responses
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Detailed error in get_chatgpt_summary: {str(e)}")
        return "Error generating summary."

def format_message(title, content, date=None):
    """Generic function to format messages"""
    if date is None:
        date = datetime.now().strftime("%A, %B %d, %Y")
    
    message = f"*{title}*\n{date}\n\n{content}\n\n"
    return message

def send_message(message):
    """Generic function to send messages"""
    if len(message) > 4096:
        messages = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for msg in messages:
            send_telegram_message(msg)
            time.sleep(1)
    else:
        send_telegram_message(message)


def generate_and_send_news_summary():
    """News-specific implementation using generic functions"""
    articles_by_topic = {topic: fetch_news(topic) for topic in TOPICS}
    
    all_summaries = []
    for topic, articles in articles_by_topic.items():
        if articles:
            articles_text = "\n\n".join([
                f"Title: {article.get('title', '')}\nDescription: {article.get('description', '')}"
                for article in articles
            ])
            
            prompt = "Please be a news summarizer. Please provide a concise 2-3 sentence summary of the following news articles. Please translate the summary to Hebrew."
            summary = generate_content_with_openai(prompt, articles_text)
            all_summaries.append(f"📰 *Latest {topic} Summary*\n\n{summary}")
    
    full_content = "\n".join(all_summaries)
    formatted_message = format_message("Daily News Summary", full_content)
    send_message(formatted_message)

def generate_and_send_custom_content(title, prompt, content, creative=True):
    generated_content = generate_content_with_openai(prompt, content, creative_mode=creative)
    formatted_message = format_message(title, generated_content)
    send_message(formatted_message)


if __name__ == "__main__":
    generate_and_send_news_summary()
