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
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Target the specific blocks you identified
        articles = soup.find_all('div', class_='newsContentBlock', limit=5)
        
        news_data = []
        for art in articles:
            title_element = art.find('h1').find('a')
            title = title_element.get_text().strip()
            link = title_element['href']
            if link.startswith('/'):
                link = "https://tweakers.net" + link
            
            # Extract a small snippet of the summary text if available
            summary = art.find('p', class_='lead')
            summary_text = summary.get_text().strip()[:150] + "..." if summary else "Klik hieronder om het volledige artikel te lezen."
            
            news_data.append({'title': title, 'link': link, 'summary': summary_text})
        
        return news_data
    except Exception as e:
        print(f"Scraping error: {e}")
        return []

def send_html_email(news_list):
    sender = os.getenv("EMAIL_USER")
    receiver = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    
    # Get current date
    today = datetime.now().strftime("%d %B %Y")

    # Create the root message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🇳🇱 Dagelijkse Tech Nieuws - {today}"
    msg['From'] = f"Tweakers Bot <{sender}>"
    msg['To'] = receiver

    # --- THE HTML LAYOUT ---
    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
            <h2 style="color: #214192; border-bottom: 2px solid #214192; padding-bottom: 10px;">Goedemorgen Divyashri! ☕</h2>
            <p style="color: #555;">Hier is het belangrijkste technieuws van vandaag uit Nederland:</p>
    """

    for item in news_list:
        html_content += f"""
            <div style="margin-bottom: 25px; padding: 15px; border-left: 4px solid #214192; background: #fafafa;">
                <h3 style="margin: 0 0 10px 0;"><a href="{item['link']}" style="color: #333; text-decoration: none;">{item['title']}</a></h3>
                <p style="font-size: 14px; color: #666; margin-bottom: 15px;">{item['summary']}</p>
                <a href="{item['link']}" style="background-color: #214192; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; font-size: 12px; font-weight: bold;">LEES MEER →</a>
            </div>
        """

    html_content += """
            <p style="font-size: 10px; color: #aaa; text-align: center; margin-top: 30px;">
                Dit is een geautomatiseerd bericht van Tweakers Bot. <br>
            </p>
        </div>
    </body>
    </html>
    """

    # Attach the HTML content
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