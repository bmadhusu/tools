#!/usr/bin/env python3
"""
Build the index HTML page from gathered_links.json.
Lists all tools with links to use them and view their source.
"""

import html
import json
from datetime import datetime

GITHUB_REPO = "bmadhusu/tools"


def format_date(iso_date: str) -> str:
    """Format ISO date to readable format."""
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime('%b %d, %Y')
    except Exception:
        return iso_date


def build_index():
    """Build the index HTML page."""
    # Load gathered data
    try:
        with open('gathered_links.json', 'r', encoding='utf-8') as f:
            tools = json.load(f)
    except FileNotFoundError:
        print("Error: gathered_links.json not found. Run gather_links.py first.")
        return

    # Build tool cards
    tool_cards = []
    for tool in tools:
        description = html.escape(tool['description']) if tool['description'] else 'A useful tool.'
        updated = format_date(tool['updated']) if tool['updated'] else ''

        tool_cards.append(f'''
            <article class="tool-card">
                <h2><a href="{tool['slug']}.html">{html.escape(tool['title'])}</a></h2>
                <p class="description">{description}</p>
                <div class="meta">
                    <span class="updated">Updated {updated}</span>
                    <a href="colophon.html#{tool['slug']}" class="history-link">History</a>
                </div>
            </article>
        ''')

    # Build full HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tools</title>
    <style>
        :root {{
            --bg: #ffffff;
            --text: #1a1a1a;
            --muted: #666666;
            --border: #e5e5e5;
            --link: #0066cc;
            --link-hover: #0052a3;
            --card-bg: #fafafa;
            --accent: #6366f1;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg: #1a1a1a;
                --text: #e5e5e5;
                --muted: #999999;
                --border: #333333;
                --link: #66b3ff;
                --link-hover: #99ccff;
                --card-bg: #242424;
                --accent: #818cf8;
            }}
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem 1rem;
            background: var(--bg);
            color: var(--text);
        }}

        header {{
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 2px solid var(--accent);
        }}

        header h1 {{
            margin: 0 0 0.5rem 0;
            font-size: 2rem;
        }}

        header p {{
            margin: 0;
            color: var(--muted);
        }}

        nav {{
            margin-top: 1rem;
        }}

        nav a {{
            margin-right: 1rem;
            color: var(--link);
            text-decoration: none;
        }}

        nav a:hover {{
            text-decoration: underline;
        }}

        .tools-grid {{
            display: grid;
            gap: 1.5rem;
        }}

        .tool-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
        }}

        .tool-card h2 {{
            margin: 0 0 0.5rem 0;
            font-size: 1.25rem;
        }}

        .tool-card h2 a {{
            color: var(--text);
            text-decoration: none;
        }}

        .tool-card h2 a:hover {{
            color: var(--link);
        }}

        .tool-card .description {{
            margin: 0 0 1rem 0;
            color: var(--muted);
            font-size: 0.95rem;
        }}

        .tool-card .meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
        }}

        .tool-card .updated {{
            color: var(--muted);
        }}

        .tool-card .history-link {{
            color: var(--link);
            text-decoration: none;
        }}

        .tool-card .history-link:hover {{
            text-decoration: underline;
        }}

        footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
            color: var(--muted);
            font-size: 0.9rem;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 1rem;
            }}

            header h1 {{
                font-size: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Tools</h1>
        <p>A collection of {len(tools)} useful tool{'s' if len(tools) != 1 else ''} built with AI assistance.</p>
        <nav>
            <a href="colophon.html">Colophon</a>
            <a href="https://github.com/{GITHUB_REPO}">GitHub</a>
        </nav>
    </header>

    <main class="tools-grid">
        {''.join(tool_cards)}
    </main>

    <footer>
        <p>
            View the <a href="colophon.html">colophon</a> for development history
            and AI session transcripts.
        </p>
    </footer>
</body>
</html>
'''

    # Write output
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Built index.html with {len(tools)} tool(s)")


if __name__ == '__main__':
    build_index()
