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

# Expanded Category Matrix focusing heavily on Danone's core & adjacent sectors
CATEGORIES = {
    "Dairy & Yogurt": ["dairy", "yogurt", "yoghurt", "milk", "cheese", "butter", "lactalis", "arla"],
    "Plant-Based Alternatives": ["plant-based", "vegan", "oat milk", "almond milk", "soy", "dairy-free", "alpro", "oatly"],
    "Baby & Kid Nutrition": ["baby food", "infant nutrition", "toddler", "kid nutrition", "aptamil", "milupa", "gerber", "formula"],
    "Hydration & Functional Beverages": ["water", "protein water", "collagen water", "functional beverage", "mineral water", "evian", "volvic", "vittel", "perrier", "hydration", "electrolyte"]
}

# Comprehensive Competitor Threat Matrix
COMPETITORS = {
    "Danone": ["danone"],
    "Nestle": ["nestle", "nestlé"],
    "Unilever": ["unilever"],
    "Arla": ["arla"],
    "Bel Group": ["bel group", "groupe bel", "babybel", "laughing cow"],
    "Coca-Cola": ["coca-cola", "coke"],
    "PepsiCo": ["pepsi", "pepsico"],
    "Ferrero": ["ferrero"],
    "Mars": ["mars"],
    "Mondelez": ["mondelez", "mondelēz"],
    "Reckitt Benckiser": ["reckitt", "benckiser", "rb"],
    "Heineken": ["heineken"],
    "Procter & Gamble": ["procter", "gamble", "p&g"],
    "Kraft Heinz": ["kraft", "heinz"]
}

# Flattens all brand keywords to trigger high-priority alerts
TOP_STORY_WORDS = [
    "acquisition", "merger", "investment", "joint venture", "jv", "buyout", "takeover",
    "carrefour", "tesco", "aldi", "lidl"
] + [kw for brand_kws in COMPETITORS.values() for kw in brand_kws]

# Context Rules for Impact Tagging
IMPACT_KEYWORDS = {
    "M&A Activity": ["acquisition", "merger", "buyout", "takeover", "acquired", "sold", "divestment"],
    "Product Launch": ["launch", "introduce", "unveil", "rollout", "new product", "innovation", "entered"],
    "Regulatory Change": ["regulation", "policy", "ban", "tax", "approved", "compliance", "law", "efsa"],
    "Corporate Strategy": ["partnership", "investment", "expansion", "growth", "strategy", "restructuring"]
}

Path("docs").mkdir(exist_ok=True)
Path("docs/archive").mkdir(exist_ok=True)

today = datetime.now()
edition_date = today.strftime("%d %B %Y")
timestamp = today.strftime("%d %b %Y %H:%M")
archive_file = f"docs/archive/{today.strftime('%Y-%m-%d')}.html"

articles = []
seen = set()

# Safe checking for feeds config
if not Path("feeds.txt").exists():
    with open("feeds.txt", "w", encoding="utf-8") as f:
        f.write("# Add your target European CPG RSS links here (one per line)\n")

with open("feeds.txt", "r", encoding="utf-8") as f:
    feeds = [line.strip() for line in f if line.strip() and not line.startswith("#")]

for feed in feeds:
    try:
        data = feedparser.parse(feed)
        source_name = data.feed.get("title", "CPG Intelligence Feed")

        for entry in data.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary") or entry.get("description") or "Summary unavailable."
            
            summary = re.sub(r"<.*?>", "", summary)
            summary = " ".join(summary.split())
            if len(summary) > 450:
                summary = summary[:450] + "..."

            key = title.lower().strip()
            if not title or key in seen:
                continue
            seen.add(key)

            search_text = f"{title} {summary}".lower()

            # 1. Geo-tagging
            matched_country = "Europe"
            for country, keywords in COUNTRIES.items():
                if any(k in search_text for k in keywords):
                    matched_country = country
                    break

            # 2. Category classification
            matched_category = "General FMCG"
            for category, keywords in CATEGORIES.items():
                if any(k in search_text for k in keywords):
                    matched_category = category
                    break

            # 3. Strategic Impact Tagging
            matched_impact = "Market Update"
            for impact, keywords in IMPACT_KEYWORDS.items():
                if any(k in search_text for k in keywords):
                    matched_impact = impact
                    break

            # 4. Read Time Calculation
            word_count = len(search_text.split())
            read_time = max(1, round(word_count / 220))

            # 5. Competitor Tracking & Dynamic Text Highlighting
            active_brands = []
            for brand_name, keywords in COMPETITORS.items():
                for kw in keywords:
                    pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                    if pattern.search(search_text):
                        if brand_name != "Danone" or (brand_name == "Danone" and kw in search_text):
                            # Apply CSS styling directly within string tokens
                            title = pattern.sub(f'<mark class="highlight-brand">{kw.capitalize()}</mark>', title)
                            summary = pattern.sub(f'<mark class="highlight-brand">{kw.capitalize()}</mark>', summary)
                        if brand_name not in active_brands:
                            active_brands.append(brand_name)

            is_top_story = any(word in search_text for word in TOP_STORY_WORDS)

            articles.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": source_name,
                "country": matched_country,
                "category": matched_category,
                "impact": matched_impact,
                "read_time": read_time,
                "brands": active_brands,
                "top_story": is_top_story
            })
    except Exception as e:
        print(f"Skipping problematic feed structure: {feed} -> {e}")

# Prioritize critical events
articles = sorted(articles, key=lambda x: x["top_story"], reverse=True)

# Generate Programmatic Rule-Based Executive Synthesis
def generate_executive_synthesis(all_articles):
    top_brands = {}
    top_cats = {}
    top_geos = {}
    
    for a in all_articles:
        for b in a["brands"]:
            top_brands[b] = top_brands.get(b, 0) + 1
        top_cats[a["category"]] = top_cats.get(a["category"], 0) + 1
        if a["country"] != "Europe":
            top_geos[a["country"]] = top_geos.get(a["country"], 0) + 1
            
    sorted_brands = sorted(top_brands.items(), key=lambda x: x[1], reverse=True)
    sorted_cats = sorted(top_cats.items(), key=lambda x: x[1], reverse=True)
    sorted_geos = sorted(top_geos.items(), key=lambda x: x[1], reverse=True)
    
    bullets = []
    if sorted_brands:
        brand_list = ", ".join([b[0] for b in sorted_brands[:3]])
        bullets.append(f"<strong>High-Profile Competitive Activity:</strong> Core industry movements detected today from primary tracked peer portfolios: <strong>{brand_list}</strong>.")
    else:
        bullets.append("<strong>Competitive Intensity:</strong> Standard transactional market reporting; no outlier capital allocation or competitive disruptions noted.")
        
    if sorted_cats:
        bullets.append(f"<strong>Category Distribution Trend:</strong> Structural tracking indicates an emphasis on <strong>{sorted_cats[0][0]}</strong> profiles, signaling accelerated regional development.")
    
    if sorted_geos:
        bullets.append(f"<strong>Geographic Hub Focus:</strong> Regional concentration patterns pinpoint elevated regulatory, strategic, or rollout tracking targeting the <strong>{sorted_geos[0][0]}</strong> marketplace.")
        
    return bullets

synthesis_bullets = generate_executive_synthesis(articles)

# Build Leadership Layout
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_TITLE}</title>
    <style>
        :root {{
            --bg-primary: #f4f6f9;
            --surface: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --brand-primary: #002e6e; /* Professional Corporate Navy */
            --accent: #0284c7;
            --border: #e2e8f0;
            --tag-bg: #f8fafc;
            --highlight: #fef08a; /* Soft highlighter yellow */
        }}
        body {{
            background-color: var(--bg-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: var(--text-main);
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }}
        .navbar {{
            background-color: var(--brand-primary);
            color: white;
            padding: 2.5rem 2rem;
            border-bottom: 5px solid var(--accent);
        }}
        .navbar-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
        }}
        .navbar h1 {{ margin: 0; font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; }}
        .navbar p {{ margin: 0.35rem 0 0 0; color: #93c5fd; font-size: 1rem; opacity: 0.9; }}
        .meta-badge {{
            background: rgba(255,255,255,0.08);
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            font-size: 0.85rem;
            border: 1px solid rgba(255,255,255,0.15);
            text-align: right;
        }}
        .main-layout {{
            max-width: 1200px;
            margin: 3rem auto;
            padding: 0 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 3rem;
        }}
        /* Executive Summary Box Styling */
        .synthesis-container {{
            background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
            border-left: 6px solid var(--brand-primary);
            border-radius: 12px;
            padding: 1.75rem 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            border: 1px solid #d0e7ff;
        }}
        .synthesis-title {{
            font-size: 1.15rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--brand-primary);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .synthesis-list {{ margin: 0; padding-left: 1.25rem; }}
        .synthesis-list li {{ margin-bottom: 0.75rem; font-size: 0.95rem; color: #334155; }}
        
        .section-title {{
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
            color: var(--brand-primary);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 1.75rem;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.75rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: box-shadow 0.2s, transform 0.2s;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 15px 30px -10px rgba(0,0,0,0.07);
        }}
        .card-tags {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        .tag {{
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.3rem 0.65rem;
            border-radius: 4px;
            background: var(--tag-bg);
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }}
        /* Color-Coded Impact Indicators */
        .tag-ma {{ background: #fee2e2; color: #991b1b; }}
        .tag-launch {{ background: #dcfce7; color: #166534; }}
        .tag-reg {{ background: #fef3c7; color: #92400e; }}
        .tag-strat {{ background: #e0f2fe; color: #075985; }}
        .tag-priority {{ background: var(--brand-primary); color: white; }}
        
        .card h3 {{
            margin: 0 0 0.85rem 0;
            font-size: 1.15rem;
            font-weight: 600;
            line-height: 1.4;
        }}
        .card h3 a {{ color: var(--text-main); text-decoration: none; }}
        .card h3 a:hover {{ color: var(--accent); }}
        
        .card p {{
            color: #475569;
            font-size: 0.925rem;
            margin: 0 0 1.5rem 0;
            flex-grow: 1;
        }}
        .card-footer {{
            font-size: 0.8rem;
            color: #94a3b8;
            border-top: 1px solid var(--border);
            padding-top: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        /* Highlighter Implementation */
        .highlight-brand {{
            background-color: var(--highlight);
            color: inherit;
            padding: 0 2px;
            border-radius: 3px;
            font-weight: 600;
        }}
        .no-data {{
            color: var(--text-muted);
            font-style: italic;
            grid-column: 1 / -1;
            padding: 3rem;
            text-align: center;
            background: var(--surface);
            border-radius: 12px;
            border: 2px dashed var(--border);
        }}
    </style>
</head>
<body>

<div class="navbar">
    <div class="navbar-container">
        <div>
            <h1>{SITE_TITLE}</h1>
            <p>Portfolio & Competitor Intelligence Portal</p>
        </div>
        <div class="meta-badge">
            Intel Edition: {edition_date}<br>
            Data Refresh: {timestamp} UTC
        </div>
    </div>
</div>

<div class="main-layout">

    <!-- EXECUTIVE SYNTHESIS MATRICES -->
    <div class="synthesis-container">
        <div class="synthesis-title">🎯 Macro Executive Summary & Portfolio Shifts</div>
        <ul class="synthesis-list">
"""

for bullet in synthesis_bullets:
    html += f"            <li>{bullet}</li>\n"

html += """        </ul>
    </div>

    <!-- HIGH PRIORITY STRATEGIC INTEL -->
    <section>
        <div class="section-title">⚡ High-Priority Competitive Threats & Top Stories</div>
        <div class="grid">
"""

top_stories = [a for a in articles if a["top_story"]][:12]
general_stories = [a for a in articles if not a["top_story"]]

if not top_stories:
    html += '            <div class="no-data">No major competitor infrastructure or M&A movements logged today.</div>'
else:
    for a in top_stories:
        impact_class = "tag-ma" if a["impact"] == "M&A Activity" else "tag-launch" if a["impact"] == "Product Launch" else "tag-reg" if a["impact"] == "Regulatory Change" else "tag-strat"
        html += f"""
            <div class="card" style="border-top: 4px solid var(--brand-primary);">
                <div>
                    <div class="card-tags">
                        <span class="tag tag-priority">Alert</span>
                        <span class="tag {impact_class}">{a['impact']}</span>
                        <span class="tag">{a['country']}</span>
                        <span class="tag">{a['category']}</span>
                    </div>
                    <h3><a href="{a['link']}" target="_blank">{a['title']}</a></h3>
                    <p>{a['summary']}</p>
                </div>
                <div class="card-footer">
                    <span>Source: {a['source']}</span>
                    <span>⏱️ {a['read_time']} min read</span>
                </div>
            </div>"""

html += """
        </div>
    </section>

    <!-- GEOGRAPHIC SUB-MARKETS -->
    <section>
        <div class="section-title">📍 Regional Market Activity</div>
"""

for country in COUNTRIES.keys():
    country_articles = [a for a in general_stories if a["country"] == country][:6]
    
    html += f"""
        <h3 style="margin: 2rem 0 1rem 0; font-size: 1.25rem; color: var(--brand-primary); font-weight:700;">{country} Market Updates</h3>
        <div class="grid" style="margin-bottom: 2.5rem;">
    """
    
    if not country_articles:
        html += '            <div class="no-data">No regional localized updates logged for this market matrix.</div>'
    else:
        for a in country_articles:
            impact_class = "tag-ma" if a["impact"] == "M&A Activity" else "tag-launch" if a["impact"] == "Product Launch" else "tag-reg" if a["impact"] == "Regulatory Change" else "tag-strat"
            html += f"""
                <div class="card">
                    <div>
                        <div class="card-tags">
                            <span class="tag {impact_class}">{a['impact']}</span>
                            <span class="tag">{a['category']}</span>
                        </div>
                        <h3><a href="{a['link']}" target="_blank">{a['title']}</a></h3>
                        <p>{a['summary']}</p>
                    </div>
                    <div class="card-footer">
                        <span>Source: {a['source']}</span>
                        <span>⏱️ {a['read_time']} min read</span>
                    </div>
                </div>"""
    html += "</div>"

html += """
    </section>
</div>

</body>
</html>
"""

# Output static deploy instances
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

with open(archive_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Pipeline executed successfully. Dashboard updated. Logs processed: {len(articles)}")


            



