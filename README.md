## Dutch Tech News Scraper
A lightweight Python-based web scraper designed to extract Dutch tech news from Tweakers.net. This tool uses Playwright to automate article collection and deliver daily email updates via GitHub Actions.

<img width="1213" height="739" alt="Email Preview" src="https://github.com/user-attachments/assets/14df4bf2-2474-4764-893b-5a22306323c9" />

## ✨ Features
- Daily Automation: Scheduled via GitHub Actions (CRON).
- Smart Scraping: Uses Playwright to bypass cookies and extract headlines, summaries, and images.
- Email Integration: Sends a formatted summary directly to the inbox.
- Lightweight: Minimal dependencies for fast execution.

## Tech Stack
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Playwright](https://img.shields.io/badge/playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-00599C?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![SMTP](https://img.shields.io/badge/SMTP-Mail-orange?style=for-the-badge&logo=gmail&logoColor=white)

## 🛠️ Installation & Usage

**1. Installation:**

Clone the repository and install the dependencies (global or venv):
```bash
git clone https://github.com/your-username/tweakers-scraper.git
cd dutch-news-scraper
pip install -r requirements.txt
playwright install chromium
```

**2. Environment Variables:**

The script looks for a .env file (or GitHub Secrets) to handle the emailing. Create a file named .env and add:
```bash
EMAIL_USER="your-email@gmail.com"
EMAIL_PASSWORD="your-app-password"
```

**3. Usage:** 

- Manual Execution:
  ```bash
  python scraper.py
  ```
- GitHub Actions:
  To automate this script, ensure that EMAIL_USER and EMAIL_PASSWORD are configured in your repository's Actions Secrets. The workflow is configured to trigger the scraper on a daily CRON schedule.
