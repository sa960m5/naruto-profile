"""
============================================================
 NARUTO PROFILE - NINJA WAY GENERATOR
 Version: 3.0
 Fixed Reference Layout + Dynamic Content Engine
============================================================

FEATURES
- Fixed 1280 x 800 reference layout
- Configurable anime artwork
- Dynamic headline and introduction
- Exactly three configurable highlight cards
- Custom icons, descriptions and colors
- Configurable quote
- Dynamic GitHub statistics
- Configurable footer
- Theme color customization
- SVG XML validation
- Safe artwork path validation
============================================================
"""

import json
import base64
import html
import re
import sys

from pathlib import Path
from xml.etree import ElementTree as ET


# ==========================================================
# PROJECT PATHS
# ==========================================================

ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILE = ROOT / "config" / "ninja_way.json"
PROFILE_FILE = ROOT / "assets" / "data" / "profile.json"

TEMPLATE_FILE = (
    ROOT / "templates" /
    "ninja-way" /
    "ninja-way-template.svg"
)

OUTPUT_FILE = (
    ROOT / "assets" /
    "ninja-way" /
    "ninja-way.svg"
)


# ==========================================================
# GENERATOR
# ==========================================================

class NinjaWayGenerator:

    def __init__(self):

        print("=" * 60)
        print(" NARUTO PROFILE - NINJA WAY GENERATOR v3.0")
        print(" FIXED REFERENCE LAYOUT ENGINE")
        print("=" * 60)

        self.config = {}
        self.profile = {}
        self.template = ""

    # ======================================================
    # LOAD JSON
    # ======================================================

    @staticmethod
    def load_json(path):

        if not path.is_file():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    # ======================================================
    # LOAD PROJECT FILES
    # ======================================================

    def load_files(self):

        print("\n[INFO] Loading Ninja Way configuration...")

        self.config = self.load_json(CONFIG_FILE)

        if not isinstance(self.config, dict):
            raise ValueError(
                "Ninja Way configuration must be a JSON object."
            )

        print("[SUCCESS] Configuration loaded.")

        print("[INFO] Loading GitHub profile...")

        self.profile = self.load_json(PROFILE_FILE)

        if not isinstance(self.profile, dict):
            raise ValueError(
                "GitHub profile data must be a JSON object."
            )

        print("[SUCCESS] GitHub profile loaded.")

        print("[INFO] Loading SVG template...")

        if not TEMPLATE_FILE.is_file():
            raise FileNotFoundError(
                f"SVG template not found: {TEMPLATE_FILE}"
            )

        self.template = TEMPLATE_FILE.read_text(
            encoding="utf-8"
        )

        print("[SUCCESS] SVG template loaded.")

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def escape(value):

        return html.escape(
            str(value),
            quote=True
        )

    @staticmethod
    def validate_color(value):

        return (
            isinstance(value, str)
            and bool(
                re.fullmatch(
                    r"#[0-9A-Fa-f]{6}",
                    value
                )
            )
        )

    def get_color(self, name, default):

        appearance = self.config.get(
            "appearance", {}
        )

        value = appearance.get(
            name, default
        )

        if not self.validate_color(value):

            print(
                f"[WARNING] Invalid color '{name}'. "
                "Using default."
            )

            return default

        return value

    # ======================================================
    # CONFIGURATION VALIDATION
    # ======================================================

    def validate_configuration(self):

        content = self.config.get(
            "content", {}
        )

        highlights = content.get(
            "highlights", {}
        )

        items = highlights.get(
            "items", []
        )

        if not isinstance(items, list):
            raise ValueError(
                "Highlight items must be a list."
            )

        if len(items) > 3:
            raise ValueError(
                "The reference design supports exactly "
                "three highlight positions. Configure "
                "up to three items."
            )

        for index, item in enumerate(items):

            if not isinstance(item, dict):
                raise ValueError(
                    f"Highlight {index + 1} must be an object."
                )

            color = item.get(
                "color",
                "#FF7A00"
            )

            if not self.validate_color(color):
                raise ValueError(
                    f"Invalid color in highlight {index + 1}."
                )

        if not isinstance(
            self.config.get("section", {}),
            dict
        ):
            raise ValueError(
                "Section configuration must be an object."
            )

        print("[SUCCESS] Configuration validated.")

    # ======================================================
    # APPLY THEME COLORS
    # ======================================================

    def apply_theme_colors(self, svg):

        replacements = {

            "#0C0E14": self.get_color(
                "background", "#0C0E14"
            ),

            "#171B25": self.get_color(
                "card_background", "#171B25"
            ),

            "#FF7A00": self.get_color(
                "primary", "#FF7A00"
            ),

            "#FFD700": self.get_color(
                "secondary", "#FFD700"
            ),

            "#4AA8FF": self.get_color(
                "accent", "#4AA8FF"
            ),

            "#EEF1F7": self.get_color(
                "text", "#EEF1F7"
            ),

            "#8B93A7": self.get_color(
                "muted", "#8B93A7"
            )

        }

        for old, new in replacements.items():

            svg = svg.replace(
                old, new
            )

        return svg

    # ======================================================
    # ARTWORK GENERATOR
    # ======================================================

    def generate_artwork(self):

        settings = self.config.get(
            "artwork", {}
        )

        if not settings.get("enabled", True):

            print("[INFO] Artwork disabled.")

            return ""

        image_path = settings.get(
            "image", ""
        )

        if not image_path:

            print("[WARNING] No artwork configured.")

            return ""

        path = (
            ROOT / image_path
        ).resolve()

        try:

            path.relative_to(
                ROOT.resolve()
            )

        except ValueError:

            raise ValueError(
                "Artwork must remain inside the project directory."
            )

        if not path.is_file():

            raise FileNotFoundError(
                f"Artwork not found: {path}"
            )

        mime_types = {

            ".gif": "image/gif",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp"

        }

        mime = mime_types.get(
            path.suffix.lower()
        )

        if not mime:

            raise ValueError(
                "Unsupported artwork format."
            )

        image_data = path.read_bytes()

        if not image_data:

            raise ValueError(
                "Artwork file is empty."
            )

        encoded = base64.b64encode(
            image_data
        ).decode("ascii")

        width = int(
            settings.get("width", 520)
        )

        height = int(
            settings.get("height", 440)
        )

        if width <= 0 or height <= 0:

            raise ValueError(
                "Artwork dimensions must be positive."
            )

        preserve = (
            "xMidYMid meet"
            if settings.get(
                "preserve_aspect_ratio", True
            )
            else "none"
        )

        print(
            f"[SUCCESS] Artwork loaded: {path.name}"
        )

        print(
            f"[INFO] Artwork size: "
            f"{len(image_data) / 1024:.2f} KB"
        )

        return f"""
        <image
            x="0"
            y="0"
            width="{width}"
            height="{height}"
            href="data:{mime};base64,{encoded}"
            preserveAspectRatio="{preserve}"
        />
        """

    # ======================================================
    # ICON GENERATOR
    # ======================================================

    def generate_icon(self, icon, color):

        icons = {

            "code": """
                <path d="M12 5 L5 12 L12 19"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2.5"
                      stroke-linecap="round"/>

                <path d="M18 5 L25 12 L18 19"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2.5"
                      stroke-linecap="round"/>
            """,

            "interface": """
                <rect x="3" y="4"
                      width="24" height="20"
                      rx="3"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2"/>

                <path d="M3 10 H27"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2"/>

                <circle cx="8" cy="7" r="1"
                        fill="{color}"/>

                <circle cx="12" cy="7" r="1"
                        fill="{color}"/>
            """,

            "security": """
                <path d="M15 3 L24 7 V13
                         C24 19 20 23 15 25
                         C10 23 6 19 6 13 V7 Z"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2"/>

                <path d="M11 14 L14 17 L20 10"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2"/>
            """,

            "database": """
                <ellipse cx="15" cy="7"
                         rx="9" ry="4"
                         fill="none"
                         stroke="{color}"
                         stroke-width="2"/>

                <path d="M6 7 V19
                         C6 24 24 24 24 19 V7"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2"/>

                <path d="M6 13
                         C6 18 24 18 24 13"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2"/>
            """,

            "star": """
                <path d="M15 3 L18.5 11 L27 12
                         L20.5 18 L22.5 27 L15 22
                         L7.5 27 L9.5 18 L3 12
                         L11.5 11 Z"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2"/>
            """,

            "target": """
                <circle cx="15" cy="15" r="11"
                        fill="none"
                        stroke="{color}"
                        stroke-width="2"/>

                <circle cx="15" cy="15" r="6"
                        fill="none"
                        stroke="{color}"
                        stroke-width="2"/>

                <circle cx="15" cy="15" r="2"
                        fill="{color}"/>
            """,

            "rocket": """
                <path d="M15 3 C21 5 24 10 22 17
                         L15 24 L8 17 C6 10 9 5 15 3 Z"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2"/>

                <circle cx="15" cy="11" r="2"
                        fill="none"
                        stroke="{color}"
                        stroke-width="2"/>
            """,

            "default": """
                <circle cx="15" cy="15" r="10"
                        fill="none"
                        stroke="{color}"
                        stroke-width="2"/>

                <path d="M10 15 L14 19 L21 11"
                      fill="none"
                      stroke="{color}"
                      stroke-width="2"/>
            """

        }

        shape = icons.get(
            str(icon).lower(),
            icons["default"]
        )

        return shape.format(
            color=color
        )

    # ======================================================
    # HIGHLIGHT GENERATOR
    # ======================================================

    def generate_highlights(self):

        settings = self.config.get(
            "content", {}
        ).get(
            "highlights", {}
        )

        if not settings.get("enabled", True):

            print("[INFO] Highlights disabled.")

            return ""

        items = settings.get(
            "items", []
        )

        # Fixed reference positions.
        positions = [
            145,
            217,
            289
        ]

        card_height = 62

        output = []

        primary = self.get_color(
            "primary", "#FF7A00"
        )

        text_color = self.get_color(
            "text", "#EEF1F7"
        )

        muted = self.get_color(
            "muted", "#8B93A7"
        )

        background = self.get_color(
            "card_background", "#171B25"
        )

        for index, item in enumerate(items):

            if not item.get("enabled", True):
                continue

            y = positions[index]

            color = item.get(
                "color", primary
            )

            title = self.escape(
                item.get(
                    "title", "Untitled"
                )
            )

            description = self.escape(
                item.get(
                    "description", ""
                )
            )

            icon = self.generate_icon(
                item.get("icon", "default"),
                color
            )

            output.append(f"""

            <g transform="translate(0,{y})">

                <rect
                    x="0"
                    y="0"
                    width="600"
                    height="{card_height}"
                    rx="12"
                    fill="{background}"
                    stroke="{color}"
                    stroke-opacity="0.75"
                    stroke-width="1.2"
                />

                <circle
                    cx="28"
                    cy="31"
                    r="17"
                    fill="{color}"
                    fill-opacity="0.12"
                />

                <g
                    class="highlight-icon"
                    transform="translate(13,16)"
                >
                    {icon}
                </g>

                <text
                    x="58"
                    y="25"
                    fill="{text_color}"
                    font-size="15"
                    font-weight="bold"
                    font-family="Arial, sans-serif"
                >{title}</text>

                <text
                    x="58"
                    y="45"
                    fill="{muted}"
                    font-size="11"
                    font-family="Arial, sans-serif"
                >{description}</text>

            </g>

            """)

        print(
            f"[SUCCESS] Generated {len(output)} highlight cards."
        )

        return "\n".join(output)

    # ======================================================
    # QUOTE GENERATOR
    # ======================================================

    def generate_quote(self):

        quote_settings = self.config.get(
            "content", {}
        ).get(
            "quote", {}
        )

        if not quote_settings.get(
            "enabled", True
        ):

            print("[INFO] Quote disabled.")

            return ""

        quote = quote_settings.get(
            "text", ""
        )

        if not quote:

            print("[INFO] Quote text is empty.")

            return ""

        color = self.get_color(
            "secondary", "#FFD700"
        )

        return f"""
        <g>

            <rect
                x="0"
                y="355"
                width="600"
                height="78"
                rx="15"
                fill="#211D20"
                stroke="#75431F"
                stroke-width="1"
            />

            <rect
                x="0"
                y="355"
                width="4"
                height="78"
                rx="2"
                fill="url(#orangeGradient)"
            />

            <text
                x="24"
                y="385"
                fill="{color}"
                font-size="15"
                font-style="italic"
                font-family="Arial, sans-serif"
            >{self.escape(quote)}</text>

        </g>
        """

    # ======================================================
    # GITHUB STATISTICS
    # ======================================================

    def get_stat_value(self, kind):

        profile = self.profile.get(
            "profile", {}
        )

        stats = self.profile.get(
            "statistics", {}
        )

        values = {

            "repositories":
                profile.get(
                    "public_repositories", 0
                ),

            "stars":
                stats.get(
                    "total_stars", 0
                ),

            "followers":
                profile.get(
                    "followers", 0
                ),

            "following":
                profile.get(
                    "following", 0
                ),

            "forks":
                stats.get(
                    "total_forks", 0
                )

        }

        return values.get(
            kind, 0
        )

    def generate_statistics(self):

        settings = self.config.get(
            "statistics", {}
        )

        if not settings.get(
            "enabled", True
        ):

            print("[INFO] Statistics disabled.")

            return ""

        items = [

            item

            for item in settings.get(
                "items", []
            )

            if item.get("enabled", True)

        ]

        if not items:
            return ""

        if len(items) > 3:

            raise ValueError(
                "The reference design supports up to "
                "three statistics."
            )

        output = []

        # Fixed reference statistics position.
        start_x = 20
        spacing = 190
        y = 465

        primary = self.get_color(
            "primary", "#FF7A00"
        )

        muted = self.get_color(
            "muted", "#8B93A7"
        )

        for index, item in enumerate(items):

            x = start_x + (
                index * spacing
            )

            kind = item.get(
                "type", ""
            )

            label = self.escape(
                item.get(
                    "label",
                    kind.upper()
                )
            )

            value = self.escape(
                self.get_stat_value(kind)
            )

            output.append(f"""

            <g transform="translate({x},{y})">

                <text
                    x="0"
                    y="0"
                    fill="{primary}"
                    font-size="25"
                    font-weight="bold"
                    font-family="Arial, sans-serif"
                >{value}</text>

                <text
                    x="0"
                    y="23"
                    fill="{muted}"
                    font-size="10"
                    font-family="monospace"
                    letter-spacing="1"
                >{label}</text>

                <line
                    x1="0"
                    y1="34"
                    x2="75"
                    y2="34"
                    stroke="{primary}"
                    stroke-opacity="0.6"
                />

            </g>

            """)

        print(
            f"[SUCCESS] Generated {len(items)} statistics."
        )

        return "\n".join(output)

    # ======================================================
    # FOOTER
    # ======================================================

    def generate_footer(self):

        settings = self.config.get(
            "footer", {}
        )

        if not settings.get(
            "enabled", True
        ):
            return ""

        return self.escape(
            settings.get(
                "tagline", ""
            )
        )

    # ======================================================
    # BUILD SVG
    # ======================================================

    def generate(self):

        if not self.config.get(
            "enabled", True
        ):

            print("[INFO] Ninja Way section disabled.")

            return

        self.validate_configuration()

        section = self.config.get(
            "section", {}
        )

        if not section.get(
            "enabled", True
        ):

            print("[INFO] Section introduction disabled.")

        # Apply theme colors to the original template
        # before injecting custom card colors.
        svg = self.apply_theme_colors(
            self.template
        )

        artwork = self.generate_artwork()

        highlights = self.generate_highlights()

        quote = self.generate_quote()

        statistics = self.generate_statistics()

        eyebrow = self.escape(
            section.get(
                "eyebrow", "// MY NINJA WAY"
            )
        )

        headline = self.escape(
            section.get(
                "headline", "Believe it — then build it"
            )
        )

        introduction = self.escape(
            section.get(
                "introduction", ""
            )
        )

        tagline = self.generate_footer()

        replacements = {

            "{{ARTWORK_COMPONENT}}": artwork,

            "{{EYEBROW}}": eyebrow,

            "{{HEADLINE}}": headline,

            "{{INTRODUCTION}}": introduction,

            "{{HIGHLIGHTS_COMPONENT}}": highlights,

            "{{QUOTE}}": quote,

            "{{STATS_COMPONENT}}": statistics,

            "{{TAGLINE}}": tagline

        }

        print("\n[INFO] Injecting dynamic content...")

        for placeholder, value in replacements.items():

            svg = svg.replace(
                placeholder,
                value
            )

        unresolved = re.findall(
            r"\{\{[^{}]+\}\}",
            svg
        )

        if unresolved:

            raise ValueError(
                f"Unresolved placeholders: {unresolved}"
            )

        print("[INFO] Validating SVG XML...")

        try:

            ET.fromstring(svg)

        except ET.ParseError as error:

            raise ValueError(
                f"SVG validation failed: {error}"
            )

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        OUTPUT_FILE.write_text(
            svg,
            encoding="utf-8"
        )

        print("\n" + "=" * 60)
        print(" NINJA WAY v3.0 GENERATION SUMMARY")
        print("=" * 60)

        print("Canvas: 1280 x 800")
        print("Layout: Fixed reference design")

        print(
            "Highlights:",
            len([
                item
                for item in self.config.get(
                    "content", {}
                ).get(
                    "highlights", {}
                ).get(
                    "items", []
                )
                if item.get("enabled", True)
            ])
        )

        print(
            "Artwork:",
            self.config.get(
                "artwork", {}
            ).get("enabled", True)
        )

        print(
            "Quote:",
            self.config.get(
                "content", {}
            ).get(
                "quote", {}
            ).get("enabled", True)
        )

        print(
            "Statistics:",
            self.config.get(
                "statistics", {}
            ).get("enabled", True)
        )

        print(
            f"Output: {OUTPUT_FILE}"
        )

        print("[SUCCESS] SVG XML validated.")
        print("[SUCCESS] Ninja Way v3.0 generated.")


# ==========================================================
# ENTRY POINT
# ==========================================================

def main():

    try:

        generator = NinjaWayGenerator()

        generator.load_files()

        generator.generate()

    except Exception as error:

        print(f"\n[ERROR] {error}")

        sys.exit(1)


if __name__ == "__main__":

    main()