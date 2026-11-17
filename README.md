# Naruto Profile

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Theme-Naruto-orange?style=for-the-badge" alt="Naruto Theme">
  <img src="https://img.shields.io/badge/Automation-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
</p>

<p align="center">
  A configurable Python framework for building animated, Naruto-inspired GitHub profile READMEs.
</p>

<p align="center">
  <b>Customize your profile. Showcase your projects. Follow your own ninja way.</b>
</p>

---

## Overview

Naruto Profile is a configurable GitHub profile customization framework built with Python, SVG, and GIF animations.

It collects public GitHub profile and repository information, generates animated visual components, and builds a personalized profile README.

The framework is designed to be reusable. You can configure your GitHub username, profile content, colors, artwork, animations, and optional sections without changing the generator source code.

## Features

### Naruto Theme
- Naruto-inspired dark visual design.
- Orange and gold accent colors.
- Animated character artwork.
- Chakra effects and Rasengan visuals.
- Customizable repository cards.

### Animated Repository Showcase
- Fetches public GitHub repositories.
- Generates an animated repository showcase.
- Displays repository information and programming languages.
- Supports configurable repository limits and sorting.

### Dynamic Hero Section
- Generates a personalized SVG hero section.
- Displays a configurable introduction and developer roles.
- Uses GitHub profile information and repository statistics.
- Supports custom character artwork.

### Ninja Way Section
- Separate, configurable profile section.
- Fixed reference-based SVG layout.
- Custom artwork, introduction, highlights, and quote.
- Configurable colors and footer tagline.
- Three highlight cards in the supplied example configuration.

### Profile README Generator
- Generates a GitHub profile README.
- Supports banner, About, repository showcase, repository links, statistics, contributions, social links, and footer sections.
- Keeps generated profile content separate from the framework source.

### GitHub Actions Automation
- Manual workflow execution.
- Automatic execution when the framework's main branch is updated.
- Scheduled daily generation.
- Publishes generated files to a configured GitHub profile repository.

---

## Project Structure

```text
naruto-profile/
│
├── .github/
│   └── workflows/
│       └── naruto-profile.yml
│
├── assets/
│   ├── characters/
│   ├── data/
│   ├── gif/
│   ├── hero/
│   ├── ninja-way/
│   └── svg/
│
├── config/
│   ├── config.example.json
│   ├── config.json
│   ├── naruto_theme.json
│   ├── ninja_way.example.json
│   ├── ninja_way.json
│   └── settings.py
│
├── scripts/
│   ├── fetch_profile.py
│   ├── fetch_repositories.py
│   ├── generate_animated_showcase.py
│   ├── generate_cards.py
│   ├── generate_hero.py
│   ├── generate_ninja_way.py
│   ├── generate_readme.py
│   └── naruto_theme.py
│
├── templates/
│   ├── cards/
│   ├── hero/
│   │   └── hero-template.svg
│   ├── ninja-way/
│   │   └── ninja-way-template.svg
│   └── profile/
│
├── requirements.txt
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

Generated files and local configuration may not be present in a fresh clone.

---

## Requirements

- Python 3.13 or compatible version.
- Git.
- A GitHub account.
- Internet connection for GitHub API access.

Python dependencies are listed in `requirements.txt`.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/naruto-profile.git
cd naruto-profile
```

Create a virtual environment:

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuration

The framework uses JSON configuration files.

### 1. Main Configuration

Create your local configuration:

**Windows**

```powershell
Copy-Item config\config.example.json config\config.json
```

**Linux / macOS**

```bash
cp config/config.example.json config/config.json
```

Set your GitHub username:

```json
{
    "github_username": "YOUR_GITHUB_USERNAME"
}
```

The example configuration also contains settings for:

- Animation preferences.
- Profile sections.
- Repository visibility and sorting.
- Hero roles and description.
- Character artwork.
- Appearance and colors.

### 2. Naruto Theme Configuration

Edit:

```text
config/naruto_theme.json
```

This file controls the Naruto visual theme, including:

- Background and card colors.
- Character artwork and positioning.
- Rasengan effects.
- Chakra particles.
- Repository card styling.
- Animation settings.

### 3. Ninja Way Configuration

Create your local configuration:

**Windows**

```powershell
Copy-Item config\ninja_way.example.json config\ninja_way.json
```

**Linux / macOS**

```bash
cp config/ninja_way.example.json config/ninja_way.json
```

You can customize:

- Section heading and introduction.
- Artwork and dimensions.
- Highlight cards.
- Quote.
- Footer tagline.
- Background and accent colors.

Keep your local configuration files separate from the reusable example configurations.

---

## Running the Generators

Run the scripts from the project root directory.

### Fetch GitHub repositories

```bash
python scripts/fetch_repositories.py
```

### Fetch GitHub profile information

```bash
python scripts/fetch_profile.py
```

### Generate Naruto theme

```bash
python scripts/naruto_theme.py
```

### Generate animated repository showcase

```bash
python scripts/generate_animated_showcase.py
```

### Generate Hero section

```bash
python scripts/generate_hero.py
```

### Generate Ninja Way section

```bash
python scripts/generate_ninja_way.py
```

### Generate profile README

```bash
python scripts/generate_readme.py
```

The generated profile README is written to:

```text
dist/profile/README.md
```

Generated visual assets are stored in their respective asset directories.

---

## GitHub Actions Setup

The framework includes a GitHub Actions workflow:

```text
.github/workflows/naruto-profile.yml
```

It supports:

- Manual execution through `workflow_dispatch`.
- Execution when changes are pushed to `main`.
- Daily scheduled execution.

### Step 1: Create a GitHub Profile Repository

Create a public repository whose name exactly matches your GitHub username.

For example:

```text
YOUR_USERNAME/YOUR_USERNAME
```

GitHub recognizes this as your profile README repository.

### Step 2: Configure Repository Variables

In your framework repository, navigate to:

```text
Settings → Secrets and variables → Actions → Variables
```

Create:

| Variable | Value |
|---|---|
| `PROFILE_USERNAME` | Your GitHub username |

### Step 3: Configure Repository Secrets

Create the following repository secret:

| Secret | Purpose |
|---|---|
| `PROFILE_REPO_TOKEN` | Token with permission to update the profile repository |

Use a fine-grained personal access token with the minimum required permissions for the target profile repository.

Never commit tokens or credentials to the repository.

### Step 4: Run the Workflow

Navigate to:

```text
Actions → Naruto Profile Automation
```

Select:

```text
Run workflow
```

The workflow fetches profile information, generates visual components and the README, then publishes the generated files to your profile repository.

**Note:** Before using automated deployment, ensure the Ninja Way configuration and required artwork files are available in the framework repository. See the configuration and asset requirements above.

---

## Customization

The framework is intended to be reusable.

You can customize your profile without modifying the generator source code.

| Component | Configuration |
|---|---|
| GitHub username | `config/config.json` |
| Profile sections | `config/config.json` |
| Naruto theme | `config/naruto_theme.json` |
| Hero section | `config/config.json` |
| Ninja Way section | `config/ninja_way.json` |
| Animation preferences | JSON configuration |
| Artwork | Asset files |

You can replace the supplied artwork with your own appropriately licensed assets.

---

## Contributing

Contributions are welcome.

If you want to improve the framework:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test the generators.
5. Submit a pull request.

Please keep the framework configurable and avoid hardcoding personal GitHub usernames or profile information.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with Python, SVG, GIF animations, and a little bit of ninja spirit.
</p>
```