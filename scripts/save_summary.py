#!/usr/bin/env python3
"""
Save YouTube summary to Obsidian vault and open styled HTML preview.

Usage:
    python save_summary.py --title "Video Title" --url "https://youtube.com/..." --summary "markdown content"
    echo "markdown" | python save_summary.py --title "Video Title" --url "https://youtube.com/..." --stdin
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Customize this path to your Obsidian vault location
VAULT_PATH = Path.home() / "Documents" / "YouTube-Summaries"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.7;
            max-width: 750px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #fafafa;
            color: #333;
        }}
        h1 {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #111;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 0.5rem;
        }}
        h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #222;
        }}
        h3 {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: #333;
        }}
        p {{
            margin-bottom: 1rem;
        }}
        ul, ol {{
            margin-bottom: 1rem;
            padding-left: 1.5rem;
        }}
        li {{
            margin-bottom: 0.5rem;
        }}
        strong {{
            font-weight: 600;
            color: #111;
        }}
        code {{
            background: #f0f0f0;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        blockquote {{
            border-left: 4px solid #e74c3c;
            margin: 1.5rem 0;
            padding: 0.5rem 1rem;
            background: #fff;
            color: #555;
        }}
        .meta {{
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 2rem;
        }}
        .meta a {{
            color: #e74c3c;
            text-decoration: none;
        }}
        .meta a:hover {{
            text-decoration: underline;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 2rem 0;
        }}
    </style>
</head>
<body>
    <article>
        <h1>{title}</h1>
        <div class="meta">
            <a href="{url}" target="_blank">Watch on YouTube</a> | Summarized {date}
        </div>
        {content}
    </article>
</body>
</html>
"""


def markdown_to_html(md: str) -> str:
    """Simple markdown to HTML conversion."""
    html = md

    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Blockquotes
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # Unordered lists - handle nested
    lines = html.split('\n')
    result = []
    in_list = False

    for line in lines:
        if re.match(r'^[-*] ', line):
            if not in_list:
                result.append('<ul>')
                in_list = True
            item = re.sub(r'^[-*] ', '', line)
            result.append(f'<li>{item}</li>')
        elif re.match(r'^\d+\. ', line):
            if not in_list:
                result.append('<ol>')
                in_list = True
            item = re.sub(r'^\d+\. ', '', line)
            result.append(f'<li>{item}</li>')
        else:
            if in_list:
                if result[-1].startswith('<ol>') or '<li>' in result[-1]:
                    result.append('</ol>' if any('<ol>' in r for r in result[-10:]) else '</ul>')
                in_list = False
            result.append(line)

    if in_list:
        result.append('</ul>')

    html = '\n'.join(result)

    # Paragraphs - wrap standalone lines
    lines = html.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<') and not stripped.endswith('>'):
            result.append(f'<p>{stripped}</p>')
        else:
            result.append(line)

    return '\n'.join(result)


def slugify(text: str) -> str:
    """Convert text to a safe filename."""
    # Remove special characters
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text[:80]  # Limit length


def save_to_vault(title: str, url: str, summary: str) -> Path:
    """Save markdown summary to Obsidian vault."""
    VAULT_PATH.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-{slugify(title)}.md"
    filepath = VAULT_PATH / filename

    # Add frontmatter
    content = f"""---
title: "{title}"
url: "{url}"
date: {date_str}
type: youtube-summary
---

# {title}

[Watch on YouTube]({url})

{summary}
"""

    filepath.write_text(content, encoding='utf-8')
    print(f"Saved to: {filepath}", file=sys.stderr)
    return filepath


def open_html_preview(title: str, url: str, summary: str):
    """Generate HTML and open in browser."""
    html_content = markdown_to_html(summary)
    date_str = datetime.now().strftime("%B %d, %Y")

    html = HTML_TEMPLATE.format(
        title=title,
        url=url,
        date=date_str,
        content=html_content
    )

    # Save to temp file and open
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html)
        temp_path = f.name

    # Open in default browser
    subprocess.run(['open', temp_path], check=True)
    print(f"Opened preview: {temp_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Save YouTube summary to Obsidian and preview")
    parser.add_argument("--title", "-t", required=True, help="Video title")
    parser.add_argument("--url", "-u", required=True, help="YouTube URL")
    parser.add_argument("--summary", "-s", help="Summary markdown content")
    parser.add_argument("--stdin", action="store_true", help="Read summary from stdin")
    parser.add_argument("--no-preview", action="store_true", help="Skip browser preview")
    parser.add_argument("--no-save", action="store_true", help="Skip saving to vault")

    args = parser.parse_args()

    # Get summary content
    if args.stdin:
        summary = sys.stdin.read()
    elif args.summary:
        summary = args.summary
    else:
        print("Error: Provide --summary or --stdin", file=sys.stderr)
        sys.exit(1)

    # Save to vault
    if not args.no_save:
        save_to_vault(args.title, args.url, summary)

    # Open preview
    if not args.no_preview:
        open_html_preview(args.title, args.url, summary)


if __name__ == "__main__":
    main()
