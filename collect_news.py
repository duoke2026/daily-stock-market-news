import requests
import feedparser
import smtplib
import json
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 美国证券市场新闻RSS源
NEWS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",  # Reuters Business News
    "https://feeds.cnbc.com/cnbc/market_news",  # CNBC Market News
    "https://feeds.bloomberg.com/markets/news.rss",  # Bloomberg Markets
    "https://feeds.bloomberg.com/stocks/news.rss",  # Bloomberg Stocks
]

def fetch_news(limit=20):
    """从多个RSS源获取新闻"""
    all_news = []
    
    for feed_url in NEWS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:  # 每个源取5条
                news_item = {
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': entry.get('published', ''),
                    'source': feed.feed.get('title', 'Unknown Source')
                }
                all_news.append(news_item)
        except Exception as e:
            print(f"Error fetching from {feed_url}: {e}")
    
    # 返回前20条
    return all_news[:limit]

def generate_email_body(news_list):
    """生成邮件内容"""
    html_content = f"""
    <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .header {{ background-color: #1f77d9; color: white; padding: 20px; text-align: center; }}
                .news-item {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
                .news-title {{ font-size: 16px; font-weight: bold; color: #1f77d9; margin-bottom: 10px; }}
                .news-link {{ color: #0066cc; text-decoration: none; word-break: break-all; }}
                .news-summary {{ margin-top: 10px; color: #333; line-height: 1.6; }}
                .news-meta {{ color: #666; font-size: 12px; margin-top: 10px; }}
                .footer {{ text-align: center; color: #999; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>美国证券市场新闻速递</h1>
                    <p>{datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
                </div>
                <div class="content">
    """
    
    for idx, news in enumerate(news_list, 1):
        html_content += f"""
                    <div class="news-item">
                        <div class="news-title">{idx}. {news['title']}</div>
                        <div class="news-link">📍 来源: {news['source']}</div>
                        <div class="news-summary">{news['summary'][:200]}...</div>
                        <div class="news-meta">
                            <a class="news-link" href="{news['link']}" target="_blank">阅读全文 →</a>
                            <br>发布时间: {news['published']}
                        </div>
                    </div>
        """
    
    html_content += """
                </div>
                <div class="footer">
                    <p>本邮件由自动化脚本生成 | 每日上午9点定时发送</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return html_content

def send_email(recipient, subject, html_content, smtp_server, smtp_port, sender_email, sender_password):
    """发送邮件"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient
        
        # 添加HTML内容
        part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part)
        
        # 发送邮件
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"邮件已发送到: {recipient}")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

def main():
    """主函数"""
    print("开始收集美国证券市场新闻...")
    
    # 获取新闻
    news_list = fetch_news(limit=20)
    
    if not news_list:
        print("未获取到新闻")
        return
    
    print(f"成功获取 {len(news_list)} 条新闻")
    
    # 生成邮件内容
    email_body = generate_email_body(news_list)
    
    # 从环境变量获取配置
    recipient_email = os.getenv('RECIPIENT_EMAIL', 'duoke1974@gmail.com')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '465'))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    if not sender_email or not sender_password:
        print("错误: 请设置SENDER_EMAIL和SENDER_PASSWORD环境变量")
        return
    
    # 发送邮件
    subject = f"美国证券市场新闻 - {datetime.now().strftime('%Y年%m月%d日')}"
    send_email(recipient_email, subject, email_body, smtp_server, smtp_port, sender_email, sender_password)
    
    # 保存新闻到本地文件用于备份
    news_file = f"news_{datetime.now().strftime('%Y%m%d')}.json"
    with open(news_file, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
    print(f"新闻已保存到: {news_file}")

if __name__ == "__main__":
    main()
