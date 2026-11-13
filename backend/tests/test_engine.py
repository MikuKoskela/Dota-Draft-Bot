import unittest

from app.engine import DraftEngine


class DraftEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = DraftEngine()
        cls.own_team = {
            "pos1": None,
            "pos2": "Lina",
            "pos3": "Axe",
            "pos4": "Silencer",
            "pos5": "Jakiro",
        }
        cls.enemy_team = {
            "pos1": "Pudge",
            "pos2": "Templar Assassin",
            "pos3": "Dawnbreaker",
            "pos4": "Hoodwink",
            "pos5": "Crystal Maiden",
        }

    def test_every_directed_pair_is_resolvable(self):
        heroes = list(self.engine.heroes)
        resolved = 0
        for candidate in heroes:
            for enemy in heroes:
                if candidate == enemy:
                    continue
                matchup = self.engine.resolve_matchup(candidate, enemy)
                self.assertIn(matchup["source"], {"curated", "curated_inverse", "inferred"})
                self.assertGreaterEqual(matchup["confidence"], 0)
                resolved += 1
        self.assertEqual(resolved, 127 * 126)

    def test_curated_and_inverse_sources_take_priority(self):
        direct = self.engine.resolve_matchup("Ursa", "Axe")
        inverse = self.engine.resolve_matchup("Axe", "Ursa")
        self.assertEqual(direct["source"], "curated")
        self.assertEqual(inverse["source"], "curated_inverse")
        self.assertAlmostEqual(inverse["lane"], -direct["lane"])

    def test_missing_pair_uses_profile_inference(self):
        matchup = self.engine.resolve_matchup("Drow Ranger", "Crystal Maiden")
        self.assertEqual(matchup["source"], "inferred")
        self.assertTrue(any(abs(matchup[key]) > 0 for key in ("lane", "mid_game", "late_game")))
        self.assertTrue(matchup["reasons"])

    def test_role_floor_removes_generic_pos1_placeholders(self):
        pool = self.engine.build_available_heroes(
            self.own_team, self.enemy_team, "pos1", available_heroes=None
        )
        self.assertIn("Drow Ranger", pool)
        self.assertNotIn("Chen", pool)
        self.assertNotIn("Pudge", pool)
        self.assertLess(len(pool), 60)

    def test_picks_and_bans_are_removed(self):
        pool = self.engine.build_available_heroes(
            self.own_team,
            self.enemy_team,
            "pos1",
            available_heroes=None,
            banned_heroes=["Drow Ranger"],
        )
        for unavailable in (*self.engine.known(self.own_team), *self.engine.known(self.enemy_team), "Drow Ranger"):
            self.assertNotIn(unavailable, pool)

    def test_rank_result_contains_enemy_matchup_breakdown(self):
        result = self.engine.rank_candidates(
            own_team=self.own_team,
            enemy_team=self.enemy_team,
            available_heroes=["Drow Ranger"],
            target_role="pos1",
            draft_phase="late",
        )[0]
        self.assertEqual(len(result["matchup_details"]), 5)
        self.assertGreater(result["matchup_confidence"], 0)
        self.assertEqual({m["enemy"] for m in result["matchup_details"]}, set(self.engine.known(self.enemy_team)))
        for matchup in result["matchup_details"]:
            # API values are rounded independently from the engine's internal
            # unrounded raw value, so allow one displayed-cent tolerance.
            self.assertLessEqual(
                abs(matchup["effective_lane"] - round(matchup["lane"] * matchup["confidence"], 2)),
                .01,
            )

    def test_all_hero_maps_are_complete_and_weighted(self):
        required = {
            "roles", "tag_weights", "weakness_weights", "team_contributions",
            "item_profile", "lane_profile", "power_spikes", "base_stats",
            "abilities", "talents", "facets", "aghanim", "profile_sources",
        }
        for name, profile in self.engine.heroes.items():
            self.assertFalse(required - set(profile), name)
            self.assertTrue(profile["tag_weights"], name)
            self.assertTrue(profile["weakness_weights"], name)
            self.assertTrue(profile["abilities"], name)
            self.assertTrue(profile["talents"], name)
            self.assertTrue(profile["facets"], name)
            self.assertEqual(len(profile["lane_profile"]), 12, name)
            self.assertTrue(all(0 <= value <= 1 for value in profile["tag_weights"].values()), name)
            self.assertTrue(all(0 <= value <= 1 for value in profile["weakness_weights"].values()), name)

    def test_known_hero_mechanics(self):
        expected = {
            "Anti-Mage": {"mana_burn", "mobility", "spell_reflect"},
            "Silencer": {"silence", "global"},
            "Earth Spirit": {"stun", "silence", "mobility"},
            "Phantom Assassin": {"evasion", "critical_strike", "mobility"},
            "Hoodwink": {"stun", "break"},
        }
        for hero, tags in expected.items():
            self.assertTrue(tags <= set(self.engine.hero(hero)["tag_weights"]), hero)

    def test_conditional_abilities_have_reduced_draft_weight(self):
        hoodwink = self.engine.hero("Hoodwink")
        decoy = next(ability for ability in hoodwink["abilities"] if ability["display_name"] == "Decoy")
        self.assertEqual(decoy["availability"], "conditional_upgrade_or_facet")
        self.assertEqual(decoy["draft_weight_multiplier"], 0.55)
        self.assertLess(hoodwink["tag_weights"]["invisibility"], 0.55)

    def test_weighted_graph_rule_uses_both_evidence_weights(self):
        value, reasons = self.engine.graph_interactions("Anti-Mage", "Templar Assassin", "counter")
        expected = (
            1.0
            * self.engine.tag_weight("Anti-Mage", "hard_disable")
            * self.engine.tag_weight("Templar Assassin", "mobility")
        )
        self.assertGreaterEqual(value, expected)
        self.assertTrue(any("evidence" in reason for reason in reasons))

    def test_every_position_has_role_aware_lane_context(self):
        for role in ("pos1", "pos2", "pos3", "pos4", "pos5"):
            score = self.engine.calculate_laning("Dawnbreaker", self.own_team, self.enemy_team, role)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_all_item_dependencies_affect_costs(self):
        pressure = self.engine.calculate_enemy_pressure(self.enemy_team)
        self.assertGreater(pressure["armor"], 0)
        self.assertGreater(pressure["survivability"], 0)
        profile = self.engine.hero("Drow Ranger")["item_profile"]
        original = dict(profile)
        try:
            for key in (
                "farm_dependency", "damage_item_dependency", "survivability_dependency", "mana_dependency"
            ):
                profile.update({field: 0 for field in profile})
                baseline = self.engine.calculate_item_tax("Drow Ranger", self.enemy_team)
                profile[key] = 1
                self.assertGreater(self.engine.calculate_item_tax("Drow Ranger", self.enemy_team), baseline, key)
        finally:
            profile.clear()
            profile.update(original)


if __name__ == "__main__":
    unittest.main()
