import base64
import json
import re
import sys
import xml.etree.ElementTree as ET

from pathlib import Path
from xml.sax.saxutils import escape


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

PROFILE_FILE = ROOT / "assets" / "data" / "profile.json"
TEMPLATE_FILE = ROOT / "templates" / "hero" / "hero-template.svg"
CONFIG_FILE = ROOT / "config" / "config.json"
OUTPUT_FILE = ROOT / "assets" / "hero" / "hero.svg"


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_TAGLINE = "Turning ideas into reality, one commit at a time."

DEFAULT_DURATION_PER_ROLE = 3

MAX_ROLES = 10

CHARACTER_AREA = {
    "x": 690,
    "y": 54,
    "width": 520,
    "height": 420
}


# ============================================================
# HERO GENERATOR
# ============================================================

class NarutoHeroGenerator:

    def __init__(self):

        self.profile_data = {}
        self.profile = {}
        self.statistics = {}

        self.config = {}
        self.hero_config = {}
        self.character_config = {}

        self.roles = []
        self.tagline = DEFAULT_TAGLINE

        self.duration_per_role = DEFAULT_DURATION_PER_ROLE

        self.character_component = ""
        self.character_enabled = False

        self.character_image_path = None

    # ========================================================
    # TEXT SANITIZATION
    # ========================================================

    @staticmethod
    def clean_text(value):

        if value is None:
            return ""

        value = re.sub(r"\s+", " ", str(value)).strip()

        return escape(value)

    # ========================================================
    # LOAD CONFIGURATION AND PROFILE DATA
    # ========================================================

    def load_data(self):

        print("[INFO] Loading project configuration...")

        if not CONFIG_FILE.exists():
            raise FileNotFoundError(
                f"Configuration not found: {CONFIG_FILE}"
            )

        if not PROFILE_FILE.exists():
            raise FileNotFoundError(
                f"Profile data not found: {PROFILE_FILE}\n"
                "Run: python scripts/fetch_profile.py"
            )

        if not TEMPLATE_FILE.exists():
            raise FileNotFoundError(
                f"Hero template not found: {TEMPLATE_FILE}"
            )

        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            self.config = json.load(file)

        with PROFILE_FILE.open("r", encoding="utf-8") as file:
            self.profile_data = json.load(file)

        self.profile = self.profile_data.get("profile", {})
        self.statistics = self.profile_data.get("statistics", {})

        if not self.profile.get("username"):
            raise ValueError(
                "GitHub username is missing from profile.json"
            )

        self.hero_config = self.config.get("hero", {})

        if not isinstance(self.hero_config, dict):
            raise ValueError(
                "The 'hero' configuration must be a JSON object."
            )

        self.character_config = self.config.get(
            "character",
            self.hero_config.get("character", {})
        )

        if not isinstance(self.character_config, dict):
            raise ValueError(
                "The 'character' configuration must be a JSON object."
            )

        print("[SUCCESS] Configuration loaded.")
        print("[SUCCESS] GitHub profile data loaded.")

        self.load_hero_preferences()
        self.load_character_preferences()

    # ========================================================
    # LOAD HERO PREFERENCES
    # ========================================================

    def load_hero_preferences(self):

        print("[INFO] Loading hero preferences...")

        configured_roles = self.hero_config.get("roles")

        if not isinstance(configured_roles, list) or not configured_roles:
            raise ValueError(
                "No roles configured. Add a non-empty roles array "
                "inside the hero section of config.json."
            )

        self.roles = [
            str(role).strip()
            for role in configured_roles
            if str(role).strip()
        ]

        if not self.roles:
            raise ValueError(
                "The configured roles list cannot be empty."
            )

        if len(self.roles) > MAX_ROLES:
            raise ValueError(
                f"A maximum of {MAX_ROLES} roles is supported."
            )

        self.tagline = str(
            self.hero_config.get(
                "tagline",
                DEFAULT_TAGLINE
            )
        ).strip()

        duration = self.hero_config.get(
            "role_duration",
            DEFAULT_DURATION_PER_ROLE
        )

        if (
            not isinstance(duration, (int, float))
            or isinstance(duration, bool)
        ):
            raise ValueError(
                "hero.role_duration must be a positive number."
            )

        if duration < 1 or duration > 10:
            raise ValueError(
                "hero.role_duration must be between 1 and 10 seconds."
            )

        self.duration_per_role = duration

        print(f"[SUCCESS] Loaded {len(self.roles)} roles.")
        print(f"[INFO] Role duration: {self.duration_per_role}s")

    # ========================================================
    # LOAD CHARACTER PREFERENCES
    # ========================================================

    def load_character_preferences(self):

        print("[INFO] Loading character preferences...")

        self.character_enabled = self.character_config.get(
            "enabled",
            False
        )

        if not isinstance(self.character_enabled, bool):
            raise ValueError(
                "character.enabled must be true or false."
            )

        if not self.character_enabled:

            print("[INFO] Custom character animation disabled.")
            return

        image_value = self.character_config.get(
            "image",
            "assets/characters/custom-character.gif"
        )

        if not image_value:
            raise ValueError(
                "Character image path is missing."
            )

        image_path = Path(image_value)

        if not image_path.is_absolute():
            image_path = ROOT / image_path

        image_path = image_path.resolve()

        # Prevent paths outside the project directory.

        try:
            image_path.relative_to(ROOT.resolve())
        except ValueError:
            raise ValueError(
                "Character image must be inside the project directory."
            )

        if not image_path.exists():
            raise FileNotFoundError(
                f"Character GIF not found: {image_path}"
            )

        if image_path.suffix.lower() != ".gif":
            raise ValueError(
                "Animated character integration currently requires a GIF."
            )

        if image_path.stat().st_size == 0:
            raise ValueError(
                "Character GIF is empty."
            )

        with image_path.open("rb") as file:
            header = file.read(6)

        if header not in (b"GIF87a", b"GIF89a"):
            raise ValueError(
                "Invalid GIF file. Expected GIF87a or GIF89a."
            )

        self.character_image_path = image_path

        print("[SUCCESS] Animated character found.")
        print(f"[INFO] Character: {image_path.name}")
        print(
            f"[INFO] GIF size: "
            f"{image_path.stat().st_size / 1024:.2f} KB"
        )

    # ========================================================
    # PROFILE INFORMATION
    # ========================================================

    def get_display_name(self):

        return (
            self.profile.get("display_name")
            or self.profile.get("username")
        )

    # ========================================================
    # DESCRIPTION
    # ========================================================

    def get_description_lines(self):

        configured_lines = self.hero_config.get(
            "description_lines"
        )

        if isinstance(configured_lines, list) and configured_lines:

            lines = configured_lines[:2]

        else:

            bio = self.profile.get("bio", "")

            parts = [
                part.strip()
                for part in bio.split("|")
                if part.strip()
            ]

            if len(parts) > 1:
                lines = parts[1:3]

            elif parts:
                lines = parts[:1]

            else:
                lines = [
                    "Building projects and exploring technology."
                ]

        while len(lines) < 2:
            lines.append("")

        return [
            self.clean_text(lines[0]),
            self.clean_text(lines[1])
        ]

    # ========================================================
    # GITHUB STATISTICS
    # ========================================================

    def get_statistics(self):

        repositories = self.statistics.get(
            "owned_repositories",
            0
        )

        stars = self.statistics.get(
            "total_stars",
            0
        )

        followers = self.profile.get(
            "followers",
            0
        )

        return {
            "repositories": repositories,
            "total_stars": stars,
            "followers": followers
        }

    # ========================================================
    # DYNAMIC ROLE ANIMATION CSS
    # ========================================================

    def generate_role_css(self):

        total_duration = (
            self.duration_per_role * len(self.roles)
        )

        css = f"""
        .role-cycle {{
            opacity: 0;
            animation-name: roleChange;
            animation-duration: {total_duration}s;
            animation-iteration-count: infinite;
            animation-timing-function: ease-in-out;
        }}

        @keyframes roleChange {{
            0%, 5% {{
                opacity: 0;
            }}

            8%, 18% {{
                opacity: 1;
            }}

            23%, 100% {{
                opacity: 0;
            }}
        }}
        """

        return css

    # ========================================================
    # GENERATE DYNAMIC ROLE COMPONENT
    # ========================================================

    def generate_role_component(self):

        print("[INFO] Generating animated role component...")

        component = [
            '<g class="mono" '
            'font-size="21" '
            'font-weight="600" '
            'fill="#E5E8EF">'
        ]

        for index, role in enumerate(self.roles):

            delay = index * self.duration_per_role

            role_text = self.clean_text(role)

            component.append(
                f'<text '
                f'x="52" '
                f'y="310" '
                f'class="role-cycle role-{index + 1}" '
                f'style="animation-delay:{delay}s">'
                f'<tspan fill="#FF7A00">&#x276F;</tspan> '
                f'{role_text}'
                f'</text>'
            )

        component.append("</g>")

        print(
            f"[SUCCESS] Generated {len(self.roles)} animated roles."
        )

        return "\n".join(component)

    # ========================================================
    # GENERATE ANIMATED CHARACTER COMPONENT
    # ========================================================

    def generate_character_component(self):

        print("[INFO] Generating character component...")

        if not self.character_enabled:

            self.character_component = ""

            print("[INFO] Character component disabled.")

            return ""

        image_width = self.character_config.get(
            "width",
            450
        )

        image_height = self.character_config.get(
            "height",
            338
        )

        for value, name in (
            (image_width, "width"),
            (image_height, "height")
        ):

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or value <= 0
            ):
                raise ValueError(
                    f"Character {name} must be a positive number."
                )

        area = CHARACTER_AREA

        if image_width > area["width"] or image_height > area["height"]:
            print(
                "[WARNING] Character dimensions exceed the display area. "
                "The SVG will scale the image to fit."
            )

        x = area["x"] + (area["width"] - image_width) / 2
        y = area["y"] + (area["height"] - image_height) / 2

        # Read and encode the original animated GIF.

        with self.character_image_path.open("rb") as file:
            gif_data = file.read()

        encoded_gif = base64.b64encode(
            gif_data
        ).decode("ascii")

        data_uri = (
            "data:image/gif;base64,"
            + encoded_gif
        )

        image_element = (
            f'<image '
            f'x="{x:.2f}" '
            f'y="{y:.2f}" '
            f'width="{image_width}" '
            f'height="{image_height}" '
            f'href="{data_uri}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'/>'
        )

        components = []

        # Optional chakra glow.

        if self.character_config.get("chakra_glow", True):

            components.append(
                '<circle '
                'cx="950" '
                'cy="265" '
                'r="180" '
                'fill="url(#chakraGlow)" '
                'class="pulse"/>'
            )

        components.append(image_element)

        self.character_component = "\n".join(components)

        print("[SUCCESS] Animated GIF embedded.")
        print("[INFO] Original GIF frames preserved.")
        print("[INFO] Original GIF animation timing preserved.")

        return self.character_component

    # ========================================================
    # CHARACTER PLACEHOLDER VISIBILITY
    # ========================================================

    def generate_character_visibility_css(self):

        if self.character_enabled:

            return """
            #character-placeholder {
                display: none;
            }

            #character-area {
                display: inline;
            }
            """

        return """
        #character-placeholder {
            display: inline;
        }

        #character-area {
            display: none;
        }
        """

    # ========================================================
    # BUILD TEMPLATE REPLACEMENTS
    # ========================================================

    def build_replacements(self):

        description_1, description_2 = (
            self.get_description_lines()
        )

        stats = self.get_statistics()

        role_component = self.generate_role_component()

        character_component = self.generate_character_component()

        replacements = {

            "{{DISPLAY_NAME}}": self.clean_text(
                self.get_display_name()
            ),

            "{{TERMINAL_USER}}": self.clean_text(
                self.profile.get("username", "")
            ),

            "{{DESCRIPTION_LINE_1}}": description_1,

            "{{DESCRIPTION_LINE_2}}": description_2,

            "{{REPOSITORIES}}": str(
                stats["repositories"]
            ),

            "{{TOTAL_STARS}}": str(
                stats["total_stars"]
            ),

            "{{FOLLOWERS}}": str(
                stats["followers"]
            ),

            "{{TAGLINE}}": self.clean_text(
                self.tagline
            ),

            "{{ROLE_COMPONENT}}": role_component,

            "{{CHARACTER_COMPONENT}}": character_component

        }

        return replacements

    # ========================================================
    # GENERATE HERO SVG
    # ========================================================

    def generate(self):

        print("[INFO] Loading Naruto hero template...")

        template = TEMPLATE_FILE.read_text(
            encoding="utf-8"
        )

        replacements = self.build_replacements()

        print("[INFO] Injecting dynamic GitHub information...")

        for placeholder, value in replacements.items():

            template = template.replace(
                placeholder,
                value
            )

        # Insert role and character CSS.

        extra_css = (
            self.generate_role_css()
            + "\n"
            + self.generate_character_visibility_css()
        )

        if "</style>" not in template:
            raise ValueError(
                "SVG template must contain a <style> section."
            )

        template = template.replace(
            "</style>",
            extra_css + "\n</style>",
            1
        )

        # Check unresolved placeholders.

        remaining = re.findall(
            r"\{\{[A-Z0-9_]+\}\}",
            template
        )

        if remaining:
            raise ValueError(
                "Unresolved template placeholders: "
                + ", ".join(sorted(set(remaining)))
            )

        # Create output directory.

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Save generated SVG.

        OUTPUT_FILE.write_text(
            template,
            encoding="utf-8"
        )

        print("[SUCCESS] Naruto hero SVG generated.")
        print(f"[INFO] Output: {OUTPUT_FILE}")

    # ========================================================
    # VALIDATE GENERATED SVG
    # ========================================================

    def validate_output(self):

        print("[INFO] Validating generated SVG...")

        if not OUTPUT_FILE.exists():
            raise FileNotFoundError(
                "Generated hero SVG was not created."
            )

        content = OUTPUT_FILE.read_text(
            encoding="utf-8"
        )

        checks = {

            "SVG opening tag":
                "<svg" in content,

            "SVG closing tag":
                "</svg>" in content,

            "Username inserted":
                self.profile["username"] in content,

            "Display name inserted":
                self.clean_text(self.get_display_name()) in content,

            "No unresolved placeholders":
                "{{" not in content,

            "Role animation CSS":
                "@keyframes roleChange" in content,

            "Role component generated":
                'class="role-cycle' in content,

            "All configured roles inserted":
                all(
                    self.clean_text(role) in content
                    for role in self.roles
                ),

            "Tagline inserted":
                self.clean_text(self.tagline) in content

        }

        if self.character_enabled:

            checks["Animated GIF embedded"] = (
                "data:image/gif;base64," in content
            )

            checks["Character placeholder hidden"] = (
                "#character-placeholder" in content
                and "display: none" in content
            )

        failed = False

        for name, result in checks.items():

            status = "PASS" if result else "FAIL"

            print(f"[{status}] {name}")

            if not result:
                failed = True

        # Validate XML structure.

        try:

            ET.parse(str(OUTPUT_FILE))

            print("[PASS] SVG XML structure")

        except ET.ParseError as error:

            print(f"[FAIL] SVG XML structure: {error}")

            failed = True

        if failed:
            raise RuntimeError(
                "Hero SVG validation failed."
            )

        print("[SUCCESS] Hero SVG validation completed.")

    # ========================================================
    # DISPLAY SUMMARY
    # ========================================================

    def display_summary(self):

        stats = self.get_statistics()

        print("\n" + "=" * 55)

        print("[HERO SUMMARY]")

        print("=" * 55)

        print(f"Username: {self.profile.get('username')}")

        print(f"Display Name: {self.get_display_name()}")

        print("\n[ANIMATED ROLES]")

        for index, role in enumerate(
            self.roles,
            start=1
        ):

            print(f"{index}. {role}")

        print("\n[STATISTICS]")

        print(f"Repositories: {stats['repositories']}")

        print(f"Total Stars: {stats['total_stars']}")

        print(f"Followers: {stats['followers']}")

        print(f"\nRole Duration: {self.duration_per_role}s")

        print(f"Tagline: {self.tagline}")

        print("\n[CHARACTER]")

        print(f"Enabled: {self.character_enabled}")

        if self.character_enabled:
            print(f"GIF: {self.character_image_path}")

        print(f"\nOutput: {OUTPUT_FILE}")

    # ========================================================
    # MAIN EXECUTION
    # ========================================================

    def run(self):

        print("=" * 55)

        print(" NARUTO PROFILE - DYNAMIC HERO GENERATOR v4.0")

        print("=" * 55)

        self.load_data()

        self.generate()

        self.validate_output()

        self.display_summary()

        print(
            "\n[SUCCESS] Dynamic Naruto hero generation completed."
        )


# ============================================================
# ENTRY POINT
# ============================================================

def main():

    try:

        generator = NarutoHeroGenerator()

        generator.run()

    except (
        FileNotFoundError,
        ValueError,
        RuntimeError,
        json.JSONDecodeError
    ) as error:

        print(f"\n[ERROR] {error}")

        sys.exit(1)

    except Exception as error:

        print(f"\n[ERROR] Unexpected error: {error}")

        sys.exit(1)


if __name__ == "__main__":

    main()
