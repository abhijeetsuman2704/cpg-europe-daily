import feedparser
from datetime import datetime
from pathlib import Path
import re

SITE_TITLE = "CPG Europe Daily Intelligence"

COUNTRIES = {
    "United Kingdom": ["uk", "britain", "british", "england", "london"],
    "France": ["france", "french"],
    "Germany": ["germany", "german"],
    "Netherlands": ["netherlands", "dutch"],
    "Italy": ["italy", "italian"],
    "Spain": ["spain", "spanish"],
    "Greece": ["greece", "greek"]
}

# Core priority categories requested
CATEGORIES = {
    "Dairy & Yogurt": ["dairy", "yogurt", "yoghurt", "milk", "cheese", "butter", "danone", "lactalis", "arla"],
    "Plant-Based Alternative": ["plant-based", "vegan", "oat milk", "almond milk", "soy", "dairy-free", "meatless"],
    "Baby & Kid Nutrition": ["baby food", "infant nutrition", "toddler", "kid nutrition", "aptamil", "milupa", "gerber"]
}

TOP_STORY_WORDS = [
    "acquisition", "merger", "investment", "launch", "expansion", 
    "growth", "partnership", "carrefour", "tesco", "aldi", "lidl", 
    "nestle", "unilever", "danone", "pepsico", "coca-cola"
]

# Ensure directories exist
Path("docs").mkdir(exist_ok=True)
Path("docs/archive").mkdir(exist_ok=True)

today = datetime.now()
edition_date = today.strftime("%d %B %Y")
timestamp = today.strftime("%d %b %Y %H:%M")
archive_file = f"docs/archive/{today.strftime('%Y-%m-%d')}.html"

articles = []
seen = set()

# Read feeds securely
if not Path("feeds.txt").exists():
    with open("feeds.txt", "w", encoding="utf-8") as f:
        f.write("# Add RSS Feed URLs below (one per line)\n")

with open("feeds.txt", "r", encoding="utf-8") as f:
    feeds = [line.strip() for line in f if line.strip() and not line.startswith("#")]

for feed in feeds:
    try:
        data = feedparser.parse(feed)
        source_name = data.feed.get("title", "Global CPG News")

        for entry in data.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary") or entry.get("description") or "Summary unavailable."
            
            # Clean HTML tags and newlines
            summary = re.sub(r"<.*?>", "", summary)
            summary = " ".join(summary.split())
            if len(summary) > 400:
                summary = summary[:400] + "..."

            key = title.lower().strip()
            if not title or key in seen:
                continue
            seen.add(key)

            search_text = f"{title} {summary}".lower()

            # Geo-tagging
            matched_country = "Europe"
            for country, keywords in COUNTRIES.items():
                if any(k in search_text for k in keywords):
                    matched_country = country
                    break

            # Category matching
            matched_category = "General FMCG"
            for category, keywords in CATEGORIES.items():
                if any(k in search_text for k in keywords):
                    matched_category = category
                    break

            # Core Top Story logic
            is_top_story = any(word in search_text for word in TOP_STORY_WORDS)

            articles.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": source_name,
                "country": matched_country,
                "category": matched_category,
                "top_story": is_top_story
            })
    except Exception as e:
        print(f"Error reading feed {feed}: {e}")

# Sort: Top Stories first
articles = sorted(articles, key=lambda x: x["top_story"], reverse=True)

# Separate articles for targeted rendering
top_stories = [a for a in articles if a["top_story"]][:10]
general_stories = [a for a in articles if not a["top_story"]]

# Build Executive Dashboard HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_TITLE}</title>
    <style>
        :root {{
            --bg-primary: #f8fafc;
            --surface: #ffffff;
            --text-main: #0f172a;
            --text-muted: #475569;
            --brand: #0f172a;
            --accent: #2563eb;
            --border: #e2e8f0;
            --tag-bg: #f1f5f9;
        }}
        body {{
            background-color: var(--bg-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: var(--text-main);
            margin: 0;
            padding: 0;
            line-height: 1.5;
        }}
        .navbar {{
            background-color: var(--brand);
            color: white;
            padding: 2rem;
            border-bottom: 4px solid var(--accent);
        }}
        .navbar-container {{
            max-width: 1100px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .navbar h1 {{ margin: 0; font-size: 1.75rem; font-weight: 700; letter-spacing: -0.025em; }}
        .navbar p {{ margin: 0.25rem 0 0 0; color: #94a3b8; font-size: 0.95rem; }}
        .meta-badge {{
            background: rgba(255,255,255,0.1);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-family: monospace;
            text-align: right;
        }}
        .main-layout {{
            max-width: 1100px;
            margin: 2.5rem auto;
            padding: 0 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 2.5rem;
        }}
        .section-title {{
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 1.25rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 20px -8px rgba(0,0,0,0.08);
        }}
        .card-tags {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
            flex-wrap: wrap;
        }}
        .tag {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
            background: var(--tag-bg);
            color: var(--text-muted);
            text-transform: uppercase;
        }}
        .tag-priority {{ background: #eff6ff; color: var(--accent); }}
        .card h3 {{
            margin: 0 0 0.75rem 0;
            font-size: 1.1rem;
            font-weight: 600;
            line-height: 1.4;
        }}
        .card h3 a {{
            color: var(--text-main);
            text-decoration: none;
        }}
        .card h3 a:hover {{ color: var(--accent); }}
        .card p {{
            color: var(--text-muted);
            font-size: 0.9rem;
            margin: 0 0 1.25rem 0;
            flex-grow: 1;
        }}
        .card-footer {{
            font-size: 0.8rem;
            color: #94a3b8;
            border-top: 1px solid var(--border);
            padding-top: 0.75rem;
            display: flex;
            justify-content: space-between;
        }}
        .no-data {{
            color: var(--text-muted);
            font-style: italic;
            grid-column: 1 / -1;
            padding: 2rem;
            text-align: center;
            background: var(--surface);
            border-radius: 8px;
            border: 1px dashed var(--border);
        }}
    </style>
</head>
<body>

<div class="navbar">
    <div class="navbar-container">
        <div>
            <h1>{SITE_TITLE}</h1>
            <p>Strategic Intelligence & Portfolio Insights</p>
        </div>
        <div class="meta-badge">
            Edition: {edition_date}<br>
            Sync Time: {timestamp} UTC
        </div>
    </div>
</div>

<div class="main-layout">

    <section>
        <div class="section-title">⚡ High-Priority Intelligence Briefing</div>
        <div class="grid">
"""

if not top_stories:
    html += '<div class="no-data">No major priority developments tracked today.</div>'
else:
    for a in top_stories:
        html += f"""
            <div class="card" style="border-top: 4px solid var(--accent);">
                <div>
                    <div class="card-tags">
                        <span class="tag tag-priority">Top Story</span>
                        <span class="tag">{a['country']}</span>
                        <span class="tag">{a['category']}</span>
                    </div>
                    <h3><a href="{a['link']}" target="_blank">{a['title']}</a></h3>
                    <p>{a['summary']}</p>
                </div>
                <div class="card-footer">
                    <span>Source: {a['source']}</span>
                </div>
            </div>"""

html += """
        </div>
    </section>

    <section>
        <div class="section-title">📍 Market Overviews by Country</div>
"""

for country in COUNTRIES.keys():
    country_articles = [a for a in general_stories if a["country"] == country][:6]
    
    html += f"""
        <h3 style="margin: 1.5rem 0 1rem 0; font-size: 1.2rem; color: var(--text-muted);">{country}</h3>
        <div class="grid" style="margin-bottom: 2rem;">
    """
    
    if not country_articles:
        html += '<div class="no-data">No market-specific alerts today.</div>'
    else:
        for a in country_articles:
            html += f"""
                <div class="card">
                    <div>
                        <div class="card-tags">
                            <span class="tag">{a['category']}</span>
                        </div>
                        <h3><a href="{a['link']}" target="_blank">{a['title']}</a></h3>
                        <p>{a['summary']}</p>
                    </div>
                    <div class="card-footer">
                        <span>Source: {a['source']}</span>
                    </div>
                </div>"""
    html += "</div>"

html += """
    </section>
</div>

</body>
</html>
"""

# Commit and output static instances
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

with open(archive_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Intelligence Dashboard compiled. Processed: {len(articles)} alerts.")

            



