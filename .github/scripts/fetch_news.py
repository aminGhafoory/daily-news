#!/usr/bin/env python3
"""
Fetch news from free sources without API keys
"""

import json
import feedparser
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
from typing import List, Dict, Any

class NewsFetcher:
    def __init__(self):
        self.news_dir = Path("news")
        self.news_dir.mkdir(exist_ok=True)
        
        # RSS Feeds from various news sources
        self.rss_feeds = [
            {
                "name": "BBC News",
                "url": "http://feeds.bbci.co.uk/news/rss.xml",
                "category": "world"
            },
            {
                "name": "Reuters",
                "url": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
                "category": "business"
            },
            {
                "name": "NPR News",
                "url": "https://feeds.npr.org/1001/rss.xml",
                "category": "world"
            },
            {
                "name": "Science Daily",
                "url": "https://www.sciencedaily.com/rss/all.xml",
                "category": "science"
            },
            {
                "name": "Hacker News",
                "url": "https://hnrss.org/frontpage",
                "category": "technology"
            }
        ]
        
        # HTML scraping sources (fallback for sites without RSS)
        self.html_sources = [
            {
                "name": "Ars Technica",
                "url": "https://arstechnica.com/",
                "selector": ".article-content h2 a",
                "category": "technology"
            }
        ]

    def fetch_rss_feed(self, feed_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed"""
        articles = []
        try:
            feed = feedparser.parse(feed_info["url"])
            
            for entry in feed.entries[:10]:  # Get top 10 articles
                article = {
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", entry.get("updated", "")),
                    "source": feed_info["name"],
                    "category": feed_info["category"],
                    "summary": entry.get("summary", entry.get("description", "No summary available")),
                    "fetched_at": datetime.now().isoformat()
                }
                articles.append(article)
                
        except Exception as e:
            print(f"Error fetching {feed_info['name']}: {e}")
        
        return articles

    def fetch_html_source(self, source_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape news from HTML source"""
        articles = []
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(source_info["url"], headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = soup.select(source_info["selector"])[:10]
            
            for link in links:
                href = link.get('href', '')
                if not href.startswith('http'):
                    href = requests.compat.urljoin(source_info["url"], href)
                
                article = {
                    "title": link.get_text().strip(),
                    "link": href,
                    "published": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z"),
                    "source": source_info["name"],
                    "category": source_info["category"],
                    "summary": "Scraped from HTML source",
                    "fetched_at": datetime.now().isoformat()
                }
                articles.append(article)
                
        except Exception as e:
            print(f"Error scraping {source_info['name']}: {e}")
        
        return articles

    def generate_article_id(self, article: Dict[str, Any]) -> str:
        """Generate unique ID for article"""
        text = f"{article['title']}{article['link']}"
        return hashlib.md5(text.encode()).hexdigest()[:8]

    def save_news_to_file(self, all_articles: List[Dict[str, Any]]):
        """Save news to various file formats"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Remove duplicates based on title
        seen = set()
        unique_articles = []
        for article in all_articles:
            title = article['title'].lower()
            if title not in seen:
                seen.add(title)
                unique_articles.append(article)
        
        # Sort by published date (newest first)
        unique_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        # Save as JSON
        json_path = self.news_dir / f"news_{today}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(unique_articles, f, indent=2, ensure_ascii=False)
        
        # Save as Markdown
        md_path = self.news_dir / f"news_{today}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Daily News Digest - {today}\n\n")
            f.write(f"Total articles: {len(unique_articles)}\n\n")
            
            # Group by category
            categories = {}
            for article in unique_articles:
                cat = article.get('category', 'general')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(article)
            
            for category, articles in categories.items():
                f.write(f"## {category.title()}\n\n")
                for article in articles:
                    f.write(f"### [{article['title']}]({article['link']})\n")
                    f.write(f"**Source:** {article['source']}  \n")
                    f.write(f"**Published:** {article['published']}  \n")
                    f.write(f"**Summary:** {article['summary'][:200]}...\n\n")
        
        # Update README with latest news
        self.update_readme(unique_articles, today)
        
        # Save as simple text file
        txt_path = self.news_dir / f"news_{today}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Daily News Digest - {today}\n")
            f.write("=" * 40 + "\n\n")
            for article in unique_articles[:20]:  # Top 20 articles
                f.write(f"Title: {article['title']}\n")
                f.write(f"Source: {article['source']}\n")
                f.write(f"URL: {article['link']}\n")
                f.write("-" * 40 + "\n")

    def update_readme(self, articles: List[Dict[str, Any]], date: str):
        """Update repository README with latest news"""
        readme_path = Path("README.md")
        
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "# News Repository\n\n"
        
        # Find or create news section
        news_section = "## Latest News\n\n"
        if "## Latest News" in content:
            parts = content.split("## Latest News")
            content = parts[0] + news_section
        else:
            content += news_section
        
        # Add top 5 news items
        content += f"*Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"
        for article in articles[:5]:
            content += f"- [{article['title']}]({article['link']}) - *{article['source']}*\n"
        
        content += f"\n[View all news](news/news_{date}.md)\n"
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def run(self):
        """Main execution method"""
        print(f"Starting news fetch at {datetime.now()}")
        all_articles = []
        
        # Fetch from RSS feeds
        for feed in self.rss_feeds:
            print(f"Fetching from RSS: {feed['name']}")
            articles = self.fetch_rss_feed(feed)
            all_articles.extend(articles)
            print(f"  Found {len(articles)} articles")
        
        # Fetch from HTML sources
        for source in self.html_sources:
            print(f"Scraping from: {source['name']}")
            articles = self.fetch_html_source(source)
            all_articles.extend(articles)
            print(f"  Found {len(articles)} articles")
        
        # Save to files
        if all_articles:
            self.save_news_to_file(all_articles)
            print(f"Saved {len(all_articles)} unique articles")
        else:
            print("No articles found")
        
        print("News fetch completed")

if __name__ == "__main__":
    fetcher = NewsFetcher()
    fetcher.run()
