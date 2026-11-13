"""Extract static profile rules from the standalone v0.9 assistant.

The generated JSON is committed with the project, so the runtime does not depend
on the legacy file. Re-run this only when intentionally importing a newer legacy
rule set.
"""

import argparse
import ast
import json
from pathlib import Path


RULE_NAMES = {
    "HERO_SPECIAL_TAGS",
    "POSITION_OVERRIDES",
    "HERO_WEIGHT_OVERRIDES",
    "POSITION_FITNESS",
    "WEAKNESS_TAGS",
    "CORE_COMPOSITION_TARGETS",
    "TAG_GROUPS",
    "ROLE_WEIGHT_HINTS",
    "ARCHETYPE_PROFILES",
    "WEAKNESS_RULES",
    "V04_PROFILE_OVERRIDES",
    "ROLE_WEIGHTS_V07",
    "DEFAULT_WEAKNESSES_V07",
    "SPECIFIC_WEAKNESSES_V07",
    "ENEMY_COUNTER_NEEDS_V07",
}


def json_safe(value):
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (set, tuple, list)):
        converted = [json_safe(item) for item in value]
        return sorted(converted) if isinstance(value, set) else converted
    return value


def extract(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    rules = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name) or target.id not in RULE_NAMES:
                continue
            try:
                rules[target.id] = json_safe(ast.literal_eval(node.value))
            except (TypeError, ValueError):
                # Runtime-generated assignments are intentionally ignored. The
                # last statically evaluable declaration remains authoritative.
                pass
    missing = sorted(RULE_NAMES - rules.keys())
    if missing:
        raise RuntimeError(f"Missing legacy rule blocks: {', '.join(missing)}")
    return {
        "source_file": path.name,
        "source_version": "0.9",
        "rules": rules,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "app/data/legacy_profile_rules.json",
    )
    args = parser.parse_args()
    payload = extract(args.source)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Imported {len(payload['rules'])} rule blocks into {args.output}")


if __name__ == "__main__":
    main()
