#!/usr/bin/env python3
"""
Gather commit history and extract URLs from HTML files in the repository.
Outputs gathered_links.json for use by build_colophon.py.
"""

import json
import os
import re
import subprocess
from pathlib import Path


def get_file_commit_details(file_path: str) -> list[dict]:
    """Get commit history for a specific file."""
    result = subprocess.run(
        [
            "git", "log",
            "--format=%H|%aI|%B%x00",
            "--follow",
            "--", file_path
        ],
        capture_output=True,
        text=True
    )

    commits = []
    for entry in result.stdout.split("\x00"):
        entry = entry.strip()
        if not entry:
            continue

        parts = entry.split("|", 2)
        if len(parts) >= 3:
            commit_hash, date, message = parts
            commits.append({
                "hash": commit_hash,
                "date": date,
                "message": message.strip()
            })

    return commits


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://[^\s<>\"\')(\]\[}{\x00]+'
    urls = re.findall(url_pattern, text)
    # Clean up URLs that might have trailing punctuation
    cleaned = []
    for url in urls:
        # Remove trailing punctuation that's not part of URL
        url = url.rstrip('.,;:!?')
        cleaned.append(url)
    return cleaned


def extract_title(html_path: str) -> str:
    """Extract title from HTML file."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for <title> tag
        match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass

    # Fallback to filename
    return Path(html_path).stem.replace('-', ' ').replace('_', ' ').title()


def extract_description(html_path: str) -> str:
    """Extract description from HTML meta tag or first paragraph."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for meta description
        match = re.search(
            r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
            content,
            re.IGNORECASE
        )
        if match:
            return match.group(1).strip()

        # Look for first <p> tag content
        match = re.search(r'<p[^>]*>([^<]+)</p>', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:200]
    except Exception:
        pass

    return ""


def main():
    # Find all HTML files in the current directory (not subdirectories)
    html_files = sorted(Path('.').glob('*.html'))

    tools = []

    for html_path in html_files:
        file_path = str(html_path)

        # Skip generated files
        if html_path.name in ('index.html', 'colophon.html', 'by-month.html'):
            continue

        commits = get_file_commit_details(file_path)
        if not commits:
            continue

        # Extract URLs from all commit messages
        all_urls = []
        for commit in commits:
            urls = extract_urls(commit['message'])
            all_urls.extend(urls)

        # Get file metadata
        title = extract_title(file_path)
        description = extract_description(file_path)
        slug = html_path.stem

        # Get creation and update dates
        created = commits[-1]['date'] if commits else None
        updated = commits[0]['date'] if commits else None

        tools.append({
            'file': file_path,
            'slug': slug,
            'title': title,
            'description': description,
            'commits': commits,
            'urls': list(set(all_urls)),  # Deduplicate
            'created': created,
            'updated': updated
        })

    # Sort by most recently updated
    tools.sort(key=lambda x: x['updated'] or '', reverse=True)

    # Write output
    with open('gathered_links.json', 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=2)

    print(f"Gathered data for {len(tools)} tool(s)")
    for tool in tools:
        print(f"  - {tool['title']} ({len(tool['commits'])} commits)")


if __name__ == '__main__':
    main()
