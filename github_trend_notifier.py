import os
import requests
import json
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from openai import OpenAI
import resend

# ─────────────────────────────────────────────
# ✅ Production Configuration
# ─────────────────────────────────────────────
CHINA_TZ = timezone(timedelta(hours=8))
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "re_Mj3rvjXM_NmerdtHrqeiPXq9oQUJqtsLa")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-da42ff2bc508463a97578370d4283549")

resend.api_key = RESEND_API_KEY
FROM_EMAIL = "TrendBot<system@cccat520.fun>"
TO_EMAIL = "1321953481@qq.com"

def log(msg):
    timestamp = datetime.now(CHINA_TZ).strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}", flush=True)

# 1. Scrape GitHub Trending
def fetch_github_trending():
    log("🛰️ Scraping GitHub Trending repositories...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = "https://github.com/trending"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            log(f"❌ Failed to fetch trending page: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        repos = []
        
        for article in soup.find_all('article', class_='Box-row'):
            # Title
            title_tag = article.find('h2', class_='h3')
            name = title_tag.get_text(strip=True).replace(' ', '') if title_tag else "N/A"
            link = "https://github.com" + title_tag.find('a')['href'] if title_tag and title_tag.find('a') else "N/A"
            
            # Description
            desc_tag = article.find('p', class_='col-9')
            description = desc_tag.get_text(strip=True) if desc_tag else "No description provided."
            
            # Stars & Language
            meta = article.find('div', class_='f6')
            stars = "N/A"
            lang = "N/A"
            if meta:
                stars_tag = meta.find('a', href=True, class_='Link--muted')
                if stars_tag:
                    stars = stars_tag.get_text(strip=True)
                
                lang_tag = meta.find('span', itemprop='programmingLanguage')
                if lang_tag:
                    lang = lang_tag.get_text(strip=True)
            
            repos.append({
                "name": name,
                "link": link,
                "description": description,
                "stars": stars,
                "language": lang
            })
            
            if len(repos) >= 10:  # Top 10
                break
                
        return repos
    except Exception as e:
        log(f"❌ Scraping error: {e}")
        return None

# 2. LLM Summarization and HTML Rendering
def get_ai_summary(repos):
    if not repos: return None, "⚠️ Failed to fetch trending projects."
    
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    
    now = datetime.now(CHINA_TZ)
    date_str = now.strftime('%Y-%m-%d')
    
    system_prompt = """你是一个服务于顶级工程师团队的技术侦查员（Tech Scout）。
你的任务是分析 GitHub 今日趋势项目，并生成一份简洁、专业且极具美感的中文报告。

输出格式要求：
1. 必须是纯 HTML 片段（以 <div style="..."> 开头）。
2. 使用内联 CSS，采用深色模式、玻璃拟态风格，搭配鲜艳的强调色（如 #00ff88）。
3. 确保在 QQ 邮箱中完美显示。

对于每个项目：
1. 简要说明它为何上榜（例如：'新型 LLM 框架'，'解决了 X 痛点'）。
2. 提供 1 句精炼的技术本质说明。
3. 包含一个 '潜力指数' (1-5)。

保持硬核风格，拒绝废话。不要输出 Markdown 格式的包裹符号。"""

    user_content = f"Date: {date_str}\n\nTrending Repositories:\n" + json.dumps(repos, indent=2)
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            stream=False,
            timeout=60
        )
        
        clean_html = response.choices[0].message.content.replace("```html", "").replace("```", "").strip()
        if "<div" in clean_html:
            clean_html = clean_html[clean_html.find("<div"):]
            
        subject = f"🚀 GitHub Trending Brief · {date_str}"
        return subject, clean_html
    except Exception as e:
        log(f"⚠️ LLM Error: {e}")
        return "GitHub Trending Update", "⚠️ Summary generation failed."

# 3. Execution and Delivery
def main():
    log("🚀 Starting GitHub Trend Notifier (Hardcore Edition)...")
    repos = fetch_github_trending()
    
    if not repos:
        log("❌ No data fetched. Exiting.")
        return
        
    subject, html_body = get_ai_summary(repos)
    
    final_html = f"""
    <div style="background-color: #0d1117; padding: 40px 10px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; background: #161b22; border: 1px solid #30363d; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); overflow: hidden;">
            <div style="padding: 20px; border-bottom: 1px solid #30363d; background: linear-gradient(135deg, #238636 0%, #2ea043 100%);">
                <h1 style="margin: 0; color: #ffffff; font-size: 20px; letter-spacing: 1px;">GITHUB 趋势侦查</h1>
            </div>
            <div style="padding: 20px;">
                {html_body}
            </div>
            <div style="padding: 20px; text-align: center; border-top: 1px solid #30363d; background: #0d1117;">
                <p style="margin: 0; color: #8b949e; font-size: 11px; letter-spacing: 2px; text-transform: uppercase;">由 Antigravity 自动驱动 · Musk Flavor</p>
            </div>
        </div>
    </div>
    """
    
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [TO_EMAIL],
            "subject": subject,
            "html": final_html
        })
        log(f"🎉 Delivery successful: {subject}")
    except Exception as e:
        log(f"❌ Delivery failed: {e}")

if __name__ == "__main__":
    main()
