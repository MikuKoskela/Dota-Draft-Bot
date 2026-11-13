"""Build complete, reproducible hero maps for the draft engine.

Sources:
- dotaconstants snapshot (heroes, abilities, hero_abilities, aghs_desc)
- the v0.6 curated role/composition/item baseline
- static weighted rules imported from Dota_Draft_Assistant_v0.9.py

The output intentionally separates source facts (stats, abilities, facets,
talents, Aghanim upgrades) from heuristic weights. Heuristic values are never
presented as measured win-rate data.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app/data"
SOURCES = DATA / "sources"

DOTACONSTANTS_COMMIT = "e7705ee975ebec2a88a59a7b455d4cae5dc69ca1"
DOTACONSTANTS_DATE = "2026-07-28T23:06:33Z"

# Keep the application's established public names so matchup/synergy keys and
# saved draft requests remain backwards compatible with v0.6.
PUBLIC_NAME_ALIASES = {
    "Outworld Devourer": "Outworld Destroyer",
    "Ring Master": "Ringmaster",
}

TAG_ALIASES = {
    "physical": "physical_damage",
    "magic": "magic_damage",
    "mobile": "mobility",
    "escape": "mobility",
    "disable": "hard_disable",
    "control": "hard_disable",
    "tank": "frontline",
    "late_game": "late_game_scaling",
    "anti_heal": "anti_regeneration",
    "mana_burn": "mana_burn",
    "aoe": "aoe_damage",
    "kite": "kiting",
}

WEAKNESS_ALIASES = {
    "weak_to_aoe": "aoe_control",
    "weak_to_silence": "silence",
    "weak_to_burst": "burst",
    "weak_to_gap_close": "gap_close",
    "needs_frontline": "needs_frontline",
    "cooldown_dependent": "cooldown_dependency",
    "needs_space": "farm_dependency",
    "weak_to_disable": "hard_disable",
    "weak_to_kiting": "kiting",
    "mana_dependent": "mana_pressure",
    "weak_to_magic": "magic_damage",
    "weak_to_physical": "physical_burst",
    "weak_to_break": "break",
    "needs_peel": "needs_peel",
    "squishy": "low_survivability",
    "weak_early": "early_pressure",
    "disable": "hard_disable",
    "kite": "kiting",
    "magic": "magic_damage",
    "physical": "physical_burst",
    "aoe": "aoe_control",
    "cleave": "aoe_control",
    "wave_clear": "aoe_control",
    "catch": "gap_close",
    "root": "root",
    "stun": "hard_disable",
}

ROLE_TAG_WEIGHTS = {
    # Generic roles are broad labels, so they are supporting evidence rather
    # than full-strength mechanics. Curated and ability-derived tags override.
    "Carry": {"carry": 0.65, "late_game_scaling": 0.55, "farm_acceleration": 0.35},
    "Support": {"support": 0.65, "utility": 0.55},
    "Initiator": {"initiation": 0.60, "catch": 0.48, "teamfight": 0.45},
    "Disabler": {"hard_disable": 0.45, "catch": 0.42},
    "Nuker": {"burst": 0.58, "magic_damage": 0.52},
    "Durable": {"frontline": 0.60, "sustain": 0.38},
    "Escape": {"mobility": 0.62, "gap_close": 0.40},
    "Pusher": {"push": 0.60, "wave_clear": 0.40, "tower_pressure": 0.50},
    "Jungler": {"farm_acceleration": 0.50, "summon": 0.28},
}

ABILITY_TAG_RULES = {
    "stun": (0.90, (r"\bstun(?:s|ned|ning)?\b", r"\bbash(?:es|ed)?\b")),
    "root": (0.88, (r"\broot(?:s|ed)?\b", r"\bensnare(?:s|d)?\b")),
    "silence": (0.88, (r"\bsilence(?:s|d)?\b",)),
    "slow": (0.68, (r"\bslow(?:s|ed|ing)?\b", r"movement speed by -")),
    "disarm": (0.82, (r"\bdisarm(?:s|ed)?\b", r"cannot attack")),
    "fear": (0.86, (r"\bfear(?:s|ed)?\b", r"flee toward")),
    "taunt": (0.90, (r"\btaunt(?:s|ed)?\b", r"forced to attack")),
    "hex": (0.95, (r"\bhex(?:es|ed)?\b", r"turned into a harmless")),
    "leash": (0.86, (r"\bleash(?:es|ed)?\b",)),
    "break": (0.90, (
        r"(?:appl(?:y|ies|ied|ying)|inflicts?) (?:the )?break\b",
        r"(?:deals?|dealing|causes?|causing).{0,80}\bbreak\b",
        r"passives? (?:are|is) disabled",
    )),
    "mute": (0.86, (r"\bmute(?:s|d)?\b", r"cannot use items")),
    "knockback": (0.68, (r"knock(?:s|ed)? back", r"knockback")),
    "reposition": (0.66, (r"\bpull(?:s|ed|ing)?\b", r"drags? .* toward", r"swap positions")),
    "dispel": (0.86, (r"\bdispel(?:s|led)?\b", r"\bpurge(?:s|d)?\b")),
    "heal": (0.82, (r"\bheal(?:s|ed|ing)?\b", r"restores? .*health", r"health regeneration")),
    "save": (0.82, (r"prevents? .*death", r"cannot die", r"becomes? invulnerable", r"damage .* redirected")),
    "mobility": (0.82, (r"\bblink(?:s|ed)?\b", r"\bteleport(?:s|ed)?\b", r"\bleap(?:s|ed)?\b", r"\bdash(?:es|ed)?\b", r"charges? toward")),
    "invisibility": (0.88, (r"\binvisib(?:le|ility)\b",)),
    "evasion": (0.86, (r"\bevasion\b", r"chance to evade")),
    "spell_reflect": (0.90, (r"reflects? .*spell", r"spell reflection")),
    "spell_block": (0.86, (r"blocks? .*spell", r"spell block")),
    "magic_immunity": (0.90, (r"magic immun", r"debuff immun")),
    "damage_reduction": (0.72, (r"damage reduction", r"reduces? .*incoming damage")),
    "armor_reduction": (0.82, (r"reduces? .*armor", r"armor reduction", r"negative armor")),
    "anti_regeneration": (0.92, (r"reduces? .*heal", r"healing reduction", r"cannot regenerate", r"prevents? .*regenerat")),
    "mana_burn": (0.88, (r"burns? .*mana", r"mana burn", r"removes? .*mana")),
    "reveal": (0.84, (r"true sight", r"reveals? invis", r"visible .* invis")),
    "illusion": (0.88, (r"creates? .*illusion", r"summons? .*illusion", r"illusions? of")),
    "summon": (0.78, (r"\bsummon(?:s|ed)?\b", r"creates? .*unit", r"spawns? .*unit")),
    "global": (0.78, (r"\bglobal\b", r"anywhere on the map")),
    "damage_over_time": (0.72, (r"damage per second", r"damage over time", r"every .* seconds?")),
    "aoe_damage": (0.62, (r"all enemies .* radius", r"enemies in .* area", r"area of effect")),
    "channeling": (0.84, (r"\bchannel(?:s|ed|ing)?\b",)),
    "attack_speed": (0.62, (r"attack speed",)),
    "movement_speed": (0.58, (r"movement speed",)),
    "vision": (0.66, (r"vision", r"sight range")),
    "critical_strike": (0.78, (r"critical strike", r"critical damage", r"critical hit")),
    "lifesteal": (0.78, (r"lifesteal", r"life steal")),
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, float(value)))


def merge_weight(target, key, value):
    if not key:
        return
    target[key] = round(max(float(target.get(key, 0.0)), clamp(value)), 3)


def normalize_tag(tag):
    return TAG_ALIASES.get(tag, tag)


def normalize_weakness(tag):
    return WEAKNESS_ALIASES.get(tag, tag)


def percentile(values, value):
    ordered = sorted(values)
    if len(ordered) <= 1:
        return 0.5
    below = sum(item < value for item in ordered)
    equal = sum(item == value for item in ordered)
    return clamp((below + max(0, equal - 1) / 2) / (len(ordered) - 1))


def primary_damage(hero):
    attack = (float(hero.get("base_attack_min", 0)) + float(hero.get("base_attack_max", 0))) / 2
    attrs = {
        "str": float(hero.get("base_str", 0)),
        "agi": float(hero.get("base_agi", 0)),
        "int": float(hero.get("base_int", 0)),
    }
    primary = hero.get("primary_attr")
    if primary == "all":
        return attack + sum(attrs.values()) * 0.7
    return attack + attrs.get(primary, max(attrs.values(), default=0))


def durability(hero):
    return float(hero.get("base_health", 0)) + float(hero.get("base_str", 0)) * 22


def armor(hero):
    return float(hero.get("base_armor", 0)) + float(hero.get("base_agi", 0)) / 6


def legacy_role_maps(rules):
    maps = []
    for name in ("ROLE_WEIGHTS_V07", "POSITION_FITNESS"):
        maps.append(rules.get(name, {}))
    return maps


def role_profile(name, base, generic_roles, rules):
    roles = {f"pos{position}": 0.0 for position in range(1, 6)}
    for role, value in base.get("roles", {}).items():
        if value >= 0.35:
            roles[role] = float(value)

    hints = {
        "Carry": {"pos1": 0.72, "pos2": 0.35},
        "Support": {"pos4": 0.68, "pos5": 0.72},
        "Initiator": {"pos3": 0.65, "pos4": 0.45},
        "Disabler": {"pos4": 0.55, "pos5": 0.50},
        "Nuker": {"pos2": 0.52, "pos4": 0.40},
        "Durable": {"pos3": 0.62},
        "Escape": {"pos2": 0.42},
        "Pusher": {"pos2": 0.38, "pos3": 0.42},
    }
    # OpenDota's generic labels describe play style, not farm positions. Only
    # use them as a fallback for a hero with no curated positional signal;
    # otherwise e.g. a scaling support labelled "Carry" becomes a false pos1.
    if max(roles.values(), default=0.0) < 0.45:
        for generic in generic_roles:
            for role, value in hints.get(generic, {}).items():
                roles[role] = max(roles[role], value)

    position_overrides = rules.get("POSITION_OVERRIDES", {}).get(name, [])
    defaults = {1: 0.90, 2: 0.88, 3: 0.88, 4: 0.84, 5: 0.86}
    for position in position_overrides:
        roles[f"pos{position}"] = max(roles[f"pos{position}"], defaults[position])

    for mapping in legacy_role_maps(rules):
        for position, value in mapping.get(name, {}).items():
            roles[f"pos{position}"] = max(roles[f"pos{position}"], float(value))
    return {key: round(clamp(value), 3) for key, value in roles.items()}


def ability_text(record):
    # Attribute labels often mention unrelated upgrade parameters (for example
    # an illusion value on a spell that does not create illusions). Descriptions
    # and names are much cleaner evidence for semantic mechanics.
    return " ".join(
        str(record.get(key, "")) for key in ("dname", "behavior", "dmg_type", "desc")
    ).lower()


def infer_ability_tags(record):
    text = ability_text(record)
    tags = {}
    damage_type = str(record.get("dmg_type", "")).lower()
    if damage_type == "magical":
        merge_weight(tags, "magic_damage", 0.74)
    elif damage_type == "physical":
        merge_weight(tags, "physical_damage", 0.72)
    elif damage_type == "pure":
        merge_weight(tags, "pure_damage", 0.82)
    behavior = str(record.get("behavior", "")).lower()
    if "passive" in behavior:
        merge_weight(tags, "passive", 0.72)
    if "channeled" in behavior or "channel" in behavior:
        merge_weight(tags, "channeling", 0.86)
    for tag, (weight, patterns) in ABILITY_TAG_RULES.items():
        if any(re.search(pattern, text) for pattern in patterns):
            inferred_weight = 0.30 if tag == "stun" and re.search(r"mini[- ]?stun", text) else weight
            merge_weight(tags, tag, inferred_weight)
    return tags


def ability_records(hero_name, hero_abilities, abilities):
    result = []
    mechanics = {}
    raw_abilities = hero_abilities.get(hero_name, {}).get("abilities", [])
    ability_names = []
    for entry in raw_abilities:
        # Some heroes expose mutually exclusive facet abilities as a nested
        # array. Preserve both variants in the comprehensive profile.
        ability_names.extend(entry if isinstance(entry, list) else [entry])
    for ability_name in ability_names:
        if ability_name == "generic_hidden" or ability_name.startswith("special_bonus"):
            continue
        source = abilities.get(ability_name, {})
        if not source:
            continue
        tags = infer_ability_tags(source)
        behavior = source.get("behavior")
        behaviors = behavior if isinstance(behavior, list) else [behavior]
        is_hidden = any(str(item).lower() == "hidden" for item in behaviors)
        availability_weight = 0.55 if is_hidden else 1.0
        for tag, value in tags.items():
            merge_weight(mechanics, tag, value * availability_weight)
        result.append({
            "name": ability_name,
            "display_name": source.get("dname", ability_name),
            "behavior": source.get("behavior"),
            "damage_type": source.get("dmg_type"),
            "pierces_debuff_immunity": source.get("bkbpierce"),
            "description": source.get("desc", ""),
            "mechanic_tags": sorted(tags),
            "mechanic_weights": dict(sorted(tags.items())),
            "availability": "conditional_upgrade_or_facet" if is_hidden else "base_kit",
            "draft_weight_multiplier": availability_weight,
        })
    return result, mechanics


def talent_records(hero_name, hero_abilities, abilities):
    records = []
    for talent in hero_abilities.get(hero_name, {}).get("talents", []):
        source = abilities.get(talent.get("name"), {})
        records.append({
            "name": talent.get("name"),
            "tier": talent.get("level"),
            "description": source.get("dname") or source.get("desc") or talent.get("name"),
        })
    return records


def facet_records(hero_name, hero_abilities):
    result = []
    for facet in hero_abilities.get(hero_name, {}).get("facets", []):
        result.append({
            "id": facet.get("id"),
            "name": facet.get("name"),
            "title": facet.get("title"),
            "description": facet.get("description", ""),
            "deprecated": str(facet.get("deprecated", "false")).lower() == "true",
        })
    return result


def merge_legacy(name, tags, weaknesses, rules):
    for tag in rules.get("HERO_SPECIAL_TAGS", {}).get(name, []):
        merge_weight(tags, normalize_tag(tag), 0.80)

    for key, value in rules.get("HERO_WEIGHT_OVERRIDES", {}).get(name, {}).items():
        if key.startswith("weak_") or key in rules.get("WEAKNESS_TAGS", []):
            merge_weight(weaknesses, normalize_weakness(key), value)
        else:
            merge_weight(tags, normalize_tag(key), value)

    detailed = rules.get("V04_PROFILE_OVERRIDES", {}).get(name, {})
    for key, value in detailed.get("tags", {}).items():
        merge_weight(tags, normalize_tag(key), value)
    for key, value in detailed.get("weaknesses", {}).items():
        merge_weight(weaknesses, normalize_weakness(key), value)

    legacy_weaknesses = rules.get("SPECIFIC_WEAKNESSES_V07", {}).get(name, {})
    for key, value in legacy_weaknesses.items():
        merge_weight(weaknesses, normalize_weakness(key), value)


def infer_weaknesses(tags, stats, generic_roles, base_weaknesses):
    weaknesses = dict(base_weaknesses)
    if tags.get("carry", 0) >= 0.6:
        merge_weight(weaknesses, "farm_dependency", 0.62 + 0.18 * tags.get("late_game_scaling", 0))
        merge_weight(weaknesses, "early_pressure", 0.48 + 0.18 * tags.get("late_game_scaling", 0))
    if tags.get("melee", 0) >= 0.7 and tags.get("mobility", 0) < 0.55:
        merge_weight(weaknesses, "kiting", 0.66)
        merge_weight(weaknesses, "low_range", 0.62)
    if tags.get("channeling", 0) >= 0.6:
        merge_weight(weaknesses, "channel_interrupt", 0.82)
        merge_weight(weaknesses, "hard_disable", 0.58)
    if tags.get("illusion", 0) >= 0.65:
        merge_weight(weaknesses, "aoe_control", 0.78)
        merge_weight(weaknesses, "wave_clear", 0.72)
    if tags.get("invisibility", 0) >= 0.65:
        merge_weight(weaknesses, "reveal", 0.82)
    if tags.get("evasion", 0) >= 0.65:
        merge_weight(weaknesses, "anti_evasion", 0.88)
    if tags.get("heal", 0) >= 0.65 or tags.get("sustain", 0) >= 0.75:
        merge_weight(weaknesses, "anti_regeneration", 0.72)
    if tags.get("mobility", 0) >= 0.72:
        merge_weight(weaknesses, "silence", 0.38)
        merge_weight(weaknesses, "root", 0.34)
        merge_weight(weaknesses, "leash", 0.36)
    if stats["move_speed_percentile"] <= 0.28 and tags.get("mobility", 0) < 0.55:
        merge_weight(weaknesses, "low_mobility", 0.72)
    if stats["armor_percentile"] <= 0.22:
        merge_weight(weaknesses, "low_armor", 0.68)
        merge_weight(weaknesses, "physical_burst", 0.52)
    if stats["durability_percentile"] <= 0.22:
        merge_weight(weaknesses, "low_survivability", 0.72)
        merge_weight(weaknesses, "burst", 0.55)
    if (
        "Nuker" in generic_roles
        and tags.get("carry", 0) < 0.75
        and tags.get("physical_damage", 0) < 0.75
    ):
        merge_weight(weaknesses, "silence", 0.34)
        merge_weight(weaknesses, "mana_pressure", 0.32)
    return weaknesses


def lane_profile(tags, stats, base):
    lane = {
        "last_hit": 0.72 * stats["damage_percentile"] + 0.28 * tags.get("physical_damage", 0),
        "deny": 0.62 * stats["damage_percentile"] + 0.20 * stats["armor_percentile"] + 0.18 * tags.get("ranged", 0),
        "harass": 0.28 * stats["range_percentile"] + 0.22 * tags.get("ranged", 0) + 0.24 * tags.get("burst", 0) + 0.14 * tags.get("slow", 0) + 0.12 * tags.get("damage_over_time", 0),
        "trade": 0.25 * stats["durability_percentile"] + 0.20 * stats["armor_percentile"] + 0.20 * tags.get("sustain", 0) + 0.20 * tags.get("physical_damage", 0) + 0.15 * tags.get("damage_reduction", 0),
        "kill_pressure": 0.32 * tags.get("burst", 0) + 0.30 * max(tags.get("stun", 0), tags.get("root", 0), tags.get("hard_disable", 0)) + 0.20 * tags.get("mobility", 0) + 0.18 * tags.get("slow", 0),
        "survivability": 0.38 * stats["durability_percentile"] + 0.25 * stats["armor_percentile"] + 0.22 * tags.get("mobility", 0) + 0.15 * max(tags.get("heal", 0), tags.get("damage_reduction", 0)),
        "sustain": 0.52 * max(tags.get("sustain", 0), tags.get("heal", 0), tags.get("lifesteal", 0)) + 0.28 * stats["regen_percentile"] + 0.20 * stats["durability_percentile"],
        "wave_clear": max(tags.get("wave_clear", 0), tags.get("aoe_damage", 0) * 0.78, tags.get("summon", 0) * 0.42),
        "range_advantage": 0.72 * stats["range_percentile"] + 0.28 * tags.get("ranged", 0),
    }
    lane["level_2_spike"] = 0.58 * lane["kill_pressure"] + 0.42 * lane["harass"]
    lane["level_3_spike"] = 0.48 * lane["kill_pressure"] + 0.28 * lane["harass"] + 0.24 * lane["wave_clear"]
    lane["level_6_spike"] = 0.32 * tags.get("burst", 0) + 0.28 * tags.get("teamfight", 0) + 0.25 * max(tags.get("stun", 0), tags.get("hard_disable", 0)) + 0.15 * tags.get("global", 0)
    for key, value in base.get("lane_profile", {}).items():
        lane[key] = max(lane.get(key, 0), float(value))
    return {key: round(clamp(value), 3) for key, value in lane.items()}


def power_spikes(tags, lane):
    early = sum(lane.values()) / max(1, len(lane))
    mid = (
        0.24 * tags.get("initiation", 0)
        + 0.22 * tags.get("burst", 0)
        + 0.18 * tags.get("mobility", 0)
        + 0.18 * tags.get("teamfight", 0)
        + 0.10 * tags.get("push", 0)
        + 0.08 * tags.get("hard_disable", 0)
    )
    late = (
        0.38 * tags.get("late_game_scaling", 0)
        + 0.22 * tags.get("physical_damage", 0)
        + 0.16 * tags.get("teamfight", 0)
        + 0.14 * tags.get("illusion", 0)
        + 0.10 * tags.get("push", 0)
    )
    values = {"early": clamp(early), "mid": clamp(mid), "late": clamp(late)}
    peak = max(values, key=values.get)
    return {**{key: round(value, 3) for key, value in values.items()}, "peak": peak}


def team_contributions(tags, base):
    source = {
        "initiation": max(tags.get("initiation", 0), tags.get("gap_close", 0) * 0.65),
        "hard_disable": max(tags.get("hard_disable", 0), tags.get("stun", 0), tags.get("root", 0), tags.get("hex", 0), tags.get("taunt", 0)),
        "frontline": max(tags.get("frontline", 0), tags.get("damage_reduction", 0) * 0.72),
        "wave_clear": max(tags.get("wave_clear", 0), tags.get("aoe_damage", 0) * 0.82),
        "physical_damage": max(tags.get("physical_damage", 0), tags.get("right_click", 0)),
        "magic_damage": tags.get("magic_damage", 0),
        # Self-heal is sustain, not automatically an ally save. Heal/dispel only
        # imply save contribution when the profile also has support evidence.
        "save": max(
            tags.get("save", 0),
            tags.get("heal", 0) * tags.get("support", 0) * 0.75,
            tags.get("dispel", 0) * tags.get("support", 0) * 0.65,
        ),
        "mobility": tags.get("mobility", 0),
        "roshan": max(tags.get("roshan", 0), tags.get("sustained_damage", 0) * 0.45, tags.get("summon", 0) * 0.25),
        "push": max(tags.get("push", 0), tags.get("summon", 0) * 0.68, tags.get("tower_pressure", 0)),
        "teamfight": max(tags.get("teamfight", 0), tags.get("aoe_damage", 0) * 0.68, tags.get("counter_initiation", 0)),
        "scaling": max(tags.get("late_game_scaling", 0), tags.get("carry", 0) * 0.72),
    }
    result = {}
    for key, value in source.items():
        derived = int(round(clamp(value) * 3))
        result[key] = max(int(base.get("team_contributions", {}).get(key, 0)), derived)
    return result


def item_profile(tags, weaknesses, base):
    current = dict(base.get("item_profile", {}))
    values = {
        "farm_dependency": max(current.get("farm_dependency", 0), weaknesses.get("farm_dependency", 0), tags.get("carry", 0) * 0.72),
        "bkb_dependency": max(current.get("bkb_dependency", 0), weaknesses.get("silence", 0) * 0.75, weaknesses.get("hard_disable", 0) * 0.68, weaknesses.get("magic_damage", 0) * 0.55),
        "dispel_dependency": max(current.get("dispel_dependency", 0), weaknesses.get("root", 0) * 0.72, weaknesses.get("silence", 0) * 0.55, weaknesses.get("anti_regeneration", 0) * 0.35),
        "mobility_dependency": max(current.get("mobility_dependency", 0), weaknesses.get("kiting", 0) * 0.78, weaknesses.get("low_mobility", 0) * 0.65),
        "damage_item_dependency": max(current.get("damage_item_dependency", 0), tags.get("carry", 0) * 0.78, tags.get("physical_damage", 0) * 0.52),
        "survivability_dependency": max(weaknesses.get("burst", 0), weaknesses.get("low_survivability", 0), weaknesses.get("physical_burst", 0) * 0.8),
        "mana_dependency": max(weaknesses.get("mana_pressure", 0), tags.get("magic_damage", 0) * 0.35),
    }
    return {key: round(clamp(value), 3) for key, value in values.items()}


def build():
    base = load_json(SOURCES / "heroes_v6_base.json")
    heroes = load_json(SOURCES / "dotaconstants_heroes.json")
    hero_abilities = load_json(SOURCES / "dotaconstants_hero_abilities.json")
    abilities = load_json(SOURCES / "dotaconstants_abilities.json")
    aghs = load_json(SOURCES / "dotaconstants_aghs_desc.json")
    legacy = load_json(DATA / "legacy_profile_rules.json")["rules"]

    hero_rows = list(heroes.values())
    metrics = {
        "damage": [primary_damage(hero) for hero in hero_rows],
        "durability": [durability(hero) for hero in hero_rows],
        "armor": [armor(hero) for hero in hero_rows],
        "range": [float(hero.get("attack_range", 0)) for hero in hero_rows],
        "move_speed": [float(hero.get("move_speed", 0)) for hero in hero_rows],
        "regen": [float(hero.get("base_health_regen", 0)) for hero in hero_rows],
    }
    aghs_by_name = {item["hero_name"]: item for item in aghs}

    output = {}
    for hero in hero_rows:
        source_name = hero["localized_name"]
        name = PUBLIC_NAME_ALIASES.get(source_name, source_name)
        if name not in base:
            raise RuntimeError(f"dotaconstants hero missing from v0.6 roster: {name}")
        old = base[name]
        internal = hero["name"]
        generic_roles = hero.get("roles", [])
        stats = {
            "damage_percentile": percentile(metrics["damage"], primary_damage(hero)),
            "durability_percentile": percentile(metrics["durability"], durability(hero)),
            "armor_percentile": percentile(metrics["armor"], armor(hero)),
            "range_percentile": percentile(metrics["range"], float(hero.get("attack_range", 0))),
            "move_speed_percentile": percentile(metrics["move_speed"], float(hero.get("move_speed", 0))),
            "regen_percentile": percentile(metrics["regen"], float(hero.get("base_health_regen", 0))),
        }

        tags = {}
        merge_weight(tags, "melee" if hero.get("attack_type") == "Melee" else "ranged", 1.0)
        for generic in generic_roles:
            for tag, value in ROLE_TAG_WEIGHTS.get(generic, {}).items():
                merge_weight(tags, tag, value)
        for tag in old.get("tags", []):
            merge_weight(tags, normalize_tag(tag), 0.82)

        ability_list, ability_tags = ability_records(internal, hero_abilities, abilities)
        for tag, value in ability_tags.items():
            merge_weight(tags, tag, value)
        if tags.get("stun", 0) or tags.get("root", 0) or tags.get("hex", 0) or tags.get("taunt", 0):
            merge_weight(tags, "hard_disable", max(tags.get("stun", 0), tags.get("root", 0), tags.get("hex", 0), tags.get("taunt", 0)))
            merge_weight(tags, "catch", tags["hard_disable"] * 0.82)
        if tags.get("heal", 0) or tags.get("lifesteal", 0):
            merge_weight(tags, "sustain", max(tags.get("heal", 0), tags.get("lifesteal", 0)) * 0.78)
        merge_legacy(name, tags, {}, legacy)

        weaknesses = {}
        for weakness in old.get("weaknesses", []):
            merge_weight(weaknesses, normalize_weakness(weakness), 0.72)
        # Reapply legacy rules to the actual weakness map.
        legacy_tags = dict(tags)
        merge_legacy(name, legacy_tags, weaknesses, legacy)
        tags = legacy_tags
        weaknesses = infer_weaknesses(tags, stats, generic_roles, weaknesses)

        lane = lane_profile(tags, stats, old)
        spikes = power_spikes(tags, lane)
        contributions = team_contributions(tags, old)
        items = item_profile(tags, weaknesses, old)
        upgrades = aghs_by_name.get(internal, {})

        output[name] = {
            "id": hero.get("id"),
            "internal_name": internal,
            "primary_attribute": hero.get("primary_attr"),
            "attack_type": hero.get("attack_type"),
            "generic_roles": generic_roles,
            "roles": role_profile(name, old, generic_roles, legacy),
            "difficulty": old.get("difficulty", 0.5),
            "data_quality": "ability_enriched_v2",
            "profile_confidence": round(0.90 if name in legacy.get("HERO_SPECIAL_TAGS", {}) else 0.85, 2),
            "patch": "7.41e",
            "tags": sorted(tags),
            "tag_weights": dict(sorted(tags.items())),
            "weaknesses": sorted(weaknesses),
            "weakness_weights": dict(sorted(weaknesses.items())),
            "team_contributions": contributions,
            "item_profile": items,
            "lane_profile": lane,
            "power_spikes": spikes,
            "base_stats": {
                "health": hero.get("base_health"),
                "health_regen": hero.get("base_health_regen"),
                "mana": hero.get("base_mana"),
                "mana_regen": hero.get("base_mana_regen"),
                "armor": hero.get("base_armor"),
                "magic_resistance": hero.get("base_mr"),
                "attack_min": hero.get("base_attack_min"),
                "attack_max": hero.get("base_attack_max"),
                "strength": hero.get("base_str"),
                "agility": hero.get("base_agi"),
                "intelligence": hero.get("base_int"),
                "strength_gain": hero.get("str_gain"),
                "agility_gain": hero.get("agi_gain"),
                "intelligence_gain": hero.get("int_gain"),
                "attack_range": hero.get("attack_range"),
                "attack_rate": hero.get("attack_rate"),
                "move_speed": hero.get("move_speed"),
                "day_vision": hero.get("day_vision"),
                "night_vision": hero.get("night_vision"),
            },
            "stat_percentiles": {key: round(value, 3) for key, value in stats.items()},
            "abilities": ability_list,
            "talents": talent_records(internal, hero_abilities, abilities),
            "facets": facet_records(internal, hero_abilities),
            "aghanim": {
                "has_scepter": bool(upgrades.get("has_scepter")),
                "scepter_skill": upgrades.get("scepter_skill_name"),
                "scepter_description": upgrades.get("scepter_desc", ""),
                "scepter_new_skill": bool(upgrades.get("scepter_new_skill")),
                "has_shard": bool(upgrades.get("has_shard")),
                "shard_skill": upgrades.get("shard_skill_name"),
                "shard_description": upgrades.get("shard_desc", ""),
                "shard_new_skill": bool(upgrades.get("shard_new_skill")),
            },
            "profile_sources": [
                "dotaconstants@" + DOTACONSTANTS_COMMIT[:12],
                "Dota_Draft_Assistant_v0.9 weighted rules",
                "dota-draft-bot-v0.6 curated baseline",
                "ability-description inference v2",
            ],
        }

    if set(output) != set(base):
        missing = sorted(set(base) - set(output))
        extra = sorted(set(output) - set(base))
        raise RuntimeError(f"Roster mismatch: missing={missing}, extra={extra}")
    DATA.joinpath("heroes.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    build_meta = {
        "schema_version": "hero-map-v2",
        "hero_count": len(output),
        "dotaconstants_commit": DOTACONSTANTS_COMMIT,
        "dotaconstants_commit_date": DOTACONSTANTS_DATE,
        "legacy_profile_source": "Dota_Draft_Assistant_v0.9.py",
        "base_profile_source": "dota-draft-bot-v0.6",
        "generated_by": "scripts/build_hero_profiles.py",
        "heuristic_notice": "Tag and weakness weights are deterministic heuristics, not measured win rates.",
    }
    DATA.joinpath("profile_build_meta.json").write_text(
        json.dumps(build_meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Built {len(output)} complete hero maps")


if __name__ == "__main__":
    build()
