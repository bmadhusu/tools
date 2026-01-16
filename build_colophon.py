#!/usr/bin/env python3
"""
Build the colophon HTML page from gathered_links.json.
Shows all tools with their commit history and transcript links.
"""

import html
import json
import re
from datetime import datetime
from pathlib import Path

GITHUB_REPO = "bmadhusu/tools"


def format_date(iso_date: str) -> str:
    """Format ISO date to readable format."""
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y')
    except Exception:
        return iso_date


def format_commit_message(message: str) -> str:
    """Format commit message with linkified URLs and escaped HTML."""
    # Escape HTML
    escaped = html.escape(message)

    # Linkify URLs
    url_pattern = r'(https?://[^\s<>&]+)'
    escaped = re.sub(
        url_pattern,
        r'<a href="\1" target="_blank" rel="noopener">\1</a>',
        escaped
    )

    # Linkify GitHub issue references
    escaped = re.sub(
        r'#(\d+)',
        rf'<a href="https://github.com/{GITHUB_REPO}/issues/\1">#\1</a>',
        escaped
    )

    # Convert newlines to <br>
    escaped = escaped.replace('\n', '<br>\n')

    return escaped


def build_colophon():
    """Build the colophon HTML page."""
    # Load gathered data
    try:
        with open('gathered_links.json', 'r', encoding='utf-8') as f:
            tools = json.load(f)
    except FileNotFoundError:
        print("Error: gathered_links.json not found. Run gather_links.py first.")
        return

    # Build tool sections
    tool_sections = []
    for tool in tools:
        commits_html = []
        for commit in tool['commits']:
            commit_url = f"https://github.com/{GITHUB_REPO}/commit/{commit['hash']}"
            short_hash = commit['hash'][:7]
            date = format_date(commit['date'])
            message = format_commit_message(commit['message'])

            commits_html.append(f'''
                <div class="commit">
                    <div class="commit-header">
                        <a href="{commit_url}" target="_blank" rel="noopener" class="commit-hash">{short_hash}</a>
                        <span class="commit-date">{date}</span>
                    </div>
                    <div class="commit-message">{message}</div>
                </div>
            ''')

        tool_url = f"https://github.com/{GITHUB_REPO}/blob/main/{tool['file']}"
        description = html.escape(tool['description']) if tool['description'] else ''

        tool_sections.append(f'''
            <section class="tool" id="{tool['slug']}">
                <h2>
                    <a href="#{tool['slug']}" class="anchor">#</a>
                    <a href="{tool['slug']}.html">{html.escape(tool['title'])}</a>
                </h2>
                {f'<p class="description">{description}</p>' if description else ''}
                <p class="meta">
                    <a href="{tool_url}" target="_blank" rel="noopener">View source on GitHub</a>
                </p>
                <details class="commits">
                    <summary>Development history ({len(tool['commits'])} commit{'s' if len(tool['commits']) != 1 else ''})</summary>
                    <div class="commits-list">
                        {''.join(commits_html)}
                    </div>
                </details>
            </section>
        ''')

    # Build full HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Colophon - Tools</title>
    <style>
        :root {{
            --bg: #ffffff;
            --text: #1a1a1a;
            --muted: #666666;
            --border: #e5e5e5;
            --link: #0066cc;
            --link-hover: #0052a3;
            --code-bg: #f5f5f5;
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
                --code-bg: #2a2a2a;
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
            margin-bottom: 3rem;
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

        .tool {{
            margin-bottom: 2.5rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--border);
        }}

        .tool:last-child {{
            border-bottom: none;
        }}

        .tool h2 {{
            margin: 0 0 0.5rem 0;
            font-size: 1.5rem;
        }}

        .tool h2 a {{
            color: var(--text);
            text-decoration: none;
        }}

        .tool h2 a:hover {{
            color: var(--link);
        }}

        .anchor {{
            color: var(--muted);
            margin-right: 0.5rem;
            opacity: 0.3;
            text-decoration: none;
        }}

        .tool:hover .anchor {{
            opacity: 1;
        }}

        .description {{
            color: var(--muted);
            margin: 0.5rem 0;
        }}

        .meta {{
            font-size: 0.9rem;
            margin: 0.5rem 0 1rem 0;
        }}

        .meta a {{
            color: var(--link);
            text-decoration: none;
        }}

        .meta a:hover {{
            text-decoration: underline;
        }}

        details.commits {{
            margin-top: 1rem;
        }}

        details.commits summary {{
            cursor: pointer;
            color: var(--link);
            font-size: 0.9rem;
        }}

        details.commits summary:hover {{
            text-decoration: underline;
        }}

        .commits-list {{
            margin-top: 1rem;
            padding-left: 1rem;
            border-left: 2px solid var(--border);
        }}

        .commit {{
            margin-bottom: 1.5rem;
        }}

        .commit:last-child {{
            margin-bottom: 0;
        }}

        .commit-header {{
            display: flex;
            gap: 1rem;
            align-items: center;
            margin-bottom: 0.25rem;
        }}

        .commit-hash {{
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 0.85rem;
            color: var(--accent);
            text-decoration: none;
            background: var(--code-bg);
            padding: 0.1rem 0.4rem;
            border-radius: 3px;
        }}

        .commit-hash:hover {{
            text-decoration: underline;
        }}

        .commit-date {{
            font-size: 0.85rem;
            color: var(--muted);
        }}

        .commit-message {{
            font-size: 0.9rem;
            white-space: pre-wrap;
            word-break: break-word;
        }}

        .commit-message a {{
            color: var(--link);
            text-decoration: none;
        }}

        .commit-message a:hover {{
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

            .tool h2 {{
                font-size: 1.25rem;
            }}

            .commit-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 0.25rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Colophon</h1>
        <p>Development history and AI session transcripts for {len(tools)} tool{'s' if len(tools) != 1 else ''}.</p>
        <nav>
            <a href="index.html">All Tools</a>
            <a href="https://github.com/{GITHUB_REPO}">GitHub</a>
        </nav>
    </header>

    <main>
        {''.join(tool_sections)}
    </main>

    <footer>
        <p>
            This page shows the commit history for each tool, including links to
            Claude Code session transcripts where available.
        </p>
    </footer>

    <script>
        // Auto-expand commits if navigating to a specific tool
        if (window.location.hash) {{
            const tool = document.querySelector(window.location.hash);
            if (tool) {{
                const details = tool.querySelector('details');
                if (details) details.open = true;
            }}
        }}
    </script>
</body>
</html>
'''

    # Write output
    with open('colophon.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Built colophon.html with {len(tools)} tool(s)")


if __name__ == '__main__':
    build_colophon()
