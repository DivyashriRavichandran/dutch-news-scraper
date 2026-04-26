import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import smtplib
from datetime import datetime 
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

def get_tweakers_news():
    url = "https://tweakers.net/nieuws/"
    news_data = []
    
    with sync_playwright() as p:
        try:
            print(f"Launching browser to visit {url}...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 800})
            page = context.new_page()
            
            page.goto(url, wait_until="domcontentloaded")

            # --- HANDLE COOKIE WALL ---
            try:
                accept_button = page.wait_for_selector("button:has-text('Akkoord')", timeout=5000)
                if accept_button:
                    accept_button.click()
                    print("Cookie wall cleared.")
                    page.wait_for_load_state("networkidle") # Wait for news to load after click
            except:
                print("No cookie wall detected (or it's already cleared).")

            # --- SCRAPE CONTENT ---
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            news_data = []

            # Select all news block
            content_blocks = soup.find_all('div', class_='newsContentBlock')

            for block in content_blocks:
                if len(news_data) >= 5:
                    break

                # 1. Get the title and summary
                title_el = block.select_one('h1 a')
                summary_el = block.select_one('p.lead')
                img_el = block.select_one('.article img')

                if title_el:
                    title = title_el.get_text(strip=True)
                    link = title_el['href']
                    
                    if summary_el:
                        summary = summary_el.get_text(strip=True)
                    else: # fallback
                        summary = "Lees het volledige artikel op Tweakers.net."

                    image_url = ""
                    if img_el:
                        image_url = img_el.get('src') or img_el.get('data-src')

                    # Link
                    full_link = link if link.startswith('http') else f"https://tweakers.net{link}"

                    news_data.append({
                        'title': title,
                        'link': full_link,
                        'summary': (summary[:160] + "...") if len(summary) > 160 else summary,
                        'image': image_url
                    })

            browser.close()
            print(f"Successfully found {len(news_data)} articles.")
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
    <body style="font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">        
    <div style="max-width: 800px; margin: auto; background: white; padding: 25px; border-radius: 12px; border: 1px solid #ddd;">
            <h2 style="color: #214192; border-bottom: 2px solid #214192; padding-bottom: 10px; margin-top: 0;">Goedemorgen Divyashri! ☕</h2>
            <p style="color: #555;">Hier is het technieuws van vandaag uit Nederland:</p>
    """

    for item in news_list:
        if item.get("image"):
            img_html = f"""
                <div style="display: inline-block; vertical-align: top; width: 100%; max-width: 200px; margin-right: 20px; margin-bottom: 15px;">
                    <img src="{item['image']}" style="width: 100%; border-radius: 8px; display: block;">
                </div>
            """
        else:
            img_html = ""

        html_content += f"""
            <div style="margin-bottom: 25px; padding: 20px; border-left: 4px solid #214192; background: #fafafa; border-radius: 0 8px 8px 0; overflow: hidden;">
                {img_html}
                <div style="display: inline-block; vertical-align: top; width: 100%; max-width: 500px;">
                    <h3 style="margin: 0 0 10px 0;">
                        <a href="{item['link']}" style="color: #333; text-decoration: none;">{item['title']}</a>
                    </h3>
                    <p style="font-size: 14px; color: #666; margin-bottom: 15px; line-height: 1.5;">
                        {item['summary']}
                    </p>
                    <a href="{item['link']}" style="background-color: #214192; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; font-size: 12px; font-weight: 600; display: inline-block;">LEES MEER →</a>
                </div>
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