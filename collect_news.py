import feedparser
from datetime import datetime
from pathlib import Path

SITE_TITLE = "CPG Europe Daily Intelligence"

feeds_file = "feeds.txt"

html = f"""
<html>
<head>
<title>{SITE_TITLE}</title>
<style>
body {{
    font-family: Arial;
    max-width: 1100px;
    margin: auto;
    padding: 20px;
    background: #f5f5f5;
}}
h1 {{
    color: #004b87;
}}
.section {{
    background:white;
    padding:20px;
    margin-bottom:20px;
    border-radius:8px;
}}
a {{
    text-decoration:none;
}}
</style>
</head>
<body>

<h1>{SITE_TITLE}</h1>

<p>
Generated on {datetime.now().strftime('%d-%b-%Y %H:%M')}
</p>
"""

with open(feeds_file, "r", encoding="utf-8") as f:
    feeds = [x.strip() for x in f.readlines() if x.strip() and not x.startswith("#")]

for feed in feeds:
    try:
        d = feedparser.parse(feed)

        html += f"""
        <div class="section">
        <h2>{feed}</h2>
        """

        for entry in d.entries[:10]:

            title = entry.get("title", "No title")
            link = entry.get("link", "#")

            html += f"""
            <p>
            {link}
            {title}
            </a>
            </p>
            """

        html += "</div>"

    except Exception as e:
        print(e)

html += "</body></html>"

Path("docs").mkdir(exist_ok=True)

with open("docs/index.html","w",encoding="utf-8") as f:
    f.write(html)

print("Website Updated")
