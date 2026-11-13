import unittest
from unittest.mock import patch

from fastapi import HTTPException

from app.main import allowed_origins_from_env, hero_profile, matchup, meta, rank_draft
from app.models import DraftRequest, DraftResult


class ApiContractTests(unittest.TestCase):
    def test_allowed_origins_are_configurable_without_wildcards(self):
        with patch.dict(
            "os.environ",
            {"ALLOWED_ORIGINS": "https://empuzki.github.io, https://preview.example"},
        ):
            self.assertEqual(
                allowed_origins_from_env(),
                ["https://empuzki.github.io", "https://preview.example"],
            )

        with patch.dict("os.environ", {"ALLOWED_ORIGINS": "*"}):
            with self.assertRaises(ValueError):
                allowed_origins_from_env()

    def test_meta_exposes_matchup_coverage(self):
        payload = meta()
        self.assertEqual(payload["engine_version"], "0.7.0")
        self.assertEqual(payload["directed_matchups"], 127 * 126)
        self.assertEqual(payload["complete_profile_coverage"]["abilities"], 127)
        self.assertEqual(payload["complete_profile_coverage"]["weakness_weights"], 127)
        self.assertAlmostEqual(sum(payload["scoring"]["component_weights"].values()), 1.0)

    def test_full_hero_profile_endpoint(self):
        profile = hero_profile("Anti-Mage")
        self.assertEqual(profile["name"], "Anti-Mage")
        self.assertIn("mana_burn", profile["tag_weights"])
        self.assertTrue(profile["abilities"])
        self.assertTrue(profile["talents"])
        self.assertIn("scepter_description", profile["aghanim"])

        with self.assertRaises(HTTPException) as error:
            hero_profile("Unknown")
        self.assertEqual(error.exception.status_code, 404)

    def test_matchup_endpoint_contract(self):
        payload = matchup("Ursa", "Axe")
        self.assertEqual(payload["source"], "curated")
        self.assertEqual(payload["candidate"], "Ursa")
        self.assertEqual(payload["enemy"], "Axe")

        with self.assertRaises(HTTPException) as error:
            matchup("Unknown", "Axe")
        self.assertEqual(error.exception.status_code, 404)

    def test_rank_response_matches_pydantic_schema(self):
        request = DraftRequest.model_validate({
            "own_team": {
                "pos1": None,
                "pos2": "Lina",
                "pos3": "Axe",
                "pos4": "Silencer",
                "pos5": "Jakiro",
            },
            "enemy_team": {
                "pos1": "Pudge",
                "pos2": "Templar Assassin",
                "pos3": "Dawnbreaker",
                "pos4": "Hoodwink",
                "pos5": "Crystal Maiden",
            },
            "available_heroes": ["Drow Ranger"],
            "banned_heroes": [],
            "target_role": "pos1",
            "draft_phase": "late",
        })
        results = rank_draft(request)
        validated = [DraftResult.model_validate(result) for result in results]
        self.assertEqual(len(validated), 1)
        self.assertEqual(len(validated[0].matchup_details), 5)


if __name__ == "__main__":
    unittest.main()
