import json

from pathlib import Path


# ==================================================
# NARUTO THEME CONFIGURATION MANAGER
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

THEME_FILE = ROOT / "config" / "naruto_theme.json"


class NarutoTheme:

    def __init__(self):

        self.config = self._load_config()

        self._validate_config()

    # ==============================================
    # LOAD CONFIGURATION
    # ==============================================

    def _load_config(self):

        if not THEME_FILE.exists():

            raise FileNotFoundError(
                f"Naruto theme configuration not found: {THEME_FILE}"
            )

        try:

            with THEME_FILE.open(
                "r",
                encoding="utf-8"
            ) as file:

                config = json.load(file)

        except json.JSONDecodeError as error:

            raise ValueError(
                f"Invalid Naruto theme JSON: {error}"
            )

        print("[SUCCESS] Naruto configuration loaded.")

        return config

    # ==============================================
    # VALIDATE CONFIGURATION
    # ==============================================

    def _validate_config(self):

        required_sections = [
            "colors",
            "character",
            "rasengan",
            "chakra_effects",
            "repository_cards",
            "animation"
        ]

        for section in required_sections:

            if section not in self.config:

                raise ValueError(
                    f"Missing configuration section: {section}"
                )

        # Validate animation.

        animation = self.config["animation"]

        fps = animation.get("fps", 12)

        duration = animation.get(
            "duration_seconds",
            4
        )

        if not isinstance(fps, int) or not 1 <= fps <= 30:

            raise ValueError(
                "Animation FPS must be between 1 and 30."
            )

        if (
            not isinstance(duration, int)
            or not 1 <= duration <= 10
        ):

            raise ValueError(
                "Animation duration must be between 1 and 10."
            )

        # Validate repository cards.

        max_cards = self.config[
            "repository_cards"
        ].get("max_cards", 8)

        if (
            not isinstance(max_cards, int)
            or not 1 <= max_cards <= 8
        ):

            raise ValueError(
                "Maximum repository cards must be between 1 and 8."
            )

        # Validate colors.

        for name, value in self.config["colors"].items():

            if (
                not isinstance(value, str)
                or len(value) != 7
                or not value.startswith("#")
            ):

                raise ValueError(
                    f"Invalid hexadecimal color: {name}"
                )

            try:

                int(value[1:], 16)

            except ValueError:

                raise ValueError(
                    f"Invalid hexadecimal color: {name}"
                )

    # ==============================================
    # GET COMPLETE CONFIGURATION
    # ==============================================

    def get_all(self):

        return self.config

    # ==============================================
    # GET COLORS
    # ==============================================

    def get_colors(self):

        return self.config["colors"]

    # ==============================================
    # GET CHARACTER SETTINGS
    # ==============================================

    def get_character(self):

        return self.config["character"]

    # ==============================================
    # GET RASENGAN SETTINGS
    # ==============================================

    def get_rasengan(self):

        return self.config["rasengan"]

    # ==============================================
    # GET CHAKRA EFFECT SETTINGS
    # ==============================================

    def get_chakra_effects(self):

        return self.config["chakra_effects"]

    # ==============================================
    # GET REPOSITORY CARD SETTINGS
    # ==============================================

    def get_repository_cards(self):

        return self.config["repository_cards"]

    # ==============================================
    # GET ANIMATION SETTINGS
    # ==============================================

    def get_animation(self):

        return self.config["animation"]

    # ==============================================
    # GET SINGLE SETTING
    # ==============================================

    def get(self, section, key, default=None):

        return self.config.get(
            section,
            {}
        ).get(key, default)


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    theme = NarutoTheme()

    print("\n" + "=" * 45)
    print(" NARUTO THEME CONFIGURATION")
    print("=" * 45)

    print(
        "Theme:",
        theme.get_all()["theme_name"]
    )

    print(
        "Primary Color:",
        theme.get_colors()["primary"]
    )

    print(
        "Character Enabled:",
        theme.get_character()["enabled"]
    )

    print(
        "Rasengan Enabled:",
        theme.get_rasengan()["enabled"]
    )

    print(
        "Maximum Cards:",
        theme.get_repository_cards()["max_cards"]
    )

    print(
        "Animation FPS:",
        theme.get_animation()["fps"]
    )

    print("\n[SUCCESS] Naruto theme engine operational.")
