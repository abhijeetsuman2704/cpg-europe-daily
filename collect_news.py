import feedparser
from datetime import datetime
from pathlib import Path
import os

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

FMCG_KEYWORDS = [
    "retail",
    "supermarket",
    "grocery",
    "consumer",
    "fmcg",
    "cpg",
    "food",
    "beverage",
    "drink",
    "brand",
    "product",
    "packaging",
    "supply chain",
    "sustainability",
    "acquisition",
    "merger",
    "launch"
]

Path("docs").mkdir(exist_ok=True)
Path("docs/archive").mkdir(exist_ok=True)

today = datetime.now()
edition_date = today.strftime("%d %b %Y")
archive_file = f"docs/archive/{today.strftime('%Y-%m-%d')}.html"

articles = []
seen = set()

with open("feeds.txt", "r", encoding="utf-8") as f:
    feeds = [x.strip() for x in f.readlines()
             if x.strip() and not x.startswith("#")]

for feed in feeds:

    try:
        parsed = feedparser.parse(feed)

        for entry in parsed.entries:

            title = entry.get("title", "")
            link = entry.get("link", "")

            text = title.lower()

            if not any(word in text for word in FMCG_KEYWORDS):
                continue

            key = title.lower().strip()

            if key in seen:
                continue

            seen.add(key)

            country = "Europe"

            for c, keywords in COUNTRIES.items():
                if any(k in text for k in keywords):
                    country = c
                    break

            articles.append({
                "title": title,
                "link": link,
                "country": country
            })

    except Exception as e:
        print(feed, e)

html = f"""
<html>
<head>

<title>{SITE_TITLE}</title>

<style>

body {{
    font-family: Arial, sans-serif;
    background:#f4f6f8;
    margin:auto;
    max-width:1200px;
    padding:20px;
}}

.header {{
    background:#003366;
    color:white;
    padding:20px;
    border-radius:8px;
}}

.section {{
    background:white;
    margin-top:20px;
    padding:15px;
    border-radius:8px;
    box-shadow:0 2px 5px rgba(0,0,0,0.1);
}}

h1 {{
    margin:0;
}}

h2 {{
    color:#003366;
}}

a {{
    text-decoration:none;
    color:#0056b3;
}}

a:hover {{
    text-decoration:underline;
}}

.article {{
    padding:5px 0;
}}

.date {{
    color:#666;
}}

</style>

</head>

<body>

<div class="header">
<h1>CPG Europe Daily Intelligence</h1>
<p>European FMCG / CPG Intelligence Newsletter</p>
<p class="date">{edition_date}</p>
</div>

<div class="section">
<h2>Top Stories</h2>
"""

for article in articles[:15]:

    html += f"""
    <div class="article">
    • {article['link']}
    {article['title']}
    </a>
    </div>
    """

html += "</div>"

for country in COUNTRIES.keys():

    html += f"""
    <div class="section">
    <h2>{country}</h2>
    """

    country_articles = [
        x for x in articles
        if x["country"] == country
    ]

    if len(country_articles) == 0:

        html += "<p>No relevant stories found.</p>"

    else:

        for article in country_articles[:20]:

            html += f"""
            <div class="article">
            • {article['link']} target="_blank">
            {article['title']}
            </a>
            </div>
            """

    html += "</div>"

html += """

<div class="section">
<h2>Archive</h2>
<p>
Previous editions available in the archive folder.
</p>
</div>

</body>
</html>

"""

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

with open(archive_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Newsletter generated: {len(articles)} articles")

            



