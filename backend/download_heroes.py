import requests
from pathlib import Path

# --------------------------------------------------
# Configuration
# --------------------------------------------------

OUTPUT_DIR = Path(__file__).parent / "public" / "heroes"

OPENDOTA_URL = "https://api.opendota.com/api/heroStats"

CDN_URL = (
    "https://cdn.steamstatic.com/"
    "apps/dota2/images/dota_react/heroes"
)

# --------------------------------------------------
# Create public/heroes
# --------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Get heroes
# --------------------------------------------------

print("Getting hero list from OpenDota...")

response = requests.get(OPENDOTA_URL, timeout=30)
response.raise_for_status()

heroes = response.json()

print(f"Found {len(heroes)} heroes.")
print()

# --------------------------------------------------
# Download images
# --------------------------------------------------

for index, hero in enumerate(heroes, start=1):

    # Example:
    # npc_dota_hero_antimage
    #
    # becomes:
    # antimage

    hero_name = hero["name"].replace("npc_dota_hero_", "")

    display_name = hero["localized_name"]

    url = f"{CDN_URL}/{hero_name}.png"

    output_file = OUTPUT_DIR / f"{hero_name}.png"

    print(
        f"[{index}/{len(heroes)}] "
        f"{display_name} -> {hero_name}.png"
    )

    # Don't download files that already exist
    if output_file.exists():
        print("    Already exists, skipping.")
        continue

    try:
        image = requests.get(url, timeout=30)
        image.raise_for_status()

        output_file.write_bytes(image.content)

        print("    Downloaded.")

    except requests.RequestException as error:
        print(f"    FAILED: {error}")

print()
print("================================")
print("Finished!")
print("================================")
print()
print(f"Images saved to:")
print(OUTPUT_DIR)