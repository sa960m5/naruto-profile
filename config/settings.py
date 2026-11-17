import json
import os

from pathlib import Path


# ==========================================
# NARUTO PROFILE - CONFIGURATION ENGINE
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILE = PROJECT_ROOT / "config" / "config.json"
EXAMPLE_CONFIG = PROJECT_ROOT / "config" / "config.example.json"


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""


def load_config():

    if not CONFIG_FILE.exists():
        raise ConfigurationError(
            "config.json not found. "
            "Copy config.example.json to config.json "
            "and configure your GitHub username."
        )

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            config = json.load(file)

    except json.JSONDecodeError as error:
        raise ConfigurationError(
            f"Invalid JSON configuration: {error}"
        )

    validate_config(config)

    # Environment variable takes priority.
    username = os.getenv("GITHUB_USERNAME")

    if username:
        config["github_username"] = username.strip()

    return config


def validate_config(config):

    if not isinstance(config, dict):
        raise ConfigurationError(
            "Configuration must be a JSON object."
        )

    username = config.get("github_username")

    if not isinstance(username, str) or not username.strip():
        raise ConfigurationError(
            "A valid GitHub username is required."
        )

    profile = config.get("profile", {})
    repositories = config.get("repositories", {})

    if not isinstance(profile, dict):
        raise ConfigurationError(
            "'profile' must be an object."
        )

    if not isinstance(repositories, dict):
        raise ConfigurationError(
            "'repositories' must be an object."
        )

    visibility = repositories.get("visibility", "public")

    if visibility not in ("public", "all"):
        raise ConfigurationError(
            "Repository visibility must be 'public' or 'all'."
        )

    sort_by = repositories.get("sort_by", "updated")

    if sort_by not in ("updated", "created", "name", "stars"):
        raise ConfigurationError(
            "Invalid repository sorting option."
        )

    max_repositories = repositories.get("max_repositories", 12)

    if (
        not isinstance(max_repositories, int)
        or isinstance(max_repositories, bool)
        or max_repositories < 1
    ):
        raise ConfigurationError(
            "max_repositories must be a positive integer."
        )


def get_setting(*keys, default=None):

    config = load_config()

    value = config

    for key in keys:

        if not isinstance(value, dict) or key not in value:
            return default

        value = value[key]

    return value


if __name__ == "__main__":

    try:
        configuration = load_config()

        print("=" * 50)
        print(" NARUTO PROFILE - CONFIGURATION ENGINE")
        print("=" * 50)

        print(
            f"\nGitHub Username: "
            f"{configuration['github_username']}"
        )

        print(
            f"Theme: "
            f"{configuration['profile'].get('theme', 'default')}"
        )

        print(
            f"Maximum Repositories: "
            f"{configuration['repositories'].get('max_repositories', 12)}"
        )

        print("\n[SUCCESS] Configuration loaded.")

    except ConfigurationError as error:
        print(f"\n[CONFIGURATION ERROR] {error}")
        raise SystemExit(1)