import telegram
import asyncio
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

WHATSAPP_API_URL = "YOUR_WHATSAPP_API_URL"  # To be replaced with your actual WhatsApp API endpoint
WHATSAPP_AUTH_TOKEN = "YOUR_AUTH_TOKEN"  # Replace with your WhatsApp API auth token
RECIPIENT_NUMBER = "YOUR_WHATSAPP_NUMBER"  # Format: country code + number, e.g., "14155238886"

def send_telegram_message(message):
    async def send():
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    
    asyncio.run(send())

def send_whatsapp_message(message):
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
