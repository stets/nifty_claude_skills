# YouTube Summarize Skill for Claude Code

A Claude Code skill that extracts transcripts from YouTube videos and generates intelligent summaries. Summaries can be saved to an Obsidian vault and previewed in your browser.

## What is a Claude Code Skill?

Skills are reusable capabilities you can add to Claude Code. They extend what Claude can do by providing specialized workflows, scripts, and context. Learn more:

- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Creating Custom Skills](https://docs.anthropic.com/en/docs/claude-code/skills#creating-custom-skills)

**Tip:** You can use the `/skill-creator` skill in Claude Code to help create or modify skills interactively!

## Features

- Extract transcripts from any YouTube video (including Shorts)
- Support for 100+ languages
- Multiple output formats: plain text, timestamped, or JSON
- Generates summaries based on your needs (TLDR, key points, detailed explanation)
- Saves summaries to an Obsidian vault with proper frontmatter
- Opens a styled HTML preview in your browser

## Installation

1. Clone this repository into your Claude Code skills directory:

```bash
git clone https://github.com/stets/nifty_claude_skills.git ~/.claude/skills/youtube-summarize
```

2. Set up the Python virtual environment and install dependencies:

```bash
cd ~/.claude/skills/youtube-summarize
python3 -m venv venv
source venv/bin/activate
pip install youtube-transcript-api
```

3. (Optional) Customize the Obsidian vault path in `scripts/save_summary.py`:

```python
# Edit this line to point to your preferred location
VAULT_PATH = Path.home() / "Documents" / "YouTube-Summaries"
```

## Usage

Once installed, simply share a YouTube URL with Claude Code and ask it to summarize:

- "Summarize this video: https://youtube.com/watch?v=..."
- "What are the key points from this video?"
- "Give me a TLDR of https://youtu.be/..."
- "Explain what this video is about"

Claude will automatically:
1. Extract the video transcript
2. Generate a summary based on your request
3. Save it to your Obsidian vault
4. Open a styled preview in your browser

## Customization

### Obsidian Vault Location

Edit `scripts/save_summary.py` and change the `VAULT_PATH` variable to your preferred directory:

```python
VAULT_PATH = Path.home() / "path" / "to" / "your" / "vault"
```

### Disable Features

When invoking the save script, you can disable features:
- `--no-save`: Skip saving to Obsidian vault
- `--no-preview`: Skip opening browser preview

## Supported URL Formats

- `youtube.com/watch?v=VIDEO_ID`
- `youtu.be/VIDEO_ID`
- `youtube.com/shorts/VIDEO_ID`
- `youtube.com/embed/VIDEO_ID`
- Direct video IDs

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `TranscriptsDisabled` | Video has no captions | Cannot extract - inform user |
| `NoTranscriptFound` | No transcript in requested language | Try without specifying language |
| `VideoUnavailable` | Private/deleted video | Video cannot be accessed |

## Creating Your Own Skills

Want to create your own Claude Code skills? Use the **Skill Creator** skill:

```
/skill-creator
```

This will guide you through creating effective skills that extend Claude's capabilities.

## License

MIT
