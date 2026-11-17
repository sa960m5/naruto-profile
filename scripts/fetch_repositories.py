import json
import os
import sys
import urllib.request
import urllib.error

from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from config.settings import load_config, ConfigurationError


# ==========================================
# NARUTO PROFILE - REPOSITORY COLLECTOR
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "assets" / "data"
OUTPUT_FILE = OUTPUT_DIR / "repositories.json"

GITHUB_API = "https://api.github.com"


class GitHubAPIError(Exception):
    pass


def fetch_page(username, page):
    """Fetch one page of public repositories."""

    url = (
        f"{GITHUB_API}/users/{username}/repos"
        f"?type=owner&sort=updated"
        f"&direction=desc&per_page=100&page={page}"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Naruto-Profile-Framework"
    }

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        url,
        headers=headers
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            return json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:

        if error.code == 403:
            raise GitHubAPIError(
                "GitHub API rate limit or access restriction."
            )

        if error.code == 404:
            raise GitHubAPIError(
                f"GitHub user '{username}' was not found."
            )

        raise GitHubAPIError(
            f"GitHub API returned HTTP {error.code}."
        )

    except urllib.error.URLError as error:

        raise GitHubAPIError(
            f"Network connection failed: {error.reason}"
        )


def fetch_all_repositories(username):
    """Fetch every page of public repositories."""

    repositories = []
    page = 1

    while True:

        print(f"[INFO] Fetching page {page}...")

        data = fetch_page(username, page)

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repositories


def process_repositories(raw_repositories, config):
    """Filter, sort and format repository information."""

    settings = config["repositories"]

    filtered = []

    for repo in raw_repositories:

        if repo.get("visibility") != "public":
            continue

        if settings.get("exclude_forks", False):
            if repo.get("fork"):
                continue

        if settings.get("exclude_archived", False):
            if repo.get("archived"):
                continue

        filtered.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "description": repo.get("description") or "",
            "language": repo.get("language") or "Not specified",
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "updated_at": repo["updated_at"],
            "created_at": repo["created_at"],
            "fork": repo["fork"],
            "archived": repo["archived"],
            "visibility": repo["visibility"]
        })

    sort_by = settings.get("sort_by", "updated")
    sort_order = settings.get("sort_order", "desc")

    sort_keys = {
        "updated": "updated_at",
        "created": "created_at",
        "name": "name",
        "stars": "stars"
    }

    key = sort_keys[sort_by]

    filtered.sort(
        key=lambda repo: repo[key].lower()
        if isinstance(repo[key], str)
        else repo[key],
        reverse=(sort_order == "desc")
    )

    max_repositories = settings.get(
        "max_repositories",
        12
    )

    return filtered[:max_repositories]


def save_repositories(username, repositories):
    """Save the latest repository dataset."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output = {
        "username": username,
        "total_repositories": len(repositories),
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "repositories": repositories
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n[SUCCESS] Repository data generated.")
    print(f"[INFO] Total repositories: {len(repositories)}")
    print(f"[INFO] Output: {OUTPUT_FILE}")


def main():

    print("=" * 55)
    print(" NARUTO PROFILE - REPOSITORY COLLECTOR")
    print("=" * 55)

    try:

        config = load_config()

        username = config["github_username"]

        print(f"\n[INFO] GitHub account: {username}")

        raw_repositories = fetch_all_repositories(
            username
        )

        repositories = process_repositories(
            raw_repositories,
            config
        )

        save_repositories(
            username,
            repositories
        )

        print("\n[INFO] Repository collection completed.")

        for repo in repositories:

            print(
                f"  {repo['name']} "
                f"| {repo['language']} "
                f"| Stars: {repo['stars']}"
            )

    except ConfigurationError as error:

        print(f"\n[CONFIG ERROR] {error}")
        sys.exit(1)

    except GitHubAPIError as error:

        print(f"\n[API ERROR] {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()