import json
import math
import random

from pathlib import Path
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageSequence,
)

from naruto_theme import NarutoTheme


# ==================================================
# NARUTO PROFILE - CHAKRA ANIMATION ENGINE v1.3
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT / "assets" / "data" / "repositories.json"

OUTPUT_FILE = (
    ROOT / "assets" / "gif" / "repository-showcase.gif"
)

LANGUAGE_COLORS = {
    "Python": (55, 155, 230),
    "JavaScript": (240, 219, 79),
    "TypeScript": (49, 120, 198),
    "Dart": (0, 190, 190),
    "PHP": (119, 123, 180),
    "Java": (220, 100, 70),
    "HTML": (235, 90, 55),
    "CSS": (100, 120, 240),
    "C++": (80, 120, 220),
    "Go": (0, 170, 190),
}


# ==================================================
# THEME INITIALIZATION
# ==================================================

theme = NarutoTheme()

THEME_CONFIG = theme.get_all()

COLORS = theme.get_colors()
CHARACTER = theme.get_character()
RASENGAN = theme.get_rasengan()
EFFECTS = theme.get_chakra_effects()
CARDS = theme.get_repository_cards()
ANIMATION = theme.get_animation()


# ==================================================
# COLOR CONVERSION
# ==================================================

def hex_to_rgb(value):

    value = value.lstrip("#")

    return tuple(
        int(value[i:i + 2], 16)
        for i in (0, 2, 4)
    )


BG = hex_to_rgb(COLORS["background"])
CARD = hex_to_rgb(COLORS["card_background"])

ORANGE = hex_to_rgb(COLORS["primary"])
GOLD = hex_to_rgb(COLORS["secondary"])

WHITE = hex_to_rgb(COLORS["text"])
MUTED = hex_to_rgb(COLORS["muted"])

BLUE = hex_to_rgb(COLORS["chakra_blue"])
LIGHT_BLUE = hex_to_rgb(COLORS["chakra_glow"])


# ==================================================
# CANVAS SETTINGS
# ==================================================

WIDTH = 960
HEIGHT = 950

FPS = ANIMATION["fps"]
DURATION = ANIMATION["duration_seconds"]

TOTAL_FRAMES = FPS * DURATION


# ==================================================
# CHARACTER SETTINGS
# ==================================================

RUNNER_WIDTH = CHARACTER["width"]
RUNNER_HEIGHT = CHARACTER["height"]

NARUTO_GIF = ROOT / CHARACTER["animation_file"]

RUNNER_POSITION = CHARACTER["position"]

RUNNER_X = WIDTH - RUNNER_WIDTH - 25
RUNNER_Y = 8


# ==================================================
# RASENGAN SETTINGS
# ==================================================

CHAKRA_RADIUS = RASENGAN["radius"]

CHAKRA_POSITION = RASENGAN["position"]

if CHAKRA_POSITION == "bottom_left":
    CHAKRA_CENTER_X = 85
    CHAKRA_CENTER_Y = HEIGHT - 85
else:
    CHAKRA_CENTER_X = WIDTH - 85
    CHAKRA_CENTER_Y = HEIGHT - 85


# ==================================================
# REPOSITORY CARD SETTINGS
# ==================================================

MAX_CARDS = CARDS["max_cards"]

CARD_WIDTH = 430
CARD_HEIGHT = 145

CARD_RADIUS = CARDS["border_radius"]
CARD_BORDER_WIDTH = CARDS["border_width"]


# ==================================================
# FONT LOADER
# ==================================================

def load_font(size, bold=False):

    candidates = (
        ["arialbd.ttf", "segoeuib.ttf"]
        if bold
        else ["arial.ttf", "segoeui.ttf"]
    )

    for font_name in candidates:

        try:
            return ImageFont.truetype(font_name, size)

        except OSError:
            continue

    return ImageFont.load_default()


TITLE_FONT = load_font(27, True)
CARD_FONT = load_font(17, True)
BODY_FONT = load_font(12)
SMALL_FONT = load_font(11)


# ==================================================
# JSON LOADER
# ==================================================

def load_json(path):

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


# ==================================================
# TEXT PROCESSING
# ==================================================

def fit_text(draw, text, font, max_width):

    text = str(text)

    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return text

    while text:

        candidate = text[:-1].rstrip() + "..."

        if draw.textbbox(
            (0, 0),
            candidate,
            font=font
        )[2] <= max_width:

            return candidate

        text = text[:-1]

    return "..."


# ==================================================
# NARUTO GIF LOADER
# ==================================================

def load_naruto_animation():

    if not CHARACTER["enabled"]:

        print("[INFO] Naruto character animation disabled.")
        return []

    if not NARUTO_GIF.exists():

        print("[WARNING] Naruto GIF not found.")
        print(f"[INFO] Expected location: {NARUTO_GIF}")

        return []

    frames = []

    try:

        with Image.open(NARUTO_GIF) as gif:

            for frame in ImageSequence.Iterator(gif):

                rgba = frame.convert("RGBA")

                background = Image.new(
                    "RGBA",
                    rgba.size,
                    BG + (255,)
                )

                background.alpha_composite(rgba)

                runner = background.convert("RGB")

                runner.thumbnail(
                    (RUNNER_WIDTH, RUNNER_HEIGHT),
                    Image.Resampling.LANCZOS
                )

                # Remove completely white frames.

                pixels = list(
                    runner.resize((30, 30)).getdata()
                )

                white_pixels = sum(
                    1 for r, g, b in pixels
                    if r > 245 and g > 245 and b > 245
                )

                if white_pixels / len(pixels) > 0.90:
                    continue

                frames.append(runner.copy())

    except Exception as error:

        print(f"[WARNING] Naruto GIF loading failed: {error}")
        return []

    print(f"[SUCCESS] Naruto frames loaded: {len(frames)}")

    return frames


# ==================================================
# PARTICLE ENGINE
# ==================================================

def create_particles(count):

    rng = random.Random(42)

    return [
        {
            "x": rng.randint(0, WIDTH),
            "y": rng.randint(0, HEIGHT),
            "speed": rng.uniform(0.5, 2.0),
            "size": rng.randint(1, 3),
            "phase": rng.uniform(0, math.tau),
        }
        for _ in range(count)
    ]


PARTICLES = create_particles(
    EFFECTS["particle_count"]
    if EFFECTS["enabled"] and EFFECTS["floating_particles"]
    else 0
)


def draw_particles(draw, frame):

    for particle in PARTICLES:

        x = particle["x"] + math.sin(
            frame * 0.08 + particle["phase"]
        ) * 18

        y = (
            particle["y"] - frame * particle["speed"]
        ) % HEIGHT

        alpha = (
            math.sin(
                frame * 0.12 + particle["phase"]
            ) + 1
        ) / 2

        color = (
            ORANGE[0],
            int(100 + alpha * 90),
            int(10 + alpha * 25),
        )

        radius = particle["size"]

        draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            ),
            fill=color
        )


# ==================================================
# BACKGROUND ENGINE
# ==================================================

def draw_background(draw):

    draw.rectangle(
        (0, 0, WIDTH, HEIGHT),
        fill=BG
    )

    if EFFECTS["enabled"] and EFFECTS["energy_lines"]:

        for y in range(0, HEIGHT, 45):

            draw.line(
                (0, y, WIDTH, y),
                fill=(19, 24, 33),
                width=1
            )


# ==================================================
# NARUTO ANIMATION RENDERER
# ==================================================

def draw_naruto(
    image,
    runner_frames,
    frame_number,
):

    if not CHARACTER["enabled"]:
        return

    if not runner_frames:
        return

    runner_index = int(
        frame_number * len(runner_frames) / TOTAL_FRAMES
    )

    runner_index %= len(runner_frames)

    runner = runner_frames[runner_index].copy()

    runner.thumbnail(
        (RUNNER_WIDTH, RUNNER_HEIGHT),
        Image.Resampling.LANCZOS
    )

    if RUNNER_POSITION == "top_left":
        x, y = 25, 8

    elif RUNNER_POSITION == "bottom_right":
        x = WIDTH - RUNNER_WIDTH - 25
        y = HEIGHT - RUNNER_HEIGHT - 25

    elif RUNNER_POSITION == "bottom_left":
        x, y = 25, HEIGHT - RUNNER_HEIGHT - 25

    else:
        x, y = RUNNER_X, RUNNER_Y

    image.paste(runner, (x, y))


# ==================================================
# BLUE RASENGAN CHAKRA ORB
# ==================================================

def draw_chakra_orb(image, frame):

    if not RASENGAN["enabled"]:
        return

    center_x = CHAKRA_CENTER_X
    center_y = CHAKRA_CENTER_Y

    pulse = (
        1 + math.sin(frame * 0.25) * 0.12
        if RASENGAN["pulse"]
        else 1
    )

    radius = int(CHAKRA_RADIUS * pulse)

    # ----------------------------------------------
    # GLOW
    # ----------------------------------------------

    if RASENGAN["glow"]:

        glow = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )

        glow_draw = ImageDraw.Draw(glow)

        for r in range(radius + 28, radius, -3):

            glow_draw.ellipse(
                (
                    center_x - r,
                    center_y - r,
                    center_x + r,
                    center_y + r,
                ),
                outline=LIGHT_BLUE + (35,),
                width=3
            )

        glow = glow.filter(
            ImageFilter.GaussianBlur(13)
        )

        image.alpha_composite(glow)

    draw = ImageDraw.Draw(image)

    # ----------------------------------------------
    # ROTATING CHAKRA PARTICLES
    # ----------------------------------------------

    if RASENGAN["particles"]:

        for i in range(16):

            angle = (
                frame * 0.18 + i * math.tau / 16
                if RASENGAN["rotation"]
                else i * math.tau / 16
            )

            orbit_radius = radius + 13 + math.sin(
                frame * 0.2 + i
            ) * 3

            x = center_x + math.cos(angle) * orbit_radius
            y = center_y + math.sin(angle) * orbit_radius

            particle_radius = 2 + (i % 2)

            draw.ellipse(
                (
                    x - particle_radius,
                    y - particle_radius,
                    x + particle_radius,
                    y + particle_radius,
                ),
                fill=LIGHT_BLUE
            )

    # ----------------------------------------------
    # MAIN RASENGAN
    # ----------------------------------------------

    draw.ellipse(
        (
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
        ),
        fill=BLUE,
        outline=LIGHT_BLUE,
        width=3
    )

    inner_radius = int(radius * 0.60)

    draw.ellipse(
        (
            center_x - inner_radius,
            center_y - inner_radius,
            center_x + inner_radius,
            center_y + inner_radius,
        ),
        fill=(55, 145, 255),
        outline=(180, 225, 255),
        width=2
    )

    highlight_radius = max(
        3,
        int(radius * 0.18)
    )

    draw.ellipse(
        (
            center_x - highlight_radius - 5,
            center_y - highlight_radius - 7,
            center_x + highlight_radius - 5,
            center_y + highlight_radius - 7,
        ),
        fill=(225, 245, 255)
    )


# ==================================================
# ANIMATED REPOSITORY CARD
# ==================================================

def draw_glowing_card(
    image,
    repo,
    x,
    y,
    frame,
    index
):

    draw = ImageDraw.Draw(image)

    # ----------------------------------------------
    # ANIMATED GLOW
    # ----------------------------------------------

    if EFFECTS["enabled"] and CARDS["glow"] and EFFECTS["glowing_borders"]:

        glow = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )

        glow_draw = ImageDraw.Draw(glow)

        pulse = (
            math.sin(frame * 0.22 + index * 0.8) + 1
        ) / 2

        intensity = int(90 + pulse * 165)

        border_color = (
            ORANGE[0],
            int(75 + pulse * 60),
            ORANGE[2],
            intensity
        )

        for thickness in range(9, 0, -2):

            glow_draw.rounded_rectangle(
                (
                    x - thickness,
                    y - thickness,
                    x + CARD_WIDTH + thickness,
                    y + CARD_HEIGHT + thickness,
                ),
                radius=CARD_RADIUS + 2,
                outline=border_color,
                width=2
            )

        glow = glow.filter(
            ImageFilter.GaussianBlur(7)
        )

        image.alpha_composite(glow)

        draw = ImageDraw.Draw(image)

    # ----------------------------------------------
    # MAIN CARD
    # ----------------------------------------------

    draw.rounded_rectangle(
        (
            x,
            y,
            x + CARD_WIDTH,
            y + CARD_HEIGHT,
        ),
        radius=CARD_RADIUS,
        fill=CARD,
        outline=ORANGE,
        width=CARD_BORDER_WIDTH
    )

    # Chakra accent.

    draw.rounded_rectangle(
        (
            x,
            y,
            x + 5,
            y + CARD_HEIGHT,
        ),
        radius=3,
        fill=ORANGE
    )

    # ----------------------------------------------
    # REPOSITORY NAME
    # ----------------------------------------------

    name = fit_text(
        draw,
        repo.get("name", "Unnamed Repository"),
        CARD_FONT,
        375
    )

    draw.text(
        (x + 22, y + 24),
        name,
        fill=WHITE,
        font=CARD_FONT
    )

    # ----------------------------------------------
    # DESCRIPTION
    # ----------------------------------------------

    description = (
        repo.get("description", "").strip()
        or "Explore this project on GitHub."
    )

    description = fit_text(
        draw,
        description,
        BODY_FONT,
        385
    )

    draw.text(
        (x + 22, y + 57),
        description,
        fill=MUTED,
        font=BODY_FONT
    )

    # ----------------------------------------------
    # LANGUAGE
    # ----------------------------------------------

    if CARDS["show_language"]:

        language = repo.get("language") or "Not specified"

        language_color = LANGUAGE_COLORS.get(
            language,
            (170, 170, 170)
        )

        draw.ellipse(
            (
                x + 22,
                y + 96,
                x + 33,
                y + 107,
            ),
            fill=language_color
        )

        draw.text(
            (x + 40, y + 94),
            language,
            fill=WHITE,
            font=SMALL_FONT
        )

    # ----------------------------------------------
    # STARS AND FORKS
    # ----------------------------------------------

    if CARDS["show_stars"] or CARDS["show_forks"]:

        stars = repo.get("stars", 0)
        forks = repo.get("forks", 0)

        metadata = []

        if CARDS["show_stars"]:
            metadata.append(f"* {stars}")

        if CARDS["show_forks"]:
            metadata.append(f"Forks: {forks}")

        draw.text(
            (x + 240, y + 94),
            "   ".join(metadata),
            fill=GOLD,
            font=SMALL_FONT
        )


# ==================================================
# COMPLETE FRAME GENERATOR
# ==================================================

def generate_frame(
    repositories,
    frame,
    runner_frames
):

    image = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        BG + (255,)
    )

    draw = ImageDraw.Draw(image)

    # Background.

    draw_background(draw)

    # Floating chakra particles.

    draw_particles(draw, frame)

    # Header.

    draw.text(
        (30, 25),
        "NINJA MISSION DATABASE",
        fill=WHITE,
        font=TITLE_FONT
    )

    draw.text(
        (32, 62),
        f"{len(repositories)} PUBLIC PROJECTS DISCOVERED",
        fill=ORANGE,
        font=SMALL_FONT
    )

    # Naruto character.

    draw_naruto(
        image,
        runner_frames,
        frame
    )

    # Repository cards.

    visible_repositories = repositories[:MAX_CARDS]

    for index, repo in enumerate(visible_repositories):

        column = index % 2
        row = index // 2

        x = 35 + column * 455
        y = 205 + row * 150

        draw_glowing_card(
            image,
            repo,
            x,
            y,
            frame,
            index
        )

    # Footer.

    draw = ImageDraw.Draw(image)

    draw.text(
        (150, 915),
        "CHAKRA SYSTEM  |  DYNAMIC REPOSITORY SHOWCASE",
        fill=MUTED,
        font=SMALL_FONT
    )

    # Rasengan.

    draw_chakra_orb(image, frame)

    return image.convert("RGB")


# ==================================================
# MAIN ANIMATION ENGINE
# ==================================================

def main():

    print("=" * 60)
    print(" NARUTO PROFILE - CHAKRA ANIMATION ENGINE v1.3")
    print("=" * 60)

    # ----------------------------------------------
    # REPOSITORY DATA
    # ----------------------------------------------

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            "Repository data not found. "
            "Run fetch_repositories.py first."
        )

    data = load_json(DATA_FILE)

    repositories = data.get("repositories", [])

    if not repositories:

        raise ValueError(
            "No repositories available for animation."
        )

    # ----------------------------------------------
    # ANIMATION SETTINGS
    # ----------------------------------------------

    if not ANIMATION["enabled"]:

        print("[INFO] Animation generation disabled.")
        return

    if not 1 <= FPS <= 30:

        raise ValueError(
            "FPS must be between 1 and 30."
        )

    if not 1 <= DURATION <= 10:

        raise ValueError(
            "Duration must be between 1 and 10 seconds."
        )

    total_frames = FPS * DURATION

    # ----------------------------------------------
    # LOAD CHARACTER
    # ----------------------------------------------

    runner_frames = load_naruto_animation()

    frames = []

    print(f"\n[INFO] Theme: {THEME_CONFIG['theme_name']}")
    print(f"[INFO] Repositories: {len(repositories)}")
    print(f"[INFO] Visible cards: {min(len(repositories), MAX_CARDS)}")
    print(f"[INFO] Animation FPS: {FPS}")
    print(f"[INFO] Duration: {DURATION} seconds")
    print(f"[INFO] Total frames: {total_frames}")
    print(f"[INFO] Canvas: {WIDTH}x{HEIGHT}")

    print(
        f"[INFO] Naruto: {'Enabled' if CHARACTER['enabled'] else 'Disabled'}"
    )

    print(
        f"[INFO] Rasengan: {'Enabled' if RASENGAN['enabled'] else 'Disabled'}"
    )

    print(
        f"[INFO] Chakra particles: {len(PARTICLES)}"
    )

    # ----------------------------------------------
    # GENERATE FRAMES
    # ----------------------------------------------

    for frame_number in range(total_frames):

        frame = generate_frame(
            repositories,
            frame_number,
            runner_frames
        )

        frames.append(frame)

        if (frame_number + 1) % FPS == 0:

            print(
                f"[INFO] Generated "
                f"{frame_number + 1}/{total_frames} frames"
            )

    # ----------------------------------------------
    # SAVE GIF
    # ----------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    frames[0].save(
        OUTPUT_FILE,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / FPS),
        loop=0 if ANIMATION["loop"] else 1,
        optimize=True,
        disposal=2
    )

    print("\n" + "=" * 60)
    print("[SUCCESS] Naruto animated showcase generated.")
    print(f"[INFO] Output: {OUTPUT_FILE}")
    print(f"[INFO] Total frames: {total_frames}")
    print("[SUCCESS] Theme configuration integration complete.")
    print("=" * 60)


# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()
