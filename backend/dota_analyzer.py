import requests
import pandas as pd
import time


# ============================================================
# CONFIG
# ============================================================

HERO_API_URL = "https://api.opendota.com/api/heroes"

TOP_N = 5


# ============================================================
# HERO DATA
# ============================================================

def load_heroes():

    try:
        response = requests.get(
            HERO_API_URL,
            timeout=15
        )

        response.raise_for_status()

        heroes = response.json()

        print(
            f"✓ Ladattu {len(heroes)} heroa OpenDotasta"
        )

        return pd.DataFrame(heroes)

    except Exception as e:

        print(
            f"⚠️ Hero API error: {e}"
        )

        return pd.DataFrame()


hero_df = load_heroes()

if hero_df.empty:

    print(
        "⚠️ Hero data puuttuu."
    )

    raise SystemExit


# ============================================================
# NORMALIZE
# ============================================================

def normalize(name):

    return str(name).strip().lower()


# ============================================================
# HERO NAME MAP
# ============================================================

hero_names = hero_df[
    "localized_name"
].dropna().tolist()


hero_name_map = {

    normalize(hero): hero

    for hero in hero_names
}


# ============================================================
# HERO SPECIAL TAGS
#
# Näitä käytetään counter- ja position scoringissa.
# ============================================================

HERO_SPECIAL_TAGS = {

    # ========================================================
    # CARRY / SCALING
    # ========================================================

    "Anti-Mage": {
        "mobile",
        "escape",
        "mana_burn",
        "scaling",
        "carry"
    },

    "Juggernaut": {
        "carry",
        "scaling",
        "sustain"
    },

    "Phantom Assassin": {
        "carry",
        "scaling",
        "burst",
        "escape"
    },

    "Sven": {
        "carry",
        "scaling",
        "aoe",
        "cleave",
        "stun"
    },

    "Faceless Void": {
        "carry",
        "scaling",
        "aoe",
        "stun",
        "disable",
        "teamfight"
    },

    "Phantom Lancer": {
        "carry",
        "scaling",
        "illusion"
    },

    "Terrorblade": {
        "carry",
        "scaling",
        "illusion",
        "push"
    },

    "Naga Siren": {
        "carry",
        "scaling",
        "illusion",
        "aoe",
        "control"
    },

    "Lifestealer": {
        "carry",
        "scaling",
        "sustain"
    },

    "Slark": {
        "carry",
        "scaling",
        "mobile",
        "escape",
        "dispel"
    },

    "Drow Ranger": {
        "carry",
        "scaling",
        "silence"
    },

    "Ursa": {
        "carry",
        "scaling",
        "burst"
    },

    "Monkey King": {
        "carry",
        "scaling",
        "aoe",
        "stun",
        "control"
    },


    # ========================================================
    # MID / BURST / MOBILITY
    # ========================================================

    "Invoker": {
        "burst",
        "disable",
        "control",
        "magic"
    },

    "Storm Spirit": {
        "mobile",
        "escape",
        "burst",
        "magic"
    },

    "Queen of Pain": {
        "mobile",
        "escape",
        "burst",
        "magic"
    },

    "Puck": {
        "mobile",
        "escape",
        "disable",
        "control"
    },

    "Ember Spirit": {
        "mobile",
        "escape",
        "burst",
        "magic"
    },

    "Void Spirit": {
        "mobile",
        "escape",
        "burst",
        "magic"
    },

    "Lina": {
        "aoe",
        "stun",
        "burst",
        "magic"
    },

    "Zeus": {
        "aoe",
        "burst",
        "magic"
    },

    "Tinker": {
        "aoe",
        "burst",
        "mobile",
        "magic"
    },

    "Tiny": {
        "burst",
        "stun",
        "initiation"
    },


    # ========================================================
    # OFFLANE / INITIATION
    # ========================================================

    "Axe": {
        "tank",
        "aoe",
        "initiation",
        "disable",
        "teamfight"
    },

    "Mars": {
        "tank",
        "aoe",
        "stun",
        "initiation",
        "teamfight"
    },

    "Tidehunter": {
        "tank",
        "aoe",
        "stun",
        "initiation",
        "teamfight"
    },

    "Centaur Warrunner": {
        "tank",
        "stun",
        "initiation"
    },

    "Slardar": {
        "tank",
        "stun",
        "initiation",
        "disable"
    },

    "Sand King": {
        "aoe",
        "stun",
        "initiation",
        "disable"
    },

    "Magnus": {
        "aoe",
        "stun",
        "initiation",
        "teamfight"
    },

    "Primal Beast": {
        "tank",
        "stun",
        "initiation",
        "disable"
    },

    "Underlord": {
        "tank",
        "aoe",
        "root",
        "disable",
        "push"
    },

    "Bristleback": {
        "tank",
        "sustain"
    },

    "Legion Commander": {
        "tank",
        "dispel",
        "disable",
        "duel"
    },


    # ========================================================
    # SUPPORT / DISABLE
    # ========================================================

    "Earthshaker": {
        "aoe",
        "stun",
        "initiation",
        "disable",
        "teamfight"
    },

    "Lion": {
        "stun",
        "disable",
        "burst"
    },

    "Shadow Shaman": {
        "stun",
        "disable",
        "push"
    },

    "Rubick": {
        "stun",
        "disable",
        "control"
    },

    "Vengeful Spirit": {
        "stun",
        "disable",
        "initiation"
    },

    "Nyx Assassin": {
        "stun",
        "disable",
        "burst"
    },

    "Witch Doctor": {
        "stun",
        "disable"
    },

    "Bane": {
        "disable",
        "control"
    },

    "Crystal Maiden": {
        "root",
        "disable",
        "control"
    },

    "Dark Willow": {
        "root",
        "stun",
        "disable",
        "burst"
    },

    "Jakiro": {
        "aoe",
        "stun",
        "disable"
    },

    "Disruptor": {
        "silence",
        "aoe",
        "disable"
    },

    "Grimstroke": {
        "silence",
        "disable"
    },


    # ========================================================
    # HEAL / SAVE / DISPEL
    # ========================================================

    "Dazzle": {
        "heal",
        "save",
        "support"
    },

    "Oracle": {
        "heal",
        "save",
        "dispel",
        "support"
    },

    "Omniknight": {
        "heal",
        "save",
        "dispel",
        "support"
    },

    "Io": {
        "heal",
        "save",
        "support"
    },

    "Warlock": {
        "heal",
        "teamfight",
        "support"
    },

    "Abaddon": {
        "heal",
        "save",
        "dispel",
        "support"
    },

    "Winter Wyvern": {
        "heal",
        "save",
        "support",
        "teamfight"
    },

    "Phoenix": {
        "aoe",
        "heal",
        "teamfight"
    },

    "Treant Protector": {
        "root",
        "heal",
        "support"
    },


    # ========================================================
    # SILENCE
    # ========================================================

    "Silencer": {
        "silence",
        "aoe",
        "disable"
    },

    "Death Prophet": {
        "silence",
        "aoe",
        "push"
    },

    "Skywrath Mage": {
        "silence",
        "burst"
    },

    "Night Stalker": {
        "silence",
        "initiation"
    },

    "Riki": {
        "silence",
        "mobile",
        "escape"
    },


    # ========================================================
    # ILLUSIONS
    # ========================================================

    "Chaos Knight": {
        "illusion",
        "burst",
        "carry"
    },

    "Spectre": {
        "illusion",
        "scaling",
        "carry"
    },

    "Shadow Demon": {
        "illusion",
        "dispel",
        "disable"
    }
}


# ============================================================
# POSITION OVERRIDES
#
# Määrittää ensisijaiset Dota-positiot.
#
# 1 = Carry
# 2 = Mid
# 3 = Offlane
# 4 = Soft Support
# 5 = Hard Support
# ============================================================

POSITION_OVERRIDES = {

    "Anti-Mage": [1],
    "Juggernaut": [1],
    "Phantom Assassin": [1],
    "Sven": [1],
    "Faceless Void": [1],
    "Phantom Lancer": [1],
    "Terrorblade": [1],
    "Naga Siren": [1],
    "Lifestealer": [1],
    "Ursa": [1],
    "Drow Ranger": [1],

    "Invoker": [2],
    "Storm Spirit": [2],
    "Queen of Pain": [2],
    "Puck": [2],
    "Ember Spirit": [2],
    "Void Spirit": [2],
    "Zeus": [2],
    "Tinker": [2],

    "Axe": [3],
    "Mars": [3],
    "Tidehunter": [3],
    "Centaur Warrunner": [3],
    "Slardar": [3],
    "Sand King": [3],
    "Magnus": [3],
    "Primal Beast": [3],
    "Underlord": [3],
    "Bristleback": [3],
    "Legion Commander": [3],

    "Earthshaker": [3, 4],
    "Rubick": [4, 5],
    "Lion": [4, 5],
    "Nyx Assassin": [4],
    "Vengeful Spirit": [4, 5],
    "Dark Willow": [4, 5],
    "Grimstroke": [4, 5],
    "Skywrath Mage": [4, 5],
    "Disruptor": [4, 5],
    "Witch Doctor": [4, 5],
    "Bane": [4, 5],

    "Crystal Maiden": [5],
    "Dazzle": [5],
    "Oracle": [5],
    "Omniknight": [5],
    "Io": [5],
    "Warlock": [5],
    "Abaddon": [5],
    "Winter Wyvern": [5],
    "Treant Protector": [5],
    "Silencer": [5],
    "Shadow Shaman": [4, 5],
    "Jakiro": [4, 5]
}


# ============================================================
# GENERATE HERO PROFILES
# ============================================================

def generate_hero_profiles(hero_df):

    profiles = {}

    for _, row in hero_df.iterrows():

        hero = row["localized_name"]

        roles = row.get(
            "roles",
            []
        )

        if not isinstance(roles, list):

            roles = []

        attack_type = row.get(
            "attack_type",
            ""
        )

        primary_attr = row.get(
            "primary_attr",
            ""
        )

        tags = set()

        # ----------------------------------------------------
        # ATTACK TYPE
        # ----------------------------------------------------

        if attack_type == "Melee":

            tags.add("melee")

        elif attack_type == "Ranged":

            tags.add("ranged")

        # ----------------------------------------------------
        # PRIMARY ATTRIBUTE
        # ----------------------------------------------------

        if primary_attr == "str":

            tags.add("tank")

        elif primary_attr == "agi":

            tags.update({
                "physical",
                "scaling"
            })

        elif primary_attr == "int":

            tags.update({
                "magic",
                "burst"
            })

        # ----------------------------------------------------
        # OPENDOTA ROLES
        # ----------------------------------------------------

        if "Carry" in roles:

            tags.update({
                "carry",
                "scaling"
            })

        if "Support" in roles:

            tags.add(
                "support"
            )

        if "Initiator" in roles:

            tags.add(
                "initiation"
            )

        if "Disabler" in roles:

            tags.update({
                "disable",
                "control"
            })

        if "Nuker" in roles:

            tags.add(
                "burst"
            )

        if "Durable" in roles:

            tags.add(
                "tank"
            )

        if "Escape" in roles:

            tags.update({
                "mobile",
                "escape"
            })

        if "Pusher" in roles:

            tags.add(
                "push"
            )

        # ----------------------------------------------------
        # SPECIAL TAGS
        # ----------------------------------------------------

        tags.update(

            HERO_SPECIAL_TAGS.get(
                hero,
                set()
            )
        )

        profiles[normalize(hero)] = {

            "name": hero,

            "tags": tags,

            "opendota_roles": roles
        }

    return profiles


hero_profile = generate_hero_profiles(
    hero_df
)


# ============================================================
# HERO SEARCH
#
# Hakee heroja kirjoitettujen kirjainten perusteella.
# ============================================================

def suggest_hero_input(
    hero_df,
    typed
):

    typed = normalize(
        typed
    )

    if not typed:

        return []

    suggestions = []

    for hero in hero_df[
        "localized_name"
    ]:

        hero_lower = normalize(
            hero
        )

        # Paras osuma:
        # nimi alkaa kirjoitetulla tekstillä

        if hero_lower.startswith(
            typed
        ):

            priority = 0

        # Teksti löytyy nimen sisältä

        elif typed in hero_lower:

            priority = 1

        # Kirjaimet löytyvät järjestyksessä

        else:

            position = 0
            found = True

            for char in typed:

                position = hero_lower.find(
                    char,
                    position
                )

                if position == -1:

                    found = False

                    break

                position += 1

            if found:

                priority = 2

            else:

                continue

        suggestions.append(
            (
                priority,
                len(hero),
                hero
            )
        )

    suggestions.sort()

    return [

        hero

        for _, _, hero in suggestions
    ]


# ============================================================
# TEAM INPUT
# ============================================================
def get_team_interactive(hero_df, team_name, max_heroes):

    team = []

    print(f"\n===== {team_name.upper()} =====")
    print("Kirjoita heron nimi tai osa nimestä.")
    print("Esim. 'phant' tai 'jug'.")
    print("Kirjoita 'next' kun haluat lopettaa tämän tiimin pickien syötön.")

    for i in range(max_heroes):

        while True:

            typed = input(
                f"\n{team_name} hero {i + 1}/{max_heroes}: "
            ).strip()

            # NEXT = lopeta tiimin syöttäminen
            if typed.lower() == "next":
                return team

            # Tyhjä Enter ei lopeta
            if not typed:
                print("❌ Kirjoita heron nimi tai 'next'.")
                continue

            key = normalize(typed)

            # Tarkka heron nimi
            if key in hero_name_map:

                hero = hero_name_map[key]

                if hero in team:
                    print("⚠️ Hero on jo valittu.")
                    continue

                team.append(hero)

                print(f"✓ Valittu: {hero}")

                break

            # Ehdotukset
            matches = suggest_hero_input(hero_df, typed)

            if not matches:
                print("❌ Heroa ei löytynyt. Kokeile uudestaan.")
                continue

            print("\nEhdotukset:")

            for index, hero in enumerate(matches[:10], start=1):
                print(f"{index}. {hero}")

                choice = input(
                 "\nValitse numero tai kirjoita 'next': "
                ).strip()

                if choice.lower() == "next":
                         return team

# Tyhjä Enter ei tee mitään.
# Palataan takaisin kysymään valintaa.
                if not choice:
                     continue


            # Valitaan ehdotus numerolla
            if choice.isdigit():

                index = int(choice) - 1

                if 0 <= index < len(matches[:10]):

                    hero = matches[index]

                    if hero in team:
                        print("⚠️ Hero on jo valittu.")
                        continue

                    team.append(hero)

                    print(f"✓ Valittu: {hero}")

                    break

                else:
                    print("❌ Virheellinen numero.")

            else:
                print("❌ Valitse numero tai kirjoita 'next'.")

    # TÄMÄ ON TÄRKEÄ!
    # Kun kaikki 5/5 heroa on syötetty,
    # palautetaan team eikä tyhjää listaa.

    return team

# ============================================================
# GET HERO ID
# ============================================================

def get_hero_id(name):

    key = normalize(
        name
    )

    hero = hero_name_map.get(
        key
    )

    if hero is None:

        raise ValueError(
            f"Heroa '{name}' ei löydy."
        )

    row = hero_df[

        hero_df["localized_name"]

        == hero

    ]

    return int(
        row.iloc[0]["id"]
    )


# ============================================================
# MATCHUP CACHE
#
# Hakee API:sta vain vihollisen matchupit.
# ============================================================

def build_enemy_matchup_cache(
    enemy_team
):

    matchup_cache = {}

    print(
        "\n===== HAETAAN MATCHUP-DATA ====="
    )

    for index, enemy in enumerate(

        enemy_team,

        start=1

    ):

        try:

            enemy_id = get_hero_id(
                enemy
            )

            print(

                f"[{index}/{len(enemy_team)}] "

                f"Haetaan {enemy}"

            )

            response = requests.get(

                f"https://api.opendota.com/api/heroes/"
                f"{enemy_id}/matchups",

                timeout=15

            )

            response.raise_for_status()

            data = response.json()

            enemy_matchups = {}

            for matchup in data:

                candidate_id = matchup.get(
                    "hero_id"
                )

                if candidate_id is None:

                    continue

                enemy_matchups[
                    int(candidate_id)
                ] = {

                    "wins": matchup.get(
                        "wins",
                        0
                    ),

                    "games": matchup.get(
                        "games_played",
                        0
                    )
                }

            matchup_cache[
                enemy_id
            ] = enemy_matchups

            time.sleep(
                0.2
            )

        except Exception as e:

            print(

                f"⚠️ Matchup error "

                f"({enemy}): {e}"

            )

    return matchup_cache


# ============================================================
# MATCHUP SCORE
#
# Ei tee API-kutsuja.
# ============================================================

def matchup_score(
    hero,
    enemy_team,
    matchup_cache
):

    hero_id = get_hero_id(
        hero
    )

    winrates = []

    for enemy in enemy_team:

        enemy_id = get_hero_id(
            enemy
        )

        enemy_data = matchup_cache.get(

            enemy_id,

            {}

        )

        matchup = enemy_data.get(
            hero_id
        )

        if not matchup:

            continue

        wins = matchup[
            "wins"
        ]

        games = matchup[
            "games"
        ]

        if games > 0:

            winrates.append(
                wins / games
            )

    if not winrates:

        return 0.0

    average = sum(
        winrates
    ) / len(
        winrates
    )

    return (
        average - 0.5
    ) * 2


# ============================================================
# COUNTER SCORE
# ============================================================

def counter_score(
    hero,
    enemy_team
):

    hero_tags = hero_profile.get(

        normalize(hero),

        {}

    ).get(

        "tags",

        set()

    )

    score = 0.0

    for enemy in enemy_team:

        enemy_tags = hero_profile.get(

            normalize(enemy),

            {}

        ).get(

            "tags",

            set()

        )

        # Illusion counter

        if "illusion" in enemy_tags:

            if "aoe" in hero_tags:

                score += 1.0

            if "cleave" in hero_tags:

                score += 0.8

        # Mobile counter

        if "mobile" in enemy_tags:

            if "stun" in hero_tags:

                score += 0.7

            if "root" in hero_tags:

                score += 0.7

            if "disable" in hero_tags:

                score += 0.4

        # Escape counter

        if "escape" in enemy_tags:

            if "silence" in hero_tags:

                score += 0.7

        # Melee counter

        if "melee" in enemy_tags:

            if "aoe" in hero_tags:

                score += 0.3

        # Magic damage counter

        if "magic" in enemy_tags:

            if "heal" in hero_tags:

                score += 0.3

            if "save" in hero_tags:

                score += 0.5

        # Disable counter

        if "disable" in enemy_tags:

            if "dispel" in hero_tags:

                score += 0.4

    return score


# ============================================================
# TEAM SYNERGY SCORE
# ============================================================

def team_synergy_score(
    hero,
    own_team
):

    if not own_team:

        return 0.0

    hero_tags = hero_profile.get(

        normalize(hero),

        {}

    ).get(

        "tags",

        set()

    )

    own_tags = set()

    for teammate in own_team:

        own_tags.update(

            hero_profile.get(

                normalize(teammate),

                {}

            ).get(

                "tags",

                set()

            )

        )

    score = 0.0

    missing_tags = {

        "disable": 0.5,

        "stun": 0.5,

        "initiation": 0.5,

        "aoe": 0.3,

        "heal": 0.4,

        "save": 0.4,

        "silence": 0.3
    }

    for tag, value in missing_tags.items():

        if (

            tag not in own_tags

            and tag in hero_tags

        ):

            score += value

    return score


# ============================================================
# POSITION SCORE
#
# Jokaisella positiolla on oma painotus.
# ============================================================

def position_score(
    hero,
    position,
    enemy_team,
    own_team,
    matchup_cache
):

    hero_tags = hero_profile.get(

        normalize(hero),

        {}

    ).get(

        "tags",

        set()

    )

    matchup = matchup_score(

        hero,

        enemy_team,

        matchup_cache

    )

    counter = counter_score(

        hero,

        enemy_team

    )

    synergy = team_synergy_score(

        hero,

        own_team

    )

    role_score = 0.0

    # ========================================================
    # POS 1 - CARRY
    # ========================================================

    if position == 1:

        if "carry" in hero_tags:

            role_score += 1.5

        if "scaling" in hero_tags:

            role_score += 1.2

        if "physical" in hero_tags:

            role_score += 0.4

        if "sustain" in hero_tags:

            role_score += 0.4

        final = (

            matchup * 3.0

            + counter * 1.0

            + role_score * 1.5

            + synergy * 0.5

        )

    # ========================================================
    # POS 2 - MID
    # ========================================================

    elif position == 2:

        if "burst" in hero_tags:

            role_score += 1.0

        if "mobile" in hero_tags:

            role_score += 1.0

        if "magic" in hero_tags:

            role_score += 0.7

        if "disable" in hero_tags:

            role_score += 0.5

        final = (

            matchup * 3.0

            + counter * 1.0

            + role_score * 1.5

            + synergy * 0.5

        )

    # ========================================================
    # POS 3 - OFFLANE
    # ========================================================

    elif position == 3:

        if "tank" in hero_tags:

            role_score += 1.0

        if "initiation" in hero_tags:

            role_score += 1.2

        if "teamfight" in hero_tags:

            role_score += 0.8

        if "disable" in hero_tags:

            role_score += 0.5

        final = (

            matchup * 2.5

            + counter * 1.0

            + role_score * 1.7

            + synergy * 1.0

        )

    # ========================================================
    # POS 4 - SOFT SUPPORT
    # ========================================================

    elif position == 4:

        if "disable" in hero_tags:

            role_score += 1.2

        if "stun" in hero_tags:

            role_score += 0.8

        if "initiation" in hero_tags:

            role_score += 0.7

        if "mobile" in hero_tags:

            role_score += 0.5

        if "support" in hero_tags:

            role_score += 0.5

        final = (

            matchup * 2.5

            + counter * 1.2

            + role_score * 1.5

            + synergy * 1.0

        )

    # ========================================================
    # POS 5 - HARD SUPPORT
    # ========================================================

    elif position == 5:

        if "support" in hero_tags:

            role_score += 1.0

        if "heal" in hero_tags:

            role_score += 0.8

        if "save" in hero_tags:

            role_score += 1.0

        if "disable" in hero_tags:

            role_score += 0.8

        if "dispel" in hero_tags:

            role_score += 0.5

        final = (

            matchup * 2.5

            + counter * 1.0

            + role_score * 1.7

            + synergy * 1.2

        )

    else:

        final = 0.0

    return {

        "total": round(
            final,
            3
        ),

        "matchup": round(
            matchup,
            3
        ),

        "counter": round(
            counter,
            3
        ),

        "role": round(
            role_score,
            3
        ),

        "synergy": round(
            synergy,
            3
        )
    }


# ============================================================
# GET HERO POSITIONS
# ============================================================

def get_hero_positions(hero):

    # Ensisijaisesti override

    if hero in POSITION_OVERRIDES:

        return POSITION_OVERRIDES[
            hero
        ]

    profile = hero_profile.get(

        normalize(hero),

        {}

    )

    tags = profile.get(

        "tags",

        set()

    )

    positions = []

    # Pos 1

    if (

        "carry" in tags

        and "scaling" in tags

    ):

        positions.append(
            1
        )

    # Pos 2

    if (

        "burst" in tags

        and (
            "mobile" in tags
            or "magic" in tags
        )

    ):

        positions.append(
            2
        )

    # Pos 3

    if (

        "tank" in tags

        and (
            "initiation" in tags
            or "disable" in tags
        )

    ):

        positions.append(
            3
        )

    # Pos 4

    if (

        "support" in tags

        and "disable" in tags

    ):

        positions.append(
            4
        )

    # Pos 5

    if (

        "support" in tags

        and (
            "heal" in tags
            or "save" in tags
            or "disable" in tags
        )

    ):

        positions.append(
            5
        )

    return positions


# ============================================================
# TOP PICKS PER POSITION
# ============================================================

def get_top_picks_for_position(
    position,
    enemy_team,
    own_team,
    matchup_cache,
    top_n=5
):

    used_heroes = {

        normalize(hero)

        for hero in (

            enemy_team

            + own_team

        )
    }

    results = []

    for hero in hero_df[
        "localized_name"
    ]:

        if normalize(hero) in used_heroes:

            continue

        positions = get_hero_positions(
            hero
        )

        # Hero ei kuulu tähän positioon

        if position not in positions:

            continue

        score_data = position_score(

            hero,

            position,

            enemy_team,

            own_team,

            matchup_cache

        )

        results.append(

            (

                hero,

                score_data

            )

        )

    results.sort(

        key=lambda x:

            x[1]["total"],

        reverse=True

    )

    return results[
        :top_n
    ]


# ============================================================
# GENERAL TOP COUNTERS
# ============================================================

def get_general_top_picks(
    enemy_team,
    own_team,
    matchup_cache,
    top_n=5
):

    used_heroes = {

        normalize(hero)

        for hero in (

            enemy_team

            + own_team

        )
    }

    results = []

    for hero in hero_df[
        "localized_name"
    ]:

        if normalize(hero) in used_heroes:

            continue

        positions = get_hero_positions(
            hero
        )

        if not positions:

            continue

        best_score = None
        best_position = None

        for position in positions:

            score_data = position_score(

                hero,

                position,

                enemy_team,

                own_team,

                matchup_cache

            )

            if (

                best_score is None

                or score_data["total"]

                > best_score["total"]

            ):

                best_score = score_data

                best_position = position

        results.append(

            (

                hero,

                best_position,

                best_score

            )

        )

    results.sort(

        key=lambda x:

            x[2]["total"],

        reverse=True

    )

    return results[
        :top_n
    ]


# ============================================================
# SHOW SCORE EXPLANATION
# ============================================================

def show_score_explanation(
    hero,
    score_data
):

    profile = hero_profile.get(

        normalize(hero),

        {}

    )

    tags = sorted(

        profile.get(

            "tags",

            set()

        )

    )

    print(
        f"\n{hero}"
    )

    print(
        f"Total score: "
        f"{score_data['total']}"
    )

    print(
        f"  Matchup: "
        f"{score_data['matchup']}"
    )

    print(
        f"  Counter: "
        f"{score_data['counter']}"
    )

    print(
        f"  Position: "
        f"{score_data['role']}"
    )

    print(
        f"  Synergy: "
        f"{score_data['synergy']}"
    )

    print(
        "  Tags: "
        + ", ".join(tags)
    )


# ============================================================
# MAIN FOR CONSOLE
# ============================================================

#if __name__ == "__main__":
#
#    print(
#        "\n===================================="
#    )
#
#    print(
#        "DOTA 2 POSITION DRAFT ASSISTANT"
#    )
#
#    print(
#        "===================================="
#    )
#
#
#    # ========================================================
#    # VIHOLLISEN PICKIT
#    # ========================================================
#
    enemy_team = get_team_interactive(

        hero_df,

       "Vihollinen",

        max_heroes=5

    )
#
#    if not enemy_team:
#
#        print(
#            "Et syöttänyt vihollisheroja."
#        )
#
#        raise SystemExit
#
#
#    # ========================================================
#    # OMAN TIIMIN PICKIT
#    # ========================================================
#
#    own_team = get_team_interactive(
#
#        hero_df,
#
#        "Oma tiimi",
#
#        max_heroes=4
#
#    )
#
#
#    # ========================================================
#    # NÄYTÄ VALINNAT
#    # ========================================================
#
#    print(
#        "\nVIHOLLISTEN HEROT:"
#    )
#
#    for hero in enemy_team:
#
#        print(
#            f"- {hero}"
#        )
#
#    print(
#        "\nOMAN TIIMIN HEROT:"
#    )
#
#    if own_team:
#
#        for hero in own_team:
#
#            print(
#                f"- {hero}"
#            )
#
#    else:
#
#        print(
#            "- Ei vielä pickejä"
#        )
#
#
#    # ========================================================
#    # HAE MATCHUP DATA VAIN KERRAN
#    # ========================================================
#
    matchup_cache = build_enemy_matchup_cache(

        enemy_team

   )
#
#
#    # ========================================================
#    # YLEINEN TOP 5
#    # ========================================================
#
#    print(
#        "\n===================================="
#    )
#
#    print(
#        "YLEINEN TOP 5 COUNTER-PICK"
#    )
#
#    print(
#        "===================================="
#    )
#
#    general_picks = get_general_top_picks(
#
#        enemy_team,
#
#        own_team,
#
#        matchup_cache,
#
#        top_n=TOP_N
#
#    )
#
#    position_names = {
#
#        1: "Pos 1 Carry",
#
#        2: "Pos 2 Mid",
#
#        3: "Pos 3 Offlane",
#
#        4: "Pos 4 Soft Support",
#
#        5: "Pos 5 Hard Support"
#    }
#
#    for index, (
#
#        hero,
#
#        position,
#
#        score_data
#
#    ) in enumerate(
#
#        general_picks,
#
#        start=1
#
#    ):
#
#        print(
#            f"\n#{index} {hero}"
#        )
#
#        print(
#            f"Suositeltu rooli: "
#            f"{position_names[position]}"
#        )
#
#        show_score_explanation(
#
#            hero,
#
#            score_data
#
#        )
#
#
#    # ========================================================
#    # TOP 5 PER POSITION
#    # ========================================================
#
#    for position in range(
#        1,
#        6
#    ):
#
#        print(
#            "\n===================================="
#        )
#
#        print(
#            f"TOP {TOP_N} - "
#            f"{position_names[position]}"
#        )
#
#        print(
#            "===================================="
#        )
#
#        picks = get_top_picks_for_position(
#
#            position,
#
#            enemy_team,
#
#            own_team,
#
#            matchup_cache,
#
#            top_n=TOP_N
#
#        )
#
#        if not picks:
#
#            print(
#                "Ei tarpeeksi dataa."
#            )
#
#            continue
#
#        for index, (
#
#            hero,
#
#            score_data
#
#        ) in enumerate(
#
#            picks,
#
#            start=1
#
#        ):
#
#            print(
#                f"\n#{index}"
#            )
#
#            show_score_explanation(
#
#                hero,
#
#                score_data
#
#            )
#
#
#    print(
#        "\n===================================="
#    )
#
#    print(
#        "ANALYYSI VALMIS"
#    )
#
#    print(
#        "===================================="
#    )
#