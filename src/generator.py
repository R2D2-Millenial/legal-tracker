def build_html_dashboard(updates, week_label):
    cards_html = ""
    for item in updates:
        badge_color = {
            "High": "bg-red-100 text-red-800 border-red-300",
            "Medium": "bg-amber-100 text-amber-800 border-amber-300",
            "Low": "bg-blue-100 text-blue-800 border-blue-300"
        }.get(item["impact_level"], "bg-slate-100 text-slate-800")

        actions = "".join([f"<li class='text-slate-700 text-sm'>• {act}</li>" for act in item["inhouse_action_items"]])

        cards_html += f"""
        <article class="update-card border border-slate-200 rounded-xl p-6 bg-white shadow-sm mb-6"
                 data-authority="{item['authority']}"
                 data-domain="{item['law_domain']}"
                 data-impact="{item['impact_level']}">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div class="flex items-center gap-2">
                    <span class="px-2.5 py-1 text-xs font-semibold rounded-full border {badge_color}">{item['impact_level']} Impact</span>
                    <span class="text-xs font-semibold uppercase tracking-wider text-slate-600 bg-slate-100 px-2 py-0.5 rounded">{item['authority']}</span>
                    <span class="text-xs text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">{item['law_domain']}</span>
                </div>
                <span class="text-xs text-slate-500 font-medium">Effective: {item['effective_date']}</span>
            </div>

            <h3 class="text-lg font-bold text-slate-900 mb-2">{item['title']}</h3>
            
            <div class="mb-4 bg-slate-50 p-3.5 rounded-lg border border-slate-100 text-sm">
                <p class="font-semibold text-slate-900 text-xs mb-1 uppercase tracking-wide">Shift in Legal Position:</p>
                <p class="text-slate-700 leading-relaxed">{item['what_changed']}</p>
            </div>

            <div class="mb-4">
                <p class="font-semibold text-slate-900 text-xs mb-1 uppercase tracking-wide">Legal & Compliance Action Items:</p>
                <ul class="space-y-1">{actions}</ul>
            </div>

            <div class="pt-3 border-t border-slate-100 flex justify-between items-center text-xs">
                <span class="text-slate-500">Sector: <strong>{item['sector']}</strong></span>
                <a href="{item['source_url']}" target="_blank" class="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center gap-1">Read Official Source &rarr;</a>
            </div>
        </article>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indian Corporate Legal Intelligence — {week_label}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background: white; }}
            .update-card {{ break-inside: avoid; border: 1px solid #ccc; box-shadow: none; margin-bottom: 1.5rem; }}
        }}
    </style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen py-10 px-4 sm:px-8">
    <div class="max-w-5xl mx-auto">
        <header class="mb-8 border-b border-slate-200 pb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
                <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">In-House Regulatory Intelligence Hub</h1>
                <p class="text-slate-600 text-sm mt-1">Weekly Regulatory & Judicial Briefing for Counsel | {week_label}</p>
            </div>
            <div class="no-print flex items-center gap-3">
                <button onclick="window.print()" class="px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded-lg hover:bg-slate-800 transition">
                    Export / Print as PDF
                </button>
            </div>
        </header>

        <!-- Dynamic Filter Controls -->
        <section class="no-print bg-white border border-slate-200 rounded-xl p-4 mb-8 shadow-sm">
            <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Filter Intelligence Feed</h2>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <select id="impactFilter" onchange="applyFilters()" class="text-xs border rounded-lg p-2 bg-white text-slate-800 border-slate-300">
                    <option value="ALL">All Impact Levels</option>
                    <option value="High">High Impact Only</option>
                    <option value="Medium">Medium Impact</option>
                    <option value="Low">Low Impact</option>
                </select>
                <select id="domainFilter" onchange="applyFilters()" class="text-xs border rounded-lg p-2 bg-white text-slate-800 border-slate-300">
                    <option value="ALL">All Legal Domains</option>
                    <option value="Corporate">Corporate / MCA</option>
                    <option value="Securities">Securities / SEBI</option>
                    <option value="Employment & Labour">Labour & Employment</option>
                    <option value="Privacy & Tech">Privacy & MeitY</option>
                    <option value="Foreign Exchange">RBI / FEMA</option>
                </select>
                <button onclick="resetFilters()" class="text-xs text-slate-600 hover:text-slate-900 border border-slate-200 rounded-lg p-2">
                    Reset Filters
                </button>
            </div>
        </section>

        <!-- Digest Cards Container -->
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
                const matchesDomain = domain === 'ALL' || cardDomain === domain;
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
