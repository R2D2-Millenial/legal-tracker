"""
Juridigm Shift - Automated Regulatory & AI Intelligence Portal Generator
Maintains weekly digests, updates the persistent archive, and builds index.html.
"""

import json
import os
import re
from datetime import datetime

# --- Paths Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPDATES_FILE = os.path.join(DATA_DIR, "updates.json")
ARCHIVE_FILE = os.path.join(DATA_DIR, "archive.json")
OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")

CONSULT_URL = "https://juridigm.in/contact"

# Categories triggering the selective advisory CTA banner
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
                return json.load(f)
        except Exception as e:
            print(f"[!] Error loading {filepath}: {e}")
            return default
    return default


def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def sync_archive(new_updates):
    """Merges newly fetched updates into the cumulative archive.json without duplicates."""
    archive = load_json(ARCHIVE_FILE, default=[])
    seen_identifiers = set()

    # Deduplicate existing records by ID or normalized title
    for item in archive:
        identifier = item.get("id") or item.get("title", "").strip().lower()
        if identifier:
            seen_identifiers.add(identifier)

    added_count = 0
    for item in new_updates:
        identifier = item.get("id") or item.get("title", "").strip().lower()
        if identifier and identifier not in seen_identifiers:
            archive.append(item)
            seen_identifiers.add(identifier)
            added_count += 1

    # Sort archive newest first (by date)
    archive.sort(key=lambda x: x.get("date", ""), reverse=True)
    save_json(ARCHIVE_FILE, archive)
    print(f"[*] Archive synchronized: {added_count} new updates added (Total: {len(archive)})")
    return archive


def render_card(item):
    """Generates an individual liquid-glass regulatory update card."""
    title = item.get("title", "Untitled Regulatory Update")
    authority = item.get("authority", "Official Authority")
    domain = item.get("domain", "Regulatory Compliance")
    impact = item.get("impact", "Medium").capitalize()
    date_str = item.get("date", datetime.utcnow().strftime("%Y-%m-%d"))
    summary = item.get("summary", "No summary provided.")
    takeaway = item.get("in_house_takeaway") or item.get("takeaway", "")
    source_url = item.get("source_url") or item.get("link", "#")

    # Impact badge CSS class
    impact_class = "impact-medium"
    if impact.lower() == "high":
        impact_class = "impact-high"
    elif impact.lower() == "low":
        impact_class = "impact-low"

    # Contextual CTA Banner for Tech, AI & Privacy items
    selective_cta_html = ""
    if domain.strip().lower() in TECH_PRIVACY_DOMAINS or "ai" in domain.lower() or "dpdp" in domain.lower():
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
    <article class="tracker-card" data-domain="{domain.lower()}" data-impact="{impact.lower()}">
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
            {source_html}
        </div>
    </article>
    """


def build_html_dashboard(updates, archive_count):
    """Builds the comprehensive, responsive HTML document."""
    current_date = datetime.utcnow().strftime("%B %d, %Y")
    
    # Calculate Metrics
    total_count = len(updates)
    high_impact_count = sum(1 for u in updates if u.get("impact", "").lower() == "high")
    tech_privacy_count = sum(1 for u in updates if u.get("domain", "").strip().lower() in TECH_PRIVACY_DOMAINS or "ai" in u.get("domain", "").lower() or "dpdp" in u.get("domain", "").lower())
    corporate_count = sum(1 for u in updates if "corporate" in u.get("domain", "").lower() or "securities" in u.get("domain", "").lower() or "mca" in u.get("authority", "").lower() or "sebi" in u.get("authority", "").lower())

    cards_html = "\n".join(render_card(u) for u in updates) if updates else """
        <div class="no-records">
            <p>No new circulars found for this period. Historical records are preserved in the archive below.</p>
        </div>
    """

    # Template using safe token replacement to avoid CSS/JS brace conflicts
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Juridigm Shift — Indian Regulatory & AI Intelligence</title>

    <!-- Branded Shield Favicon (Embedded Vector) -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M50 12 L82 24 V48 C82 68 68 84 50 90 C32 84 18 68 18 48 V24 Z' fill='%23030712' stroke='%23d97706' stroke-width='6' stroke-linejoin='round'/%3E%3Cpath d='M38 34 H62 V66 H38 Z' fill='none' stroke='%23fbbf24' stroke-width='4' stroke-linejoin='round'/%3E%3Cpath d='M54 52 L59 57 L68 46' fill='none' stroke='%2338bdf8' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">

    <!-- Mobile Browser Header Theming -->
    <meta name="theme-color" content="#030712">
    <meta name="msapplication-navbutton-color" content="#030712">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

    <!-- Primary SEO Metadata -->
    <meta name="title" content="Juridigm Shift — Regulatory & Legal Tech Intelligence">
    <meta name="description" content="Automated regulatory tracking, AI governance, data privacy compliance, and commercial legal intelligence curated by Juridigm.">
    <link rel="canonical" href="https://shift.juridigm.in">

    <!-- Open Graph / LinkedIn, WhatsApp & Slack Link Previews -->
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

        /* Ambient Animated Mesh Background */
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

        .container {
            max-width: 1360px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }

        /* Top Brand Navigation Bar */
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
        }
        .logo-badge:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px var(--brand-gold-glow);
            border-color: var(--brand-amber);
        }
        .logo-badge svg { width: 32px; height: 32px; }

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

        /* Overview Headline */
        .portal-header {
            margin-bottom: 28px;
        }
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
            max-width: 800px;
            line-height: 1.5;
        }

        /* Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 32px;
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
        .metric-card .sub {
            font-size: 0.74rem;
            color: var(--text-muted);
        }

        /* Filter & Search Controls */
        .controls-panel {
            background: var(--glass-card);
            border: 1px solid var(--glass-border);
            border-radius: 18px;
            padding: 16px 20px;
            margin-bottom: 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
            backdrop-filter: blur(25px);
        }
        .filter-tabs {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .filter-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .filter-btn:hover, .filter-btn.active {
            background: rgba(217, 119, 6, 0.22);
            border-color: var(--brand-amber);
            color: #ffffff;
            box-shadow: 0 0 12px rgba(217, 119, 6, 0.3);
        }
        .search-box {
            position: relative;
            min-width: 280px;
        }
        .search-input {
            width: 100%;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            padding: 9px 14px;
            color: var(--text-main);
            font-size: 0.85rem;
            outline: none;
            transition: all 0.2s;
        }
        .search-input:focus {
            border-color: var(--brand-amber);
            box-shadow: 0 0 16px var(--brand-gold-glow);
        }

        /* Updates Grid */
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
        .impact-high {
            background: var(--impact-high-bg);
            color: var(--impact-high-text);
            border: 1px solid var(--impact-high-border);
        }
        .impact-medium {
            background: var(--impact-med-bg);
            color: var(--impact-med-text);
            border: 1px solid var(--impact-med-border);
        }
        .impact-low {
            background: var(--impact-low-bg);
            color: var(--impact-low-text);
            border: 1px solid var(--impact-low-border);
        }
        .update-date {
            font-size: 0.74rem;
            color: var(--text-muted);
            white-space: nowrap;
        }
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
        .takeaway-box p {
            font-size: 0.82rem;
            color: #f1f5f9;
            line-height: 1.45;
        }

        /* Selective Tech/Privacy Review Banner */
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
        .advisory-text {
            font-size: 0.78rem;
            color: #fde68a;
            line-height: 1.35;
        }
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
        .btn-review-cta:hover {
            background: #fbbf24;
            box-shadow: 0 0 10px rgba(251, 191, 36, 0.6);
        }

        .card-footer {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }
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
        .card-link:hover {
            color: #7dd3fc;
            text-decoration: underline;
        }

        .no-records {
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
            background: var(--glass-card);
            border-radius: 20px;
            border: 1px solid var(--glass-border);
        }

        /* Footer */
        .portal-footer {
            text-align: center;
            padding-top: 32px;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--text-muted);
            font-size: 0.82rem;
            line-height: 1.6;
        }
        .portal-footer a {
            color: var(--brand-amber);
            text-decoration: none;
        }
        .portal-footer a:hover {
            text-decoration: underline;
        }

        @media (max-width: 900px) {
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
            .updates-grid { grid-template-columns: 1fr; }
            .top-navbar { flex-direction: column; align-items: flex-start; gap: 16px; }
            .header-actions { width: 100%; justify-content: flex-start; }
            .controls-panel { flex-direction: column; align-items: stretch; }
            .search-box { min-width: 100%; }
        }
    </style>
</head>

<body>
    <!-- Background Ambient Layers -->
    <div class="bg-ambient-layer">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
    </div>

    <div class="container">
        <!-- Top Navigation -->
        <header class="top-navbar">
            <a href="https://juridigm.in" class="brand-cluster">
                <div class="logo-badge">
                    <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M50 12 L82 24 V48 C82 68 68 84 50 90 C32 84 18 68 18 48 V24 Z" stroke="#d97706" stroke-width="5" stroke-linejoin="round" />
                        <path d="M38 34 H62 V66 H38 Z" stroke="#fbbf24" stroke-width="3.5" stroke-linejoin="round" />
                        <path d="M54 52 L59 57 L68 46" stroke="#38bdf8" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" />
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

        <!-- Main Banner -->
        <section class="portal-header">
            <div class="tagline">Weekly Executive Intelligence Digest</div>
            <h2>Live Regulatory Trajectory</h2>
            <p>Automated intelligence tracking updates across DPDP regulations, MeitY directives, RBI FinTech circulars, SEBI compliances, and corporate commercial law in India.</p>
        </section>

        <!-- Metrics Overview -->
        <section class="metrics-grid">
            <div class="metric-card">
                <div class="title">Current Digest</div>
                <div class="val">__TOTAL_COUNT__</div>
                <div class="sub">Updates for week of __GENERATED_DATE__</div>
            </div>
            <div class="metric-card">
                <div class="title">High Impact Actions</div>
                <div class="val">__HIGH_IMPACT_COUNT__</div>
                <div class="sub">Immediate attention required</div>
            </div>
            <div class="metric-card">
                <div class="title">Tech & Privacy</div>
                <div class="val">__TECH_COUNT__</div>
                <div class="sub">AI, DPDP, Cyber & IT Law</div>
            </div>
            <div class="metric-card">
                <div class="title">Historical Archive</div>
                <div class="val">__ARCHIVE_COUNT__</div>
                <div class="sub">Preserved intelligence records</div>
            </div>
        </section>

        <!-- Filters & Search Toolbar -->
        <div class="controls-panel">
            <div class="filter-tabs">
                <button class="filter-btn active" onclick="filterDomain('all', this)">All Updates</button>
                <button class="filter-btn" onclick="filterDomain('ai & emerging tech', this)">AI & Tech</button>
                <button class="filter-btn" onclick="filterDomain('data privacy & dpdp', this)">Data Privacy</button>
                <button class="filter-btn" onclick="filterDomain('corporate', this)">Corporate & Securities</button>
                <button class="filter-btn" onclick="filterDomain('high-impact', this)">High Impact Only</button>
            </div>
            <div class="search-box">
                <input type="text" id="trackerSearch" class="search-input" placeholder="🔍 Search circulars, keywords, or authority..." onkeyup="handleSearch()">
            </div>
        </div>

        <!-- Cards Display Area -->
        <main class="updates-grid" id="updatesGrid">
            __CARDS_HTML__
        </main>

        <!-- Footer -->
        <footer class="portal-footer">
            <p>&copy; 2026 <strong>Juridigm Legal Advisory</strong>. All rights reserved.</p>
            <p>Intelligence synthesized for tech enterprises, in-house teams, and startup founders. Need bespoke review? <a href="https://juridigm.in/contact">Schedule a consultation &rarr;</a></p>
        </footer>
    </div>

    <!-- Client-Side Vanilla JS for Fast Filtering -->
    <script>
        let currentFilter = 'all';

        function filterDomain(domainKey, btn) {
            currentFilter = domainKey;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            applyFilters();
        }

        function handleSearch() {
            applyFilters();
        }

        function applyFilters() {
            const searchQuery = document.getElementById('trackerSearch').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.tracker-card');

            cards.forEach(card => {
                const domain = card.getAttribute('data-domain') || '';
                const impact = card.getAttribute('data-impact') || '';
                const cardText = card.innerText.toLowerCase();

                let matchesDomain = false;
                if (currentFilter === 'all') {
                    matchesDomain = true;
                } else if (currentFilter === 'high-impact') {
                    matchesDomain = (impact === 'high');
                } else if (currentFilter === 'corporate') {
                    matchesDomain = domain.includes('corporate') || domain.includes('securities') || domain.includes('finance') || domain.includes('tax');
                } else {
                    matchesDomain = domain.includes(currentFilter);
                }

                const matchesSearch = !searchQuery || cardText.includes(searchQuery);

                if (matchesDomain && matchesSearch) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""

    # Populate the placeholders
    output = html_template.replace("__TOTAL_COUNT__", str(total_count))
    output = output.replace("__HIGH_IMPACT_COUNT__", str(high_impact_count))
    output = output.replace("__TECH_COUNT__", str(tech_privacy_count))
    output = output.replace("__ARCHIVE_COUNT__", str(archive_count))
    output = output.replace("__GENERATED_DATE__", current_date)
    output = output.replace("__CARDS_HTML__", cards_html)

    return output


def main():
    print("[*] Starting Juridigm Shift Static Site Generator...")

    # Load new updates generated by analyzer
    new_updates = load_json(UPDATES_FILE, default=[])

    # Synchronize updates into permanent archive
    archive = sync_archive(new_updates)

    # Determine what to display on the active dashboard:
    # If this week has updates, show them. If empty, fall back to recent records from the archive.
    display_updates = new_updates if new_updates else archive[:10]

    # Render dashboard
    html_content = build_html_dashboard(display_updates, len(archive))

    # Write output to index.html in the repo root
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[✓] Successfully generated {OUTPUT_HTML} with {len(display_updates)} active updates.")


if __name__ == "__main__":
    main()
