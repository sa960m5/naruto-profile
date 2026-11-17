import json
import os
import urllib.request
import urllib.error

from pathlib import Path


# ==================================================
# NARUTO PROFILE - GITHUB PROFILE FETCHER v1.0
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILE = ROOT / "config" / "config.json"
OUTPUT_FILE = ROOT / "assets" / "data" / "profile.json"

API_BASE = "https://api.github.com"


# ==================================================
# CONFIGURATION
# ==================================================

def load_configuration():

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            "config/config.json not found."
        )

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        config = json.load(file)

    username = os.getenv(
        "GITHUB_USERNAME",
        config.get("github_username", "")
    ).strip()

    if not username:
        raise ValueError("GitHub username is missing.")

    return config, username


# ==================================================
# GITHUB API REQUEST
# ==================================================

def github_request(endpoint):

    url = f"{API_BASE}{endpoint}"

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
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
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as error:
        if error.code == 404:
            raise RuntimeError("GitHub user or resource not found.")

        if error.code == 403:
            raise RuntimeError(
                "GitHub API rate limit exceeded or access denied."
            )

        raise RuntimeError(
            f"GitHub API returned HTTP {error.code}."
        )

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Unable to connect to GitHub: {error.reason}"
        )


# ==================================================
# FETCH USER PROFILE
# ==================================================

def fetch_profile(username):

    print("[INFO] Fetching GitHub profile...")

    profile = github_request(f"/users/{username}")

    return {
        "username": profile.get("login", username),
        "display_name": profile.get("name") or username,
        "bio": profile.get("bio") or "",
        "avatar_url": profile.get("avatar_url", ""),
        "profile_url": profile.get("html_url", ""),
        "location": profile.get("location") or "",
        "company": profile.get("company") or "",
        "blog": profile.get("blog") or "",
        "public_repositories": profile.get("public_repos", 0),
        "followers": profile.get("followers", 0),
        "following": profile.get("following", 0),
        "created_at": profile.get("created_at", "")
    }


# ==================================================
# FETCH ALL PUBLIC REPOSITORIES
# ==================================================

def fetch_repositories(username):

    print("[INFO] Fetching public repositories...")

    repositories = []
    page = 1

    while True:

        endpoint = (
            f"/users/{username}/repos"
            f"?type=owner&per_page=100&page={page}"
        )

        batch = github_request(endpoint)

        if not batch:
            break

        repositories.extend(batch)

        if len(batch) < 100:
            break

        page += 1

    return repositories


# ==================================================
# CALCULATE STATISTICS
# ==================================================

def calculate_statistics(repositories):

    owned_repositories = [
        repo for repo in repositories
        if not repo.get("fork", False)
    ]

    total_stars = sum(
        repo.get("stargazers_count", 0)
        for repo in repositories
    )

    total_forks = sum(
        repo.get("forks_count", 0)
        for repo in repositories
    )

    languages = {}

    for repo in repositories:

        language = repo.get("language")

        if language:
            languages[language] = languages.get(language, 0) + 1

    return {
        "repositories_fetched": len(repositories),
        "owned_repositories": len(owned_repositories),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "languages": languages
    }


# ==================================================
# SAVE PROFILE DATA
# ==================================================

def save_profile(data):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"[SUCCESS] Profile data saved: {OUTPUT_FILE}")


# ==================================================
# MAIN
# ==================================================

def main():

    print("=" * 55)
    print(" NARUTO PROFILE - GITHUB DATA FETCHER v1.0")
    print("=" * 55)

    config, username = load_configuration()

    profile = fetch_profile(username)

    repositories = fetch_repositories(username)

    statistics = calculate_statistics(repositories)

    result = {
        "profile": profile,
        "statistics": statistics,
        "preferences": config.get("hero", {}),
        "generated_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat()
    }

    save_profile(result)

    print("\n[PROFILE SUMMARY]")
    print(f"Username: {profile['username']}")
    print(f"Display Name: {profile['display_name']}")
    print(f"Public Repositories: {profile['public_repositories']}")
    print(f"Followers: {profile['followers']}")
    print(f"Following: {profile['following']}")

    print("\n[REPOSITORY STATISTICS]")
    print(f"Repositories Fetched: {statistics['repositories_fetched']}")
    print(f"Owned Repositories: {statistics['owned_repositories']}")
    print(f"Total Stars: {statistics['total_stars']}")
    print(f"Total Forks: {statistics['total_forks']}")

    print("\n[SUCCESS] GitHub profile fetching completed.")


if __name__ == "__main__":
    main()