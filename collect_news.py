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

TOP_STORY_WORDS = [
    "acquisition",
    "merger",
    "investment",
    "launch",
    "expansion",
    "growth",
    "partnership",
    "carrefour",
    "tesco",
    "aldi",
    "lidl",
    "nestle",
    "unilever",
    "danone",
    "pepsico",
    "coca-cola"
]

Path("docs").mkdir(exist_ok=True)
Path("docs/archive").mkdir(exist_ok=True)

today = datetime.now()

edition_date = today.strftime("%d %B %Y")
timestamp = today.strftime("%d %b %Y %H:%M")

archive_file = f"docs/archive/{today.strftime('%Y-%m-%d')}.html"

articles = []
seen = set()

with open("feeds.txt", "r", encoding="utf-8") as f:
    feeds = [
        x.strip()
        for x in f.readlines()
        if x.strip() and not x.startswith("#")
    ]

for feed in feeds:

    try:

        data = feedparser.parse(feed)

        source_name = data.feed.get(
            "title",
            "Unknown Source"
        )

        for entry in data.entries:

            title = entry.get("title", "")

            link = entry.get("link", "")

            summary = (
                entry.get("summary")
                or entry.get("description")
                or "Summary unavailable."
            )

            summary = re.sub(r"<.*?>", "", summary)

            summary = summary.replace("\n", " ")

            if len(summary) > 500:
                summary = summary[:500] + "..."

            key = title.lower().strip()

            if key in seen:
                continue

            seen.add(key)

            text = (title + " " + summary).lower()

            country = "Europe"

            for c, keywords in COUNTRIES.items():

                if any(k in text for k in keywords):
                    country = c
                    break

            top_story = any(
                keyword in text
                for keyword in TOP_STORY_WORDS
            )

            articles.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": source_name,
                "country": country,
                "top_story": top_story
            })

    except Exception as e:
        print("Feed Error:", feed, e)

articles = sorted(
    articles,
    key=lambda x: x["top_story"],
    reverse=True
)

html = f"""
<html>

<head>

<title>{SITE_TITLE}</title>

<style>

body {{
    background:#f3f5f7;
    font-family:Arial,sans-serif;
    max-width:1200px;
    margin:auto;
    padding:25px;
}}

.header {{
    background:#003366;
    color:white;
    padding:25px;
    border-radius:10px;
    margin-bottom:25px;
}}

.section {{
    background:white;
    padding:20px;
    border-radius:10px;
    margin-bottom:25px;
    box-shadow:0 1px 5px rgba(0,0,0,0.15);
}}

.story {{
    padding:18px;
    margin-bottom:15px;
    border-left:4px solid #003366;
    background:#fafafa;
}}

.story h3 {{
    margin-top:0;
}}

.story a {{
    text-decoration:none;
    color:#0056b3;
}}

.story a:hover {{
    text-decoration:underline;
}}

.story p {{
    line-height:1.6;
    color:#333;
}}

.meta {{
    color:#777;
    font-size:12px;
    margin-top:10px;
}}

h1,h2 {{
    margin-top:0;
}}

</style>

</head>

<body>

<div class="header">

<h1>CPG Europe Daily Intelligence</h1>

<p>
European FMCG / Consumer Goods Intelligence Newsletter
</p>

<p>
Edition Date: {edition_date}
<br>
Updated: {timestamp}
</p>

</div>
"""

# TOP STORIES

html += """
<div class="section">
<h2>Top Stories</h2>
"""

for article in articles[:15]:

    html += f"""
    <div class="story">

        <h3>
            {article['link']}
                {article['title']}
            </a>
        </h3>

        <p>
            {article['summary']}
        </p>

        <div class="meta">
            Source: {article['source']}
        </div>

    </div>
    """

html += "</div>"

# COUNTRY SECTIONS

for country in COUNTRIES.keys():

    country_articles = [
        a
        for a in articles
        if a["country"] == country
    ]

    html += f"""
    <div class="section">
    <h2>{country}</h2>
    """

    if len(country_articles) == 0:

        html += """
        <p>No relevant stories found.</p>
        """

    else:

        for article in country_articles[:10]:

            html += f"""
            <div class="story">

                <h3>
                    {article['link']}">
                        {article['title']}
                    </a>
                </h3>

                <p>
                    {article['summary']}
                </p>

                <div class="meta">
                    Source: {article['source']}
                </div>

            </div>
            """

    html += "</div>"

html += f"""

<div class="section">

<h2>Archive</h2>

<p>
Daily archive created automatically.
Current archive file:
{today.strftime('%Y-%m-%d')}.html
</p>

</div>

</body>
</html>
"""

with open(
    "docs/index.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(html)

with open(
    archive_file,
    "w",
    encoding="utf-8"
) as f:
    f.write(html)

print(
    f"Newsletter generated successfully. "
    f"Stories: {len(articles)}"
)
    

            



