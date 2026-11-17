import json
import html
import math

from pathlib import Path

# ==========================================
# NARUTO PROFILE - SVG CARD GENERATOR
# ==========================================

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "assets" / "data" / "repositories.json"
OUTPUT_FILE = ROOT / "assets" / "svg" / "repositories.svg"

CARD_WIDTH = 350
CARD_HEIGHT = 145
GAP = 18
PADDING = 24
COLUMNS = 2

COLORS = {
    "background": "#111318",
    "card": "#191D26",
    "border": "#343B49",
    "primary": "#FF7A00",
    "secondary": "#FFD700",
    "text": "#F5F5F5",
    "muted": "#A0A8B5"
}


def load_repository_data():
    """Load generated repository JSON."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "Repository JSON not found. "
            "Run fetch_repositories.py first."
        )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def escape(value):
    """Escape text for safe SVG/XML output."""

    return html.escape(str(value), quote=True)


def wrap_text(text, max_length=43):
    """Wrap long descriptions into SVG text lines."""

    words = text.split()
    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()

        if len(candidate) > max_length and current:
            lines.append(current)
            current = word
        else:
            current = candidate

    if current:
        lines.append(current)

    return lines[:2]


def create_card(repo, x, y):
    """Generate an individual clickable repository card."""

    name = escape(repo["name"])
    language = escape(repo["language"])

    description = (
        repo["description"].strip()
        or "Explore this project on GitHub."
    )

    description_lines = wrap_text(description)

    description_svg = ""

    for index, line in enumerate(description_lines):
        description_svg += (
            f'<text x="22" y="{69 + index * 17}" '
            f'class="description">{escape(line)}</text>'
        )

    return f"""
    <a href="{escape(repo['url'])}"
       target="_blank"
       rel="noopener noreferrer">

        <g transform="translate({x},{y})">

            <rect
                width="{CARD_WIDTH}"
                height="{CARD_HEIGHT}"
                rx="13"
                fill="{COLORS['card']}"
                stroke="{COLORS['border']}"
                stroke-width="1.2"
                class="card"
            />

            <rect
                x="0"
                y="0"
                width="5"
                height="{CARD_HEIGHT}"
                rx="2"
                fill="{COLORS['primary']}"
            />

            <text x="22" y="37" class="title">
                {name}
            </text>

            {description_svg}

            <text x="22" y="119" class="language">
                {language}
            </text>

            <text x="190" y="119" class="stats">
                ★ {repo['stars']}   Forks: {repo['forks']}
            </text>

        </g>

    </a>
    """


def generate_svg(data):
    """Generate the complete repository dashboard."""

    repositories = data["repositories"]

    rows = math.ceil(len(repositories) / COLUMNS)

    dashboard_height = (
        100
        + rows * CARD_HEIGHT
        + max(0, rows - 1) * GAP
        + 35
    )

    dashboard_width = (
        PADDING * 2
        + COLUMNS * CARD_WIDTH
        + (COLUMNS - 1) * GAP
    )

    cards = []

    for index, repo in enumerate(repositories):

        column = index % COLUMNS
        row = index // COLUMNS

        x = PADDING + column * (CARD_WIDTH + GAP)
        y = 100 + row * (CARD_HEIGHT + GAP)

        cards.append(create_card(repo, x, y))

    generated_at = escape(data["generated_at"])

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    width="{dashboard_width}"
    height="{dashboard_height}"
    viewBox="0 0 {dashboard_width} {dashboard_height}"
>

<style>

    .heading {{
        fill: {COLORS['text']};
        font-size: 25px;
        font-weight: bold;
        font-family: Arial, sans-serif;
    }}

    .subtitle {{
        fill: {COLORS['muted']};
        font-size: 12px;
        font-family: Arial, sans-serif;
    }}

    .title {{
        fill: {COLORS['primary']};
        font-size: 16px;
        font-weight: bold;
        font-family: Arial, sans-serif;
    }}

    .description {{
        fill: {COLORS['muted']};
        font-size: 12px;
        font-family: Arial, sans-serif;
    }}

    .language {{
        fill: {COLORS['secondary']};
        font-size: 12px;
        font-family: Arial, sans-serif;
    }}

    .stats {{
        fill: {COLORS['muted']};
        font-size: 11px;
        font-family: Arial, sans-serif;
    }}

    .card {{
        transition: stroke 0.2s ease;
    }}

    a:hover .card {{
        stroke: {COLORS['primary']};
        stroke-width: 2;
    }}

</style>

<rect
    width="100%"
    height="100%"
    rx="16"
    fill="{COLORS['background']}"
/>

<text x="{PADDING}" y="39" class="heading">
    🍥 NINJA MISSION DATABASE
</text>

<text x="{PADDING}" y="65" class="subtitle">
    {len(repositories)} PUBLIC PROJECTS DISCOVERED
</text>

{''.join(cards)}

<text
    x="{PADDING}"
    y="{dashboard_height - 12}"
    class="subtitle"
>
    Generated automatically | {generated_at}
</text>

</svg>
"""

    return svg


def main():

    print("=" * 50)
    print(" NARUTO PROFILE - SVG CARD GENERATOR")
    print("=" * 50)

    data = load_repository_data()

    svg = generate_svg(data)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        svg,
        encoding="utf-8"
    )

    print("\n[SUCCESS] SVG dashboard generated.")
    print(f"[INFO] Cards generated: {len(data['repositories'])}")
    print(f"[INFO] Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()