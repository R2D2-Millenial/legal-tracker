"""
Juridigm Shift - Automated Regulatory & AI Intelligence Portal Generator
Maintains weekly digests, synchronizes persistent archive, and builds full filterable index.html.
"""

import json
import os
from datetime import datetime, timedelta

# --- Paths Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPDATES_FILE = os.path.join(DATA_DIR, "updates.json")
ARCHIVE_FILE = os.path.join(DATA_DIR, "archive.json")
OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")

CONSULT_URL = "https://juridigm.in/contact"

TECH_PRIVACY_DOMAINS = {
    "ai & emerging tech",
    "data privacy & dpdp",
    "technology & it law",
    "telecom & cyber",
    "contracts & cross-border",
    "employment & labor"
}


def load_json(filepath, default=None):
    if default is None:
        default = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else default
        except Exception as e:
            print(f"[!] Warning reading {filepath}: {e}")
            return default
    return default


def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Warning saving {filepath}: {e}")


def compute_week_label(date_str):
    """Derives a normalized 'Week of Mon DD, YYYY' string from a date."""
    now = datetime.utcnow()
    if not date_str:
        monday = now - timedelta(days=now.weekday())
        return f"Week of {monday.strftime('%b %d, %Y')}"
    try:
        clean_date = str(date_str).strip()[:10]
        dt = datetime.strptime(clean_date, "%Y-%m-%d")
        monday = dt - timedelta(days=dt.weekday())
        return f"Week of {monday.strftime('%b %d, %Y')}"
    except Exception:
        monday = now - timedelta(days=now.weekday())
        return f"Week of {monday.strftime('%b %d, %Y')}"


def sync_archive(new_updates):
    """Merges new weekly updates into archive.json, assigning week labels and deduplicating."""
    archive = load_json(ARCHIVE_FILE, default=[])
    seen_identifiers = set()

    # Normalize existing archive records
    for item in archive:
        if not isinstance(item, dict):
            continue
        if not item.get("week_label"):
            item["week_label"] = compute_week_label(item.get("date"))
        identifier = str(item.get("id") or item.get("title") or "").strip().lower()
        if identifier:
            seen_identifiers.add(identifier)

    added_count = 0
    if isinstance(new_updates, list):
        for item in new_updates:
            if not isinstance(item, dict):
                continue
            if not item.get("week_label"):
                item["week_label"] = compute_week_label(item.get("date"))
            identifier = str(item.get("id") or item.get("title") or "").strip().lower()
            if identifier and identifier not in seen_identifiers:
                archive.append(item)
                seen_identifiers.add(identifier)
                added_count += 1

    archive.sort(key=lambda x: str(x.get("date") or ""), reverse=True)
    save_json(ARCHIVE_FILE, archive)
    print(f"[*] Archive synchronized: {added_count} new updates added (Total: {len(archive)})")
    return archive


def render_card(item):
    """Generates an individual liquid-glass regulatory update card with null safety."""
    if not isinstance(item, dict):
        return ""

    title = str(item.get("title") or "Untitled Regulatory Update").strip()
    authority = str(item.get("authority") or "Official Authority").strip()
    domain = str(item.get("domain") or "Regulatory Compliance").strip()
    raw_impact = str(item.get("impact") or "Medium").strip().capitalize()
    date_str = str(item.get("date") or datetime.utcnow().strftime("%Y-%m-%d")).strip()
    summary = str(item.get("summary") or "No summary provided.").strip()
    takeaway = str(item.get("in_house_takeaway") or item.get("takeaway") or "").strip()
    source_url = str(item.get("source_url") or item.get("link") or "#").strip()
    week_label = str(item.get("week_label") or compute_week_label(date_str)).strip()

    impact = raw_impact if raw_impact in ["High", "Medium", "Low"] else "Medium"
    impact_class = "impact-medium"
    if impact.lower() == "high":
        impact_class = "impact-high"
    elif impact.lower() == "low":
        impact_class = "impact-low"

    # Contextual CTA Banner for Tech, AI & Privacy items
    dom_lower = domain.lower()
    selective_cta_html = ""
    if dom_lower in TECH_PRIVACY_DOMAINS or "ai" in dom_lower or "dpdp" in dom_lower:
        selective_cta_html = f"""
        <div class="card-advisory-cta">
            <div class="advisory-text">
                <strong>Advisory Impact:</strong> Requires in-house policy or contract review.
            </div>
            <a href="{CONSULT_URL}" target="_blank" rel="noopener noreferrer" class="btn-review-cta">
                Request Legal Review &rarr;
            </a>
        </div>
        """

    takeaway_html = ""
    if takeaway:
        takeaway_html = f"""
        <div class="takeaway-box">
            <span class="takeaway-badge">In-House Action</span>
            <p>{takeaway}</p>
        </div>
        """

    source_html = ""
    if source_url and source_url != "#":
        source_html = f"""
        <a href="{source_url}" target="_blank" rel="noopener noreferrer" class="card-link">
            <span>Read Circular / Source</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
        </a>
        """

    return f"""
    <article class="tracker-card" 
             data-week="{week_label}" 
             data-domain="{domain.lower()}" 
             data-authority="{authority.lower()}" 
             data-impact="{impact.lower()}">
        <div class="card-header">
            <div class="meta-row">
                <span class="badge badge-authority">{authority}</span>
                <span class="badge badge-domain">{domain}</span>
                <span class="badge {impact_class}">{impact} Impact</span>
            </div>
            <span class="update-date">{date_str}</span>
        </div>
        <h3 class="card-title">{title}</h3>
        <p class="card-summary">{summary}</p>
        {takeaway_html}
        {selective_cta_html}
        <div class="card-footer">
            <span class="card-week-tag">📅 {week_label}</span>
            {source_html}
        </div>
    </article>
    """


def build_html_dashboard(updates=None, archive_count=None, *args, **kwargs):
    """
    Builds the complete HTML dashboard interface.
    Accepts 0, 1, or 2 positional arguments to support direct workflow execution.
    Loads and merges cumulative historical data from archive.json.
    """
    # 1. Sync any incoming updates into archive.json
    incoming_updates = updates if isinstance(updates, list) else []
    archive = sync_archive(incoming_updates)

    # 2. Use all archive records for the complete searchable interface
    all_records = archive if archive else incoming_updates
    valid_updates = [u for u in all_records if isinstance(u, dict)]
    current_date = datetime.utcnow().strftime("%B %d, %Y")

    # 3. Extract Unique Weeks (Chronological, newest first)
    unique_weeks = []
    for u in valid_updates:
        wl = str(u.get("week_label") or "").strip()
        if wl and wl not in unique_weeks:
            unique_weeks.append(wl)
    if not unique_weeks:
        unique_weeks = [compute_week_label(None)]

    latest_week = unique_weeks[0]

    # 4. Extract Unique Authorities and Domains for Filter Dropdowns
    unique_authorities = sorted(list({str(u.get("authority") or "").strip() for u in valid_updates if str(u.get("authority") or "").strip()}))
    unique_domains = sorted(list({str(u.get("domain") or "").strip() for u in valid_updates if str(u.get("domain") or "").strip()}))

    week_options_html = "\n".join([f'<option value="{w}">{w}</option>' for w in unique_weeks])
    authority_options_html = "\n".join([f'<option value="{a.lower()}">{a}</option>' for a in unique_authorities])
    domain_options_html = "\n".join([f'<option value="{d.lower()}">{d}</option>' for d in unique_domains])

    # 5. Metrics Calculations
    current_week_updates = [u for u in valid_updates if str(u.get("week_label") or "").strip() == latest_week]
    current_digest_count = len(current_week_updates) if current_week_updates else len(valid_updates)
    high_impact_count = sum(1 for u in valid_updates if str(u.get("impact") or "").strip().lower() == "high")
    tech_count = sum(
        1 for u in valid_updates 
        if str(u.get("domain") or "").strip().lower() in TECH_PRIVACY_DOMAINS 
        or "ai" in str(u.get("domain") or "").lower() 
        or "dpdp" in str(u.get("domain") or "").lower()
    )
    total_archive_count = len(valid_updates)

    # 6. Render All Cards
    cards_html = "\n".join(filter(None, [render_card(u) for u in valid_updates])) if valid_updates else """
        <div class="no-records">
            <p>No regulatory records available in the tracker.</p>
        </div>
    """

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Juridigm Shift — Indian Regulatory & AI Intelligence</title>

    <!-- Juridigm Balanced Lens Vector Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M12 50 C 28 20, 72 20, 88 50 C 72 80, 28 80, 12 50 Z' fill='%23030712' stroke='%23d97706' stroke-width='6' stroke-linejoin='round'/%3E%3Cpath d='M32 50 C 40 34, 60 34, 68 50 C 60 66, 40 66, 32 50 Z' fill='none' stroke='%23fbbf24' stroke-width='4'/%3E%3Ccircle cx='50' cy='50' r='7' fill='%2338bdf8'/%3E%3C/svg%3E">

    <!-- Mobile Browser Header Theming -->
    <meta name="theme-color" content="#030712">
    <meta name="msapplication-navbutton-color" content="#030712">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

    <!-- Primary SEO Metadata -->
    <meta name="title" content="Juridigm Shift — Regulatory & Legal Tech Intelligence">
    <meta name="description" content="Automated regulatory tracking, AI governance, data privacy compliance, and commercial legal intelligence curated by Juridigm.">
    <link rel="canonical" href="https://shift.juridigm.in">

    <!-- Open Graph / LinkedIn & Social Link Previews -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://shift.juridigm.in">
    <meta property="og:site_name" content="Juridigm Shift">
    <meta property="og:title" content="Juridigm Shift — Regulatory & Legal Tech Intelligence">
    <meta property="og:description" content="Automated regulatory tracking, AI governance, data privacy compliance, and commercial legal intelligence curated by Juridigm.">

    <!-- Twitter Cards -->
    <meta name="twitter:card" content="summary">
    <meta name="twitter:url" content="https://shift.juridigm.in">
    <meta name="twitter:title" content="Juridigm Shift — Regulatory & Legal Tech Intelligence">
    <meta name="twitter:description" content="Automated regulatory tracking, AI governance, data privacy compliance, and commercial legal intelligence curated by Juridigm.">

    <style>
        :root {
            --bg-dark: #030712;
            --glass-card: rgba(15, 23, 42, 0.55);
            --glass-border: rgba(217, 119, 6, 0.22);
            --glass-border-hover: rgba(251, 191, 36, 0.55);
            --brand-gold: #d97706;
            --brand-gold-glow: rgba(217, 119, 6, 0.45);
            --brand-amber: #fbbf24;
            --brand-indigo: #4f46e5;
            --brand-violet: #7c3aed;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --impact-high-bg: rgba(239, 68, 68, 0.15);
            --impact-high-border: rgba(239, 68, 68, 0.45);
            --impact-high-text: #fca5a5;
            --impact-med-bg: rgba(245, 158, 11, 0.15);
            --impact-med-border: rgba(245, 158, 11, 0.45);
            --impact-med-text: #fde68a;
            --impact-low-bg: rgba(56, 189, 248, 0.15);
            --impact-low-border: rgba(56, 189, 248, 0.45);
            --impact-low-text: #7dd3fc;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            padding: 32px 24px;
            overflow-x: hidden;
            position: relative;
        }

        .bg-ambient-layer {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            z-index: -2;
            overflow: hidden;
            background: radial-gradient(circle at 50% -20%, #1e1b4b 0%, #030712 70%);
        }

        .orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(100px);
            opacity: 0.38;
            animation: floatOrb 22s ease-in-out infinite alternate;
        }
        .orb-1 { width: 550px; height: 550px; background: radial-gradient(circle, var(--brand-indigo), transparent 70%); top: -100px; left: -100px; }
        .orb-2 { width: 600px; height: 600px; background: radial-gradient(circle, var(--brand-violet), transparent 70%); bottom: -150px; right: -100px; animation-duration: 28s; animation-delay: -6s; }
        .orb-3 { width: 450px; height: 450px; background: radial-gradient(circle, var(--brand-gold-glow), transparent 70%); top: 40%; left: 35%; animation-duration: 18s; animation-delay: -12s; }

        @keyframes floatOrb {
            0% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(60px, 40px) scale(1.1); }
            100% { transform: translate(-40px, 80px) scale(0.95); }
        }

        .bg-watermark-logo {
            position: fixed;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 600px; height: 600px;
            z-index: -1;
            opacity: 0.03;
            pointer-events: none;
            animation: pulseWatermark 14s ease-in-out infinite alternate;
        }

        @keyframes pulseWatermark {
            0% { transform: translate(-50%, -50%) scale(0.96) rotate(0deg); opacity: 0.025; }
            50% { transform: translate(-50%, -52%) scale(1.04) rotate(1deg); opacity: 0.045; }
            100% { transform: translate(-50%, -48%) scale(0.98) rotate(-1deg); opacity: 0.03; }
        }

        .container {
            max-width: 1360px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }

        .top-navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 32px;
            padding-bottom: 24px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .brand-cluster {
            display: flex;
            align-items: center;
            gap: 16px;
            text-decoration: none;
        }

        .logo-badge {
            width: 54px; height: 54px;
            background: radial-gradient(circle at 50% 0%, rgba(217, 119, 6, 0.3) 0%, rgba(30, 27, 75, 0.6) 100%);
            border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            border: 1.5px solid var(--glass-border);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            transition: all 0.3s ease;
            overflow: hidden;
            flex-shrink: 0;
        }
        .logo-badge:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px var(--brand-gold-glow);
            border-color: var(--brand-amber);
        }
        .logo-badge svg { width: 34px; height: 34px; filter: drop-shadow(0 2px 6px rgba(217, 119, 6, 0.45)); }

        .brand-text h1 {
            font-size: 1.35rem;
            font-weight: 900;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .brand-text h1 span { color: var(--brand-amber); }
        .brand-text p {
            font-size: 0.76rem;
            color: var(--text-muted);
            letter-spacing: 1.2px;
            text-transform: uppercase;
            font-weight: 600;
            margin-top: 2px;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .btn-consult {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, rgba(217, 119, 6, 0.95) 0%, rgba(180, 83, 9, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: #ffffff;
            padding: 9px 18px;
            font-size: 0.85rem;
            font-weight: 700;
            border-radius: 10px;
            text-decoration: none;
            backdrop-filter: blur(20px);
            box-shadow: 0 6px 18px rgba(217, 119, 6, 0.35);
            transition: all 0.25s ease;
        }
        .btn-consult:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 24px rgba(217, 119, 6, 0.55);
            border-color: #ffffff;
        }

        .portal-header { margin-bottom: 28px; }
        .portal-header .tagline {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--brand-amber);
            margin-bottom: 8px;
        }
        .portal-header h2 {
            font-size: 2.3rem;
            font-weight: 900;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #ffffff 40%, #c7d2fe 75%, var(--brand-amber) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        .portal-header p {
            color: var(--text-muted);
            font-size: 0.96rem;
            max-width: 820px;
            line-height: 1.5;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: var(--glass-card);
            border: 1px solid var(--glass-border);
            border-radius: 18px;
            padding: 20px;
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
            position: relative;
            overflow: hidden;
            transition: all 0.25s ease;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            border-color: var(--glass-border-hover);
        }
        .metric-card .title {
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 8px;
        }
        .metric-card .val {
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 4px;
        }
        .metric-card .sub { font-size: 0.74rem; color: var(--text-muted); }

        .controls-panel {
            background: var(--glass-card);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 22px 24px;
            margin-bottom: 30px;
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
        }

        .filters-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 18px;
        }

        .control-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .control-label {
            font-size: 0.74rem;
            font-weight: 700;
            color: var(--brand-amber);
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        .filter-select, .search-input {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 10px 14px;
            color: var(--text-main);
            font-size: 0.86rem;
            outline: none;
            transition: all 0.25s ease;
            width: 100%;
        }

        .filter-select:focus, .search-input:focus {
            border-color: var(--brand-amber);
            box-shadow: 0 0 16px var(--brand-gold-glow);
        }

        .filter-select option { background: #0f172a; color: #f8fafc; }

        .search-row {
            display: flex;
            gap: 14px;
            align-items: center;
            margin-bottom: 14px;
        }
        .search-row .control-group { flex: 1; }

        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 14px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            font-size: 0.82rem;
            color: var(--text-muted);
            flex-wrap: wrap;
            gap: 10px;
        }

        .active-filter-tags {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .active-tag {
            background: rgba(217, 119, 6, 0.2);
            border: 1px solid rgba(251, 191, 36, 0.35);
            color: #fbbf24;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.74rem;
            font-weight: 600;
        }

        .btn-reset {
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #e2e8f0;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .btn-reset:hover {
            background: rgba(217, 119, 6, 0.2);
            border-color: var(--brand-amber);
            color: #ffffff;
        }

        .updates-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }
        .tracker-card {
            background: var(--glass-card);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
        }
        .tracker-card:hover {
            transform: translateY(-4px);
            border-color: var(--glass-border-hover);
            box-shadow: 0 20px 48px rgba(0, 0, 0, 0.6), 0 0 20px rgba(217, 119, 6, 0.2);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            gap: 12px;
        }
        .meta-row {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .badge {
            font-size: 0.7rem;
            font-weight: 700;
            padding: 4px 9px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .badge-authority {
            background: rgba(79, 70, 229, 0.2);
            color: #a5b4fc;
            border: 1px solid rgba(79, 70, 229, 0.4);
        }
        .badge-domain {
            background: rgba(124, 58, 237, 0.2);
            color: #c4b5fd;
            border: 1px solid rgba(124, 58, 237, 0.4);
        }
        .impact-high { background: var(--impact-high-bg); color: var(--impact-high-text); border: 1px solid var(--impact-high-border); }
        .impact-medium { background: var(--impact-med-bg); color: var(--impact-med-text); border: 1px solid var(--impact-med-border); }
        .impact-low { background: var(--impact-low-bg); color: var(--impact-low-text); border: 1px solid var(--impact-low-border); }
        .update-date { font-size: 0.74rem; color: var(--text-muted); white-space: nowrap; }
        .card-title {
            font-size: 1.15rem;
            font-weight: 700;
            line-height: 1.4;
            color: #ffffff;
            margin-bottom: 12px;
        }
        .card-summary {
            font-size: 0.88rem;
            line-height: 1.6;
            color: #cbd5e1;
            margin-bottom: 16px;
            flex-grow: 1;
        }
        .takeaway-box {
            background: rgba(0, 0, 0, 0.35);
            border-left: 3px solid var(--brand-amber);
            border-radius: 0 10px 10px 0;
            padding: 12px 14px;
            margin-bottom: 16px;
        }
        .takeaway-badge {
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 800;
            color: var(--brand-amber);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 4px;
        }
        .takeaway-box p { font-size: 0.82rem; color: #f1f5f9; line-height: 1.45; }

        .card-advisory-cta {
            background: rgba(217, 119, 6, 0.12);
            border: 1px dashed rgba(251, 191, 36, 0.45);
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        }
        .advisory-text { font-size: 0.78rem; color: #fde68a; line-height: 1.35; }
        .btn-review-cta {
            background: var(--brand-gold);
            color: #030712;
            padding: 5px 11px;
            border-radius: 6px;
            font-size: 0.74rem;
            font-weight: 800;
            text-decoration: none;
            white-space: nowrap;
            transition: all 0.2s ease;
        }
        .btn-review-cta:hover { background: #fbbf24; box-shadow: 0 0 10px rgba(251, 191, 36, 0.6); }

        .card-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }
        .card-week-tag { font-size: 0.74rem; color: var(--text-muted); font-weight: 500; }
        .card-link {
            color: #38bdf8;
            font-size: 0.8rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: color 0.2s;
        }
        .card-link:hover { color: #7dd3fc; text-decoration: underline; }

        .no-records {
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
            background: var(--glass-card);
            border-radius: 20px;
            border: 1px solid var(--glass-border);
        }

        .portal-footer {
            text-align: center;
            padding-top: 32px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--text-muted);
            font-size: 0.82rem;
            line-height: 1.6;
        }
        .portal-footer a { color: var(--brand-amber); text-decoration: none; }
        .portal-footer a:hover { text-decoration: underline; }

        @media (max-width: 1024px) {
            .filters-grid { grid-template-columns: repeat(2, 1fr); }
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
            .updates-grid { grid-template-columns: 1fr; }
        }

        @media (max-width: 768px) {
            .filters-grid { grid-template-columns: 1fr; }
            .top-navbar { flex-direction: column; align-items: flex-start; gap: 16px; }
            .header-actions { width: 100%; justify-content: flex-start; }
            .status-bar { flex-direction: column; align-items: flex-start; }
        }
    </style>
</head>

<body>
    <div class="bg-ambient-layer">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
    </div>

    <div class="bg-watermark-logo">
        <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 50 C 28 20, 72 20, 88 50 C 72 80, 28 80, 12 50 Z" stroke="#d97706" stroke-width="4" stroke-linejoin="round" />
            <path d="M32 50 C 40 34, 60 34, 68 50 C 60 66, 40 66, 32 50 Z" stroke="#fbbf24" stroke-width="3" stroke-linejoin="round" />
            <circle cx="50" cy="50" r="7" fill="#38bdf8" />
        </svg>
    </div>

    <div class="container">
        <header class="top-navbar">
            <a href="https://juridigm.in" class="brand-cluster">
                <div class="logo-badge">
                    <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="lensGold" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#fbbf24" />
                                <stop offset="100%" stop-color="#d97706" />
                            </linearGradient>
                        </defs>
                        <path d="M12 50 C 28 20, 72 20, 88 50 C 72 80, 28 80, 12 50 Z" stroke="url(#lensGold)" stroke-width="5" stroke-linejoin="round" />
                        <path d="M32 50 C 40 34, 60 34, 68 50 C 60 66, 40 66, 32 50 Z" stroke="#fbbf24" stroke-width="3" opacity="0.85" />
                        <circle cx="50" cy="50" r="6" fill="#38bdf8" />
                    </svg>
                </div>
                <div class="brand-text">
                    <h1>JURIDIGM <span>SHIFT</span></h1>
                    <p>Indian Regulatory & AI Intelligence</p>
                </div>
            </a>
            <div class="header-actions">
                <a href="https://juridigm.in/contact" target="_blank" rel="noopener noreferrer" class="btn-consult">
                    <span>Consult Juridigm</span>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </a>
            </div>
        </header>

        <section class="portal-header">
            <div class="tagline">Executive Intelligence Digest & Persistent Archive</div>
            <h2>Live Regulatory Trajectory</h2>
            <p>Automated intelligence tracking updates across DPDP regulations, MeitY directives, RBI FinTech circulars, SEBI compliances, and corporate commercial law in India.</p>
        </section>

        <section class="metrics-grid">
            <div class="metric-card">
                <div class="title">Current Digest</div>
                <div class="val">__CURRENT_DIGEST_COUNT__</div>
                <div class="sub">Latest edition: __LATEST_WEEK__</div>
            </div>
            <div class="metric-card">
                <div class="title">High Impact Actions</div>
                <div class="val">__HIGH_IMPACT_COUNT__</div>
                <div class="sub">Critical attention items across archive</div>
            </div>
            <div class="metric-card">
                <div class="title">Tech & Privacy</div>
                <div class="val">__TECH_COUNT__</div>
                <div class="sub">AI, DPDP, Cyber & IT Law updates</div>
            </div>
            <div class="metric-card">
                <div class="title">Historical Archive</div>
                <div class="val">__TOTAL_ARCHIVE_COUNT__</div>
                <div class="sub">Preserved intelligence records</div>
            </div>
        </section>

        <div class="controls-panel">
            <div class="filters-grid">
                <div class="control-group">
                    <label class="control-label" for="weekFilter">Timeline / Edition</label>
                    <select id="weekFilter" class="filter-select" onchange="applyFilters()">
                        <option value="current" selected>⚡ Current Week (Latest Edition)</option>
                        <option value="all">📚 All Editions (Complete History)</option>
                        <optgroup label="Past Individual Editions">
                            __WEEK_OPTIONS__
                        </optgroup>
                    </select>
                </div>

                <div class="control-group">
                    <label class="control-label" for="domainFilter">Topic / Legal Domain</label>
                    <select id="domainFilter" class="filter-select" onchange="applyFilters()">
                        <option value="all" selected>All Legal Domains</option>
                        __DOMAIN_OPTIONS__
                    </select>
                </div>

                <div class="control-group">
                    <label class="control-label" for="authorityFilter">Sector / Regulator</label>
                    <select id="authorityFilter" class="filter-select" onchange="applyFilters()">
                        <option value="all" selected>All Regulators & Authorities</option>
                        __AUTHORITY_OPTIONS__
                    </select>
                </div>

                <div class="control-group">
                    <label class="control-label" for="impactFilter">Impact Urgency</label>
                    <select id="impactFilter" class="filter-select" onchange="applyFilters()">
                        <option value="all" selected>All Impact Levels</option>
                        <option value="high">🔴 High Impact Only</option>
                        <option value="medium">🟡 Medium Impact</option>
                        <option value="low">🔵 Low Impact</option>
                    </select>
                </div>
            </div>

            <div class="search-row">
                <div class="control-group">
                    <input type="text" id="trackerSearch" class="search-input" placeholder="🔍 Search circular title, takeaway, regulation, or keywords..." onkeyup="applyFilters()">
                </div>
            </div>

            <div class="status-bar">
                <div class="active-filter-tags">
                    <span id="resultsCount">Loading updates...</span>
                    <span id="viewingTag" class="active-tag">Current Week</span>
                </div>
                <button class="btn-reset" onclick="resetFilters()">↺ Reset to Current Week</button>
            </div>
        </div>

        <main class="updates-grid" id="updatesGrid">
            __CARDS_HTML__
            <div id="emptyFilterNotice" class="no-records" style="display: none;">
                <p>No circulars match your current filter criteria.</p>
                <button class="btn-reset" style="margin-top: 14px;" onclick="resetFilters()">Reset to Current Week</button>
            </div>
        </main>

        <footer class="portal-footer">
            <p>&copy; 2026 <strong>Juridigm Legal Advisory</strong>. All rights reserved.</p>
            <p>Intelligence synthesized for tech enterprises, in-house teams, and startup founders. Need bespoke review? <a href="https://juridigm.in/contact">Schedule a consultation &rarr;</a></p>
        </footer>
    </div>

    <script>
        const LATEST_WEEK = "__LATEST_WEEK__";

        document.addEventListener("DOMContentLoaded", () => {
            applyFilters();
        });

        function applyFilters() {
            const selectedWeek = document.getElementById('weekFilter').value;
            const selectedDomain = document.getElementById('domainFilter').value.toLowerCase().trim();
            const selectedAuthority = document.getElementById('authorityFilter').value.toLowerCase().trim();
            const selectedImpact = document.getElementById('impactFilter').value.toLowerCase().trim();
            const searchQuery = document.getElementById('trackerSearch').value.toLowerCase().trim();

            const cards = document.querySelectorAll('.tracker-card');
            let visibleCount = 0;

            cards.forEach(card => {
                const cardWeek = (card.getAttribute('data-week') || '').trim();
                const cardDomain = (card.getAttribute('data-domain') || '').trim();
                const cardAuthority = (card.getAttribute('data-authority') || '').trim();
                const cardImpact = (card.getAttribute('data-impact') || '').trim();
                const cardText = card.innerText.toLowerCase();

                let matchesWeek = false;
                if (selectedWeek === 'all') {
                    matchesWeek = true;
                } else if (selectedWeek === 'current') {
                    matchesWeek = (cardWeek === LATEST_WEEK);
                } else {
                    matchesWeek = (cardWeek === selectedWeek);
                }

                let matchesDomain = (selectedDomain === 'all') || cardDomain.includes(selectedDomain);
                let matchesAuthority = (selectedAuthority === 'all') || cardAuthority.includes(selectedAuthority);
                let matchesImpact = (selectedImpact === 'all') || (cardImpact === selectedImpact);
                let matchesSearch = !searchQuery || cardText.includes(searchQuery);

                if (matchesWeek && matchesDomain && matchesAuthority && matchesImpact && matchesSearch) {
                    card.style.display = 'flex';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            const countElem = document.getElementById('resultsCount');
            if (countElem) {
                countElem.innerText = `Showing ${visibleCount} of ${cards.length} updates`;
            }

            const tagElem = document.getElementById('viewingTag');
            if (tagElem) {
                if (selectedWeek === 'current') {
                    tagElem.innerText = `Edition: ${LATEST_WEEK}`;
                } else if (selectedWeek === 'all') {
                    tagElem.innerText = "All Editions (Complete History)";
                } else {
                    tagElem.innerText = `Edition: ${selectedWeek}`;
                }
            }

            const emptyNotice = document.getElementById('emptyFilterNotice');
            if (emptyNotice) {
                emptyNotice.style.display = (visibleCount === 0) ? 'block' : 'none';
            }
        }

        function resetFilters() {
            document.getElementById('weekFilter').value = 'current';
            document.getElementById('domainFilter').value = 'all';
            document.getElementById('authorityFilter').value = 'all';
            document.getElementById('impactFilter').value = 'all';
            document.getElementById('trackerSearch').value = '';
            applyFilters();
        }
    </script>
</body>
</html>
"""

    output = html_template.replace("__CURRENT_DIGEST_COUNT__", str(current_digest_count))
    output = output.replace("__HIGH_IMPACT_COUNT__", str(high_impact_count))
    output = output.replace("__TECH_COUNT__", str(tech_count))
    output = output.replace("__TOTAL_ARCHIVE_COUNT__", str(total_archive_count))
    output = output.replace("__LATEST_WEEK__", latest_week)
    output = output.replace("__WEEK_OPTIONS__", week_options_html)
    output = output.replace("__DOMAIN_OPTIONS__", domain_options_html)
    output = output.replace("__AUTHORITY_OPTIONS__", authority_options_html)
    output = output.replace("__CARDS_HTML__", cards_html)

    # Auto-write to index.html if caller doesn't explicitly handle the return string
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(output)

    return output


def main():
    print("[*] Starting Juridigm Shift Static Site Generator...")
    new_updates = load_json(UPDATES_FILE, default=[])
    build_html_dashboard(new_updates)
    print(f"[✓] Successfully generated {OUTPUT_HTML}.")


if __name__ == "__main__":
    main()
