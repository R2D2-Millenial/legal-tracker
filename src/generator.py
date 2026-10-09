import json
import os
import re
import urllib.request

def get_saved_history():
    if os.path.exists("archive.json"):
        try:
            with open("archive.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    try:
        url = "https://r2d2-millenial.github.io/legal-tracker/"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as resp:
            html_text = resp.read().decode('utf-8')
            match = re.search(r'<script id="archive-data" type="application/json">(.*?)</script>', html_text, re.DOTALL)
            if match:
                return json.loads(match.group(1).strip())
    except Exception:
        pass
    return []

def build_html_dashboard(updates, week_label):
    for item in updates:
        item["week_label"] = item.get("week_label") or week_label

    history = get_saved_history()
    all_items = []
    seen = set()

    for item in updates + history:
        title_key = item.get("title", "").strip().lower()
        if title_key and title_key not in seen:
            seen.add(title_key)
            all_items.append(item)
        elif not title_key:
            all_items.append(item)

    try:
        with open("archive.json", "w", encoding="utf-8") as f:
            json.dump(all_items, f, indent=2)
    except Exception:
        pass

    weeks = []
    for it in all_items:
        w = it.get("week_label", week_label)
        if w and w not in weeks:
            weeks.append(w)

    week_options = f'<option value="{week_label}" selected>{week_label} (Latest)</option>'
    week_options += '<option value="ALL">All Editions (Full Archive)</option>'
    for w in weeks:
        if w != week_label:
            week_options += f'<option value="{w}">{w}</option>'

    # Active practice domains for Juridigm's advisory:
    TECH_PRACTICE_KEYWORDS = [
        "data privacy", "dpdp", "ai", "artificial intelligence", 
        "technology", "tech", "cybersecurity", "employment", 
        "labour", "contract", "software", "intellectual property"
    ]

    cards_html = ""
    for item in all_items:
        impact = item.get("impact_level", "Medium")
        item_week = item.get("week_label", week_label)
        domain = item.get("law_domain", "General")
        sector = item.get("sector", "General")

        badge_style = {
            "High": "background:#fef2f2;color:#991b1b;border:1px solid #fecaca;",
            "Low": "background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;",
        }.get(impact, "background:#fdfbf7;color:#926f27;border:1px solid #e8d7a7;")

        action_lis = "".join(f"<li>{act.lstrip('•-* ').strip()}</li>" for act in item.get("inhouse_action_items", []))

        # Check if card touches Tech, AI, DPDP, Employment, or Contracts
        combined_text = f"{domain} {sector} {item.get('title', '')}".lower()
        is_relevant_tech_matter = any(kw in combined_text for kw in TECH_PRACTICE_KEYWORDS)
        is_excluded_industry = any(ex in combined_text for ex in ["biodiversity", "pharmaceutical", "heavy industry", "factory inspection"])
        
        cta_bar_html = ""
        if is_relevant_tech_matter and not is_excluded_industry:
            cta_bar_html = """
            <div class="card-cta-bar no-print">
                <span>Reviewing contracts, employee IP, or compliance in this area?</span>
                <a href="https://juridigm.in/contact" target="_blank" rel="noopener noreferrer">Request Legal Review &rarr;</a>
            </div>"""

        cards_html += f"""
        <article class="update-card" data-week="{item_week}" data-authority="{item.get('authority', '')}" data-domain="{domain}" data-impact="{impact}">
            <div class="card-meta">
                <div class="meta-tags">
                    <span class="badge badge-week">{item_week}</span>
                    <span class="badge" style="{badge_style}">{impact} Impact</span>
                    <span class="badge badge-navy">{item.get('authority', 'General')}</span>
                    <span class="badge badge-indigo">{domain}</span>
                </div>
                <div class="effective-date">Effective: <strong>{item.get('effective_date', 'Immediate')}</strong></div>
            </div>
            <h2 class="card-title">{item.get('title', '')}</h2>
            <div class="shift-box">
                <div class="label-gold">Regulatory Shift</div>
                <p>{item.get('what_changed', '')}</p>
            </div>
            <div class="action-box">
                <div class="label-navy">Counsel Action Items</div>
                <ul>{action_lis}</ul>
            </div>
            <div class="card-footer">
                <span>Sector: <strong>{sector}</strong></span>
                <a href="{item.get('source_url', '#')}" target="_blank" rel="noopener noreferrer">Primary Gazette / Source &rarr;</a>
            </div>
            {cta_bar_html}
        </article>"""

    archive_json_str = json.dumps(all_items).replace("</script>", "<\\/script>")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Juridigm Shift — Regulatory Intelligence Hub</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.55; padding: 40px 16px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{ display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #0a192f; padding-bottom: 20px; margin-bottom: 28px; gap: 16px; flex-wrap: wrap; }}
        .brand-eyebrow {{ font-size: 11px; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: #c5a059; margin-bottom: 4px; }}
        .brand-title {{ font-size: 30px; font-weight: 800; color: #0a192f; letter-spacing: -0.02em; line-height: 1.1; }}
        .brand-title span {{ color: #c5a059; font-weight: 700; }}
        .subtitle {{ font-size: 13px; color: #475569; margin-top: 6px; }}
        .header-actions {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
        .cta-btn {{ background: #c5a059; color: #0a192f; border: 1px solid #c5a059; padding: 9px 15px; font-size: 12px; font-weight: 700; border-radius: 6px; text-decoration: none; cursor: pointer; transition: all 0.2s ease; }}
        .cta-btn:hover {{ background: #d4b26f; color: #0a192f; }}
        .print-btn {{ background: #0a192f; color: #fff; border: 1px solid #c5a059; padding: 9px 16px; font-size: 12px; font-weight: 600; border-radius: 6px; cursor: pointer; white-space: nowrap; }}
        .print-btn:hover {{ background: #1e3a8a; border-color: #e8c872; }}
        .filter-panel {{ background: #fff; border: 1px solid #e2e8f0; border-top: 3px solid #c5a059; border-radius: 10px; padding: 18px 22px; margin-bottom: 28px; box-shadow: 0 2px 6px rgba(10,25,47,0.04); }}
        .filter-title {{ font-size: 11px; font-weight: 700; text-transform: uppercase; color: #0a192f; margin-bottom: 12px; letter-spacing: 0.08em; }}
        .filter-row {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        select, input[type="text"], .reset-btn {{ font-size: 13px; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; background: #fff; color: #0a192f; outline: none; }}
        select:focus, input[type="text"]:focus {{ border-color: #c5a059; }}
        .search-box {{ flex: 1; min-width: 200px; }}
        .reset-btn {{ background: #f8fafc; color: #475569; cursor: pointer; font-weight: 600; }}
        .reset-btn:hover {{ background: #e2e8f0; color: #0a192f; }}
        .update-card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 26px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(10,25,47,0.03); transition: border-color 0.2s ease; }}
        .update-card:hover {{ border-color: #c5a059; }}
        .card-meta {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }}
        .meta-tags {{ display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
        .badge {{ font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 9999px; letter-spacing: 0.03em; }}
        .badge-week {{ background: #0a192f; color: #c5a059; border: 1px solid #c5a059; }}
        .badge-navy {{ background: #0a192f; color: #f8fafc; }}
        .badge-indigo {{ background: #eff6ff; color: #1e3a8a; border: 1px solid #bfdbfe; }}
        .effective-date {{ font-size: 12px; color: #64748b; }}
        .card-title {{ font-size: 18.5px; font-weight: 700; color: #0a192f; margin-bottom: 16px; line-height: 1.35; }}
        .shift-box {{ background: #fdfbf7; border-left: 3.5px solid #c5a059; padding: 14px 18px; border-radius: 0 8px 8px 0; margin-bottom: 16px; }}
        .shift-box p {{ font-size: 14px; color: #334155; line-height: 1.55; }}
        .label-gold {{ font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.07em; color: #926f27; margin-bottom: 5px; }}
        .label-navy {{ font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.07em; color: #0a192f; margin-bottom: 6px; }}
        .action-box {{ margin-bottom: 16px; }}
        .action-box ul {{ list-style-type: disc; padding-left: 20px; }}
        .action-box li {{ font-size: 13.5px; color: #1e293b; margin-bottom: 5px; }}
        .card-footer {{ display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 14px; font-size: 12.5px; color: #64748b; }}
        .card-footer strong {{ color: #0a192f; }}
        .card-footer a {{ color: #1e3a8a; text-decoration: none; font-weight: 600; }}
        .card-footer a:hover {{ color: #c5a059; text-decoration: underline; }}
        .card-cta-bar {{ background: #fdfbf7; border: 1px dashed #e8d7a7; border-radius: 6px; padding: 10px 14px; margin-top: 14px; font-size: 12.5px; color: #64748b; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px; }}
        .card-cta-bar a {{ color: #926f27; font-weight: 700; text-decoration: none; }}
        .card-cta-bar a:hover {{ color: #0a192f; text-decoration: underline; }}
        @media print {{ .no-print {{ display: none !important; }} body {{ background: #fff; padding: 0; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <div class="brand-eyebrow">Juridigm Intelligence Network</div>
                <h1 class="brand-title">JURIDIGM <span>SHIFT</span></h1>
                <p class="subtitle">Weekly Regulatory, Privacy & AI Intelligence Briefing</p>
            </div>
            <div class="header-actions no-print">
                <a href="https://juridigm.in/contact" target="_blank" rel="noopener noreferrer" class="cta-btn">Consult Juridigm &rarr;</a>
                <button class="print-btn" onclick="window.print()">Export Memo (PDF)</button>
            </div>
        </header>

        <section class="filter-panel no-print">
            <div class="filter-title">Archive Search & Multi-Domain Filter</div>
            <div class="filter-row">
                <input type="text" id="searchInput" class="search-box" placeholder="Search keywords, laws, rules..." oninput="applyFilters()">
                <select id="weekFilter" onchange="applyFilters()">{week_options}</select>
                <select id="impactFilter" onchange="applyFilters()">
                    <option value="ALL">All Impact</option>
                    <option value="High">High Impact</option>
                    <option value="Medium">Medium Impact</option>
                    <option value="Low">Low Impact</option>
                </select>
                <select id="domainFilter" onchange="applyFilters()">
                    <option value="ALL">All Domains</option>
                    <option value="Data Privacy & DPDP">Data Privacy & DPDP</option>
                    <option value="AI & Emerging Tech">AI & Emerging Tech</option>
                    <option value="Corporate">Corporate / MCA</option>
                    <option value="Securities">Securities / SEBI</option>
                    <option value="Employment & Labour">Labour & Employment</option>
                    <option value="Foreign Exchange">RBI / FEMA</option>
                </select>
                <button class="reset-btn" onclick="resetFilters()">Reset</button>
            </div>
        </section>

        <main id="cardsContainer">{cards_html}</main>
    </div>

    <script id="archive-data" type="application/json">{archive_json_str}</script>
    <script>
        function applyFilters() {{
            const week = document.getElementById('weekFilter').value;
            const impact = document.getElementById('impactFilter').value;
            const domain = document.getElementById('domainFilter').value;
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.update-card');

            cards.forEach(card => {{
                const cardWeek = card.getAttribute('data-week');
                const cardImpact = card.getAttribute('data-impact');
                const cardDomain = card.getAttribute('data-domain');
                const cardText = card.innerText.toLowerCase();

                const matchesWeek = (week === 'ALL' || cardWeek === week);
                const matchesImpact = (impact === 'ALL' || cardImpact === impact);
                const matchesDomain = (domain === 'ALL' || cardDomain.includes(domain));
                const matchesSearch = (!query || cardText.includes(query));

                card.style.display = (matchesWeek && matchesImpact && matchesDomain && matchesSearch) ? 'block' : 'none';
            }});
        }}

        function resetFilters() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('weekFilter').value = '{week_label}';
            document.getElementById('impactFilter').value = 'ALL';
            document.getElementById('domainFilter').value = 'ALL';
            applyFilters();
        }}

        applyFilters();
    </script>
</body>
</html>"""
    return html
