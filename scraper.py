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
    <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f4f3; margin: 0; padding: 20px;">        
        <div style="max-width: 750px; margin: auto; background-color: #fcfbfa; padding: 30px; border-radius: 16px; border: 1px solid #e7e5e4; box-shadow: 0 4px 20px -2px rgba(28,25,23,0.05);">
            <h2 style="color: #1c1917; border-bottom: 2px solid #e05600; padding-bottom: 12px; margin-top: 0; font-size: 24px; font-weight: 500; letter-spacing: -0.02em;">Goedemorgen Divyashri! ☕</h2>
            <p style="color: #44403c; font-size: 15px; margin-bottom: 25px;">Hier is het technieuws van vandaag uit Nederland:</p>
    """

    for item in news_list:
        if item.get("image"):
            img_html = f"""
                <div style="display: inline-block; vertical-align: top; width: 100%; max-width: 180px; margin-right: 24px; margin-bottom: 16px;">
                    <img src="{item['image']}" style="width: 100%; max-height:400px; border-radius: 8px; display: block; object-fit: cover;">
                </div>
            """
        else:
            img_html = ""

        html_content += f"""
            <div style="margin-bottom: 30px; padding-bottom: 25px; border-bottom: 1px solid #e7e5e4; overflow: hidden;">
                {img_html}
                <div style="display: inline-block; vertical-align: top; width: 100%; max-width: 480px;">
                    <h3 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 500; line-height: 1.4; letter-spacing: -0.01em;">
                        <a href="{item['link']}" style="color: #1c1917; text-decoration: none;">{item['title']}</a>
                    </h3>
                    <p style="font-family: Georgia, Cambria, 'Times New Roman', Times, serif; font-size: 14px; color: #57534e; margin-bottom: 16px; line-height: 1.6;">
                        {item['summary']}
                    </p>
                    <a href="{item['link']}" style="color: #e05600; text-decoration: none; font-size: 13px; font-weight: 600; letter-spacing: 0.05em; display: inline-block;">LEES MEER <span style="font-family: system-ui;">→</span></a>
                </div>
            </div>
        """

    html_content += """
                <p style="font-size: 11px; color: #a8a29e; text-align: center; margin-top: 30px; letter-spacing: 0.02em;">
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