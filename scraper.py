import os
import requests
from bs4 import BeautifulSoup
import smtplib
from datetime import datetime 
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

def get_tweakers_news():
    url = "https://tweakers.net/nieuws/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = soup.select('a.fpaItemTitle', limit=5)
        
        if not articles:
            articles = soup.select('div.newsContentBlock h1 a', limit=5)
        
        news_data = []
        for art in articles:
            title = art.get_text().strip()
            link = art['href']
            
            if link.startswith('/'):
                link = "https://tweakers.net" + link
            
            parent = art.find_parent('div', class_='newsContentBlock')
            summary_text = "Klik hieronder om het volledige artikel te lezen."
            if parent:
                summary = parent.find('p', class_='lead')
                if summary:
                    summary_text = summary.get_text().strip()[:150] + "..."
            
            news_data.append({'title': title, 'link': link, 'summary': summary_text})
        
        print(f"DEBUG: Successfully found {len(news_data)} articles.")
        return news_data
        
    except Exception as e:
        print(f"Scraping error: {e}")
        return []

def send_html_email(news_list):
    sender = os.getenv("EMAIL_USER")
    receiver = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    
    if not sender or not password:
        print("Error: EMAIL_USER or EMAIL_PASSWORD not found in environment.")
        return

    today = datetime.now().strftime("%d %B %Y")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🇳🇱 Dagelijkse Tech Nieuws - {today}"
    msg['From'] = f"Tweakers Bot <{sender}>"
    msg['To'] = receiver

    html_content = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; padding: 25px; border-radius: 12px; border: 1px solid #ddd;">
            <h2 style="color: #214192; border-bottom: 2px solid #214192; padding-bottom: 10px; margin-top: 0;">Goedemorgen Divyashri! ☕</h2>
            <p style="color: #555;">Hier is de tech-update voor <strong>{today}</strong>:</p>
    """

    for item in news_list:
        html_content += f"""
            <div style="margin-bottom: 25px; padding: 15px; border-left: 4px solid #214192; background: #fafafa; border-radius: 0 8px 8px 0;">
                <h3 style="margin: 0 0 10px 0;"><a href="{item['link']}" style="color: #333; text-decoration: none;">{item['title']}</a></h3>
                <p style="font-size: 14px; color: #666; margin-bottom: 15px; line-height: 1.5;">{item['summary']}</p>
                <a href="{item['link']}" style="background-color: #214192; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; font-size: 12px; font-weight: bold; display: inline-block;">LEES MEER →</a>
            </div>
        """

    html_content += """
            <p style="font-size: 10px; color: #aaa; text-align: center; margin-top: 30px;">
                Gegenereerd door de Python News Bot.
            </p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print("Success: Email sent!")
    except Exception as e:
        print(f"Email Error: {e}")

if __name__ == "__main__":
    news = get_tweakers_news()
    if news:
        send_html_email(news)
    else:
        print("No news found to send.")