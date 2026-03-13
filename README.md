# Daily News Repository

This repository automatically fetches news from various free sources daily and stores them.

## Features
- Fetches news from RSS feeds and HTML sources
- No API keys required
- Runs daily via GitHub Actions
- Stores news in multiple formats (JSON, Markdown, TXT)
- Updates README with latest headlines

## News Sources
- BBC News (World)
- Reuters (Business)
- NPR News (World)
- Science Daily (Science)
- Hacker News (Technology)
- Ars Technica (Technology)

## Structure
- `news/` - Contains daily news files
  - `news_YYYY-MM-DD.json` - JSON format
  - `news_YYYY-MM-DD.md` - Markdown format
  - `news_YYYY-MM-DD.txt` - Plain text format

## Latest News
*Updated automatically by GitHub Actions*

[View all news](news/)
