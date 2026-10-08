def build_html_dashboard(updates, week_label):
    cards_html = ""
    for item in updates:
        impact = item.get("impact_level", "Medium")
        
        # Risk badges calibrated to the navy/gold palette
        if impact == "High":
            badge_style = "background: #fef2f2; color: #991b1b; border: 1px solid #fecaca;"
        elif impact == "Low":
            badge_style = "background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;"
        else:
            badge_style = "background: #fdfbf7; color: #926f27; border: 1px solid #e8d7a7;"

        action_lis = "".join(f"<li>{act.lstrip('•-* ').strip()}</li>" for act in item.get("inhouse_action_items", []))

        cards_html += f"""
        <article class="update-card" data-authority="{item.get('authority', '')}" data-domain="{item.get('law_domain', '')}" data-impact="{impact}">
            <div class="card-meta">
                <div class="meta-tags">
                    <span class="badge" style="{badge_style}">{impact} Impact</span>
                    <span class="badge badge-navy">{item.get('authority', 'General')}</span>
                    <span class="badge badge-indigo">{item.get('law_domain', 'General')}</span>
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
                <span>Sector: <strong>{item.get('sector', 'General')}</strong></span>
                <a href="{item.get('source_url', '#')}" target="_blank" rel="noopener noreferrer">Primary Gazette / Source &rarr;</a>
            </div>
        </article>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Juridigm Shift — Regulatory Intelligence | {week_label}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f8fafc;
            color: #0f172a;
            line-height: 1.55;
            padding: 40px 16px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 2px solid #0a192f;
            padding-bottom: 20px;
            margin-bottom: 28px;
            gap: 16px;
        }}
        .brand-eyebrow {{
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: #c5a059;
            margin-bottom: 4px;
        }}
        .brand-title {{
            font-size: 30px;
            font-weight: 800;
            color: #0a192f;
            letter-spacing: -0.02em;
            line-height: 1.1;
        }}
        .brand-title span {{
            color: #c5a059;
            font-weight: 700;
            margin-left: 2px;
        }}
        .subtitle {{
            font-size: 13px;
            color: #475569;
            margin-top: 6px;
        }}
        .print-btn {{
            background: #0a192f;
            color: #ffffff;
            border: 1px solid #c5a059;
            padding: 10px 18px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.02em;
            border-radius: 6px;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        .print-btn:hover {{
            background: #1e3a8a;
            border-color: #e8c872;
            box-shadow: 0 2px 8px rgba(10, 25, 47, 0.15);
        }}
        .filter-panel {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-top: 3px solid #c5a059;
            border-radius: 10px;
            padding: 18px 22px;
            margin-bottom: 28px;
            box-shadow: 0 2px 6px rgba(10, 25, 47, 0.04);
        }}
        .filter-title {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: #0a192f;
            margin-bottom: 12px;
            letter-spacing: 0.08em;
        }}
        .filter-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }}
        select, .reset-btn {{
            font-size: 13px;
            padding: 8px 14px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            background: #ffffff;
            color: #0a192f;
            outline: none;
            transition: border-color 0.15s ease;
        }}
        select:focus {{
            border-color: #c5a059;
        }}
        .reset-btn {{
            background: #f8fafc;
            color: #475569;
            cursor: pointer;
            font-weight: 600;
        }}
        .reset-btn:hover {{
            background: #e2e8f0;
            color: #0a192f;
        }}
        .update-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}
        .update-card:hover {{
            border-color: #c5a059;
            box-shadow: 0 4px 14px rgba(197, 160, 89, 0.12);
        }}
        .card-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 14px;
        }}
        .meta-tags {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 9999px;
            letter-spacing: 0.03em;
        }}
        .badge-navy {{
            background: #0a192f;
            color: #f8fafc;
            border: 1px solid #0a192f;
        }}
        .badge-indigo {{
            background: #eff6ff;
            color: #1e3a8a;
            border: 1px solid #bfdbfe;
        }}
        .effective-date {{
            font-size: 12px;
            color: #64748b;
        }}
        .card-title {{
            font-size: 18.5px;
            font-weight: 700;
            color: #0a192f;
            margin-bottom: 16px;
            line-height: 1.35;
        }}
        .shift-box {{
            background: #fdfbf7;
            border-left: 3.5px solid #c5a059;
            padding: 14px 18px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 16px;
        }}
        .shift-box p {{
            font-size: 14px;
            color: #334155;
            line-height: 1.55;
        }}
        .label-gold {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: #926f27;
            margin-bottom: 5px;
        }}
        .label-navy {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: #0a192f;
            margin-bottom: 6px;
        }}
        .action-box {{
            margin-bottom: 16px;
        }}
        .action-box ul {{
            list-style-type: disc;
            padding-left: 20px;
        }}
        .action-box li {{
            font-size: 13.5px;
            color: #1e293b;
            margin-bottom: 5px;
        }}
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #f1f5f9;
            padding-top: 14px;
            font-size: 12.5px;
            color: #64748b;
        }}
        .card-footer strong {{
            color: #0a192f;
        }}
        .card-footer a {{
            color: #1e3a8a;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.15s ease;
        }}
        .card-footer a:hover {{
            color: #c5a059;
            text-decoration: underline;
        }}
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background: #fff; padding: 0; }}
            .update-card {{ break-inside: avoid; border: 1px solid #94a3b8; box-shadow: none; margin-bottom: 20px; }}
            .shift-box {{ border-left-color: #0a192f; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <div class="brand-eyebrow">Juridigm Intelligence Network</div>
                <h1 class="brand-title">JURIDIGM <span>SHIFT</span></h1>
                <p class="subtitle">Weekly Regulatory, Privacy & AI Intelligence Briefing | {week_label}</p>
            </div>
            <button class="print-btn no-print" onclick="window.print()">Export Memo (PDF)</button>
        </header>

        <section class="filter-panel no-print">
            <div class="filter-title">Filter by Compliance Domain & Risk Level</div>
            <div class="filter-row">
                <select id="impactFilter" onchange="applyFilters()">
                    <option value="ALL">All Impact Levels</option>
                    <option value="High">High Impact Only</option>
                    <option value="Medium">Medium Impact</option>
                    <option value="Low">Low Impact</option>
                </select>
                <select id="domainFilter" onchange="applyFilters()">
                    <option value="ALL">All Legal Domains</option>
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

        <main id="cardsContainer">
            {cards_html}
        </main>
    </div>

    <script>
        function applyFilters() {{
            const impact = document.getElementById('impactFilter').value;
            const domain = document.getElementById('domainFilter').value;
            const cards = document.querySelectorAll('.update-card');

            cards.forEach(card => {{
                const cardImpact = card.getAttribute('data-impact');
                const cardDomain = card.getAttribute('data-domain');
                const matchesImpact = impact === 'ALL' || cardImpact === impact;
                const matchesDomain = domain === 'ALL' || cardDomain.includes(domain);
                card.style.display = (matchesImpact && matchesDomain) ? 'block' : 'none';
            }});
        }}

        function resetFilters() {{
            document.getElementById('impactFilter').value = 'ALL';
            document.getElementById('domainFilter').value = 'ALL';
            applyFilters();
        }}
    </script>
</body>
</html>"""
    return html
