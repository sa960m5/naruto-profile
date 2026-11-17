import json
import shutil
from pathlib import Path
from urllib.parse import quote

# ==================================================
# NARUTO PROFILE - README GENERATOR v1.1
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILE = ROOT / "config" / "config.json"
THEME_FILE = ROOT / "config" / "naruto_theme.json"
REPOSITORY_FILE = ROOT / "assets" / "data" / "repositories.json"

SHOWCASE_GIF = ROOT / "assets" / "gif" / "repository-showcase.gif"

OUTPUT_DIR = ROOT / "dist" / "profile"
OUTPUT_FILE = OUTPUT_DIR / "README.md"


# ==================================================
# JSON LOADER
# ==================================================

def load_json(path):

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


# ==================================================
# CONFIGURATION
# ==================================================

def load_configuration():

    config = load_json(CONFIG_FILE)
    theme = load_json(THEME_FILE)

    username = config.get("github_username", "").strip()

    if not username or username == "YOUR_GITHUB_USERNAME":
        raise ValueError(
            "Configure your GitHub username in config/config.json."
        )

    return config, theme, username


# ==================================================
# THEME COLORS
# ==================================================

def get_theme_colors(theme):

    colors = theme.get("colors", {})

    return {
        "background": colors.get("background", "#0C0E14").lstrip("#"),
        "primary": colors.get("primary", "#FF7A00").lstrip("#"),
        "secondary": colors.get("secondary", "#FFD700").lstrip("#"),
        "text": colors.get("text", "#FFFFFF").lstrip("#")
    }


# ==================================================
# PROFILE HEADER
# ==================================================

def generate_header(username, config, colors):

    profile = config.get("profile", {})

    if not profile.get("show_banner", True):
        return f"""\
<div align="center">

# 🍥 {username}'s Ninja Profile

### Believe It! — Welcome to my Hidden Leaf Village.

</div>

"""

    primary = colors["primary"]

    banner_url = (
        "https://capsule-render.vercel.app/api?"
        "type=waving"
        f"&color={primary}"
        "&height=180"
        "&section=header"
        "&text=SHINOBI%20DEVELOPER"
        "&fontSize=38"
        "&fontColor=FFFFFF"
        "&animation=fadeIn"
    )

    return f"""\
<div align="center">

# 🍥 {username}'s Ninja Profile

### Believe It! — Welcome to my Hidden Leaf Village.

<img src="{banner_url}" width="100%" alt="Naruto Profile Banner"/>

</div>

"""


# ==================================================
# ABOUT SECTION
# ==================================================

def generate_about(username):

    profile_url = f"https://github.com/{username}"

    return f"""\
## 🍃 About the Shinobi

- 🥷 GitHub Ninja: **[@{username}]({profile_url})**
- ⚡ Exploring development and technology.
- 🔥 Building projects and learning new skills.
- 🌀 Turning ideas into real-world applications.

"""


# ==================================================
# ANIMATED REPOSITORY SHOWCASE
# ==================================================

def generate_showcase():

    if not SHOWCASE_GIF.exists():

        print("[WARNING] Repository showcase GIF not found.")
        return ""

    destination = OUTPUT_DIR / "repository-showcase.gif"

    shutil.copy2(SHOWCASE_GIF, destination)

    return """\
## 🌀 Ninja Mission Database

<div align="center">

<img src="./repository-showcase.gif"
     width="100%"
     alt="Animated Naruto Repository Showcase"/>

</div>

"""


# ==================================================
# REPOSITORY LIST
# ==================================================

def generate_repository_section(repositories, config, theme):

    if not repositories:
        return ""

    profile_settings = config.get("profile", {})
    repository_settings = config.get("repositories", {})
    card_settings = theme.get("repository_cards", {})

    if not profile_settings.get("show_repository_cards", True):
        return ""

    max_repositories = repository_settings.get(
        "max_repositories", 6
    )

    max_cards = card_settings.get("max_cards", 8)

    limit = min(max_repositories, max_cards)

    visible_repositories = repositories[:limit]

    content = """\
## ⚔️ Featured Ninja Missions

| Repository | Language | Stars | Forks |
|---|---|---:|---:|
"""

    for repo in visible_repositories:

        name = repo.get("name", "Unknown")
        url = repo.get("url", "#")

        language = repo.get("language") or "Not specified"

        # Prevent Markdown table formatting issues.
        name = name.replace("|", "\\|")
        language = language.replace("|", "\\|")

        stars = repo.get("stars", 0)
        forks = repo.get("forks", 0)

        content += (
            f"| [{name}]({url}) "
            f"| {language} "
            f"| ⭐ {stars} "
            f"| 🍴 {forks} |\n"
        )

    content += "\n"

    print(f"[INFO] Repository links generated: {len(visible_repositories)}")

    return content


# ==================================================
# GITHUB STATISTICS
# ==================================================

def generate_statistics(username, enabled, colors):

    if not enabled:
        return ""

    primary = colors["primary"]
    secondary = colors["secondary"]

    stats_url = (
        "https://github-readme-stats.vercel.app/api?"
        f"username={username}"
        "&show_icons=true"
        "&theme=dark"
        "&hide_border=true"
        f"&title_color={primary}"
        f"&icon_color={secondary}"
        "&text_color=FFFFFF"
    )

    languages_url = (
        "https://github-readme-stats.vercel.app/api/top-langs/?"
        f"username={username}"
        "&layout=compact"
        "&theme=dark"
        "&hide_border=true"
        f"&title_color={primary}"
    )

    return f"""\
## 📊 Shinobi Statistics

<div align="center">

<img height="180"
     src="{stats_url}"
     alt="GitHub Statistics"/>

<img height="180"
     src="{languages_url}"
     alt="Most Used Programming Languages"/>

</div>

"""


# ==================================================
# CONTRIBUTION GRAPH
# ==================================================

def generate_contributions(username, enabled, colors):

    if not enabled:
        return ""

    background = colors["background"]
    primary = colors["primary"]
    secondary = colors["secondary"]

    graph_url = (
        "https://github-readme-activity-graph.vercel.app/graph?"
        f"username={username}"
        f"&bg_color={background}"
        f"&color={primary}"
        f"&line={secondary}"
        "&point=FFFFFF"
        "&hide_border=true"
    )

    return f"""\
## 🐍 Shinobi Contribution Journey

<div align="center">

<img src="{graph_url}"
     width="100%"
     alt="GitHub Contribution Activity Graph"/>

</div>

"""


# ==================================================
# SOCIAL LINKS
# ==================================================

def generate_social_links(config):

    profile = config.get("profile", {})

    if not profile.get("show_social_links", True):
        return ""

    links = config.get("social_links", {})

    if not links:
        return ""

    content = """\
## 🌐 Connect With Me

<div align="center">

"""

    for platform, url in links.items():

        if not url:
            continue

        label = platform.replace("_", " ").title()

        badge_label = quote(label, safe="")

        badge_url = (
            "https://img.shields.io/badge/"
            f"{badge_label}-FF7A00"
            "?style=for-the-badge"
            "&logo=github"
            "&logoColor=white"
        )

        content += (
            f'<a href="{url}">'
            f'<img src="{badge_url}" alt="{label}"/>'
            f'</a> '
        )

    content += """

</div>

"""

    return content


# ==================================================
# FOOTER
# ==================================================

def generate_footer(colors):

    primary = colors["primary"]

    footer_url = (
        "https://capsule-render.vercel.app/api?"
        "type=waving"
        f"&color={primary}"
        "&height=100"
        "&section=footer"
    )

    return f"""\
<div align="center">

### 🍥 A shinobi never gives up!

<img src="{footer_url}" alt="Naruto Footer"/>

</div>

<!-- Generated automatically by Naruto Profile Framework -->

"""


# ==================================================
# MAIN GENERATOR
# ==================================================

def main():

    print("=" * 60)
    print(" NARUTO PROFILE - README GENERATOR v1.1")
    print("=" * 60)

    config, theme, username = load_configuration()

    repository_data = load_json(REPOSITORY_FILE)

    repositories = repository_data.get("repositories", [])

    profile_settings = config.get("profile", {})

    colors = get_theme_colors(theme)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    sections = []

    # Header.
    sections.append(
        generate_header(username, config, colors)
    )

    # About.
    sections.append(
        generate_about(username)
    )

    # Repository showcase and links.
    if profile_settings.get("show_repository_cards", True):

        sections.append(
            generate_showcase()
        )

        sections.append(
            generate_repository_section(
                repositories,
                config,
                theme
            )
        )

    # Statistics.
    sections.append(
        generate_statistics(
            username,
            profile_settings.get("show_statistics", True),
            colors
        )
    )

    # Contributions.
    sections.append(
        generate_contributions(
            username,
            profile_settings.get("show_contributions", True),
            colors
        )
    )

    # Social links.
    sections.append(
        generate_social_links(config)
    )

    # Footer.
    sections.append(
        generate_footer(colors)
    )

    # Combine README.
    readme = "\n".join(
        section for section in sections if section.strip()
    )

    OUTPUT_FILE.write_text(
        readme,
        encoding="utf-8"
    )

    print("\n[SUCCESS] README generated.")
    print(f"[INFO] Username: {username}")
    print(f"[INFO] Repositories available: {len(repositories)}")
    print(f"[INFO] Output: {OUTPUT_FILE}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()