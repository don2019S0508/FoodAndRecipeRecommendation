import unittest
from datetime import date

from recipe_recommender.recommendation import (
    determine_season,
    match_requirements,
    parse_requirements,
    recommend_recipe,
)
from recipe_recommender.gui import RecipeApp


class RequirementParsingTests(unittest.TestCase):
    def test_parse_requirements_includes(self):
        parsed = parse_requirements("vegan, quick, high protein")
        self.assertEqual(parsed["include"], ["vegan", "quick", "high-protein"])
        self.assertEqual(parsed["exclude"], [])
        self.assertIsNone(parsed["max_time"])

    def test_parse_requirements_excludes(self):
        parsed = parse_requirements("no nuts, avoid dairy")
        self.assertEqual(parsed["include"], [])
        self.assertEqual(parsed["exclude"], ["nut-free", "dairy-free"])

    def test_parse_requirements_max_time(self):
        parsed = parse_requirements("max 30, gluten free")
        self.assertEqual(parsed["include"], ["gluten-free"])
        self.assertEqual(parsed["max_time"], 30)


class MatchingTests(unittest.TestCase):
    def test_match_requirements_tags(self):
        recipe = {"dietary_tags": ["vegan", "quick"], "time_minutes": 20}
        parsed = {"include": ["vegan"], "exclude": [], "max_time": None}
        self.assertTrue(match_requirements(recipe, parsed))

    def test_match_requirements_exclude(self):
        recipe = {"dietary_tags": ["vegan", "nut-free"], "time_minutes": 20}
        parsed = {"include": [], "exclude": ["nut-free"], "max_time": None}
        self.assertFalse(match_requirements(recipe, parsed))

    def test_match_requirements_max_time(self):
        recipe = {"dietary_tags": ["quick"], "time_minutes": 25}
        parsed = {"include": [], "exclude": [], "max_time": 20}
        self.assertFalse(match_requirements(recipe, parsed))


class SeasonTests(unittest.TestCase):
    def test_season_northern_hemisphere(self):
        self.assertEqual(determine_season(date(2026, 1, 10), "north"), "winter")
        self.assertEqual(determine_season(date(2026, 4, 10), "north"), "spring")
        self.assertEqual(determine_season(date(2026, 7, 10), "north"), "summer")
        self.assertEqual(determine_season(date(2026, 10, 10), "north"), "autumn")

    def test_season_southern_hemisphere(self):
        self.assertEqual(determine_season(date(2026, 1, 10), "south"), "summer")
        self.assertEqual(determine_season(date(2026, 4, 10), "south"), "autumn")
        self.assertEqual(determine_season(date(2026, 7, 10), "south"), "winter")
        self.assertEqual(determine_season(date(2026, 10, 10), "south"), "spring")


class RecommendTests(unittest.TestCase):
    def test_recommend_recipe_filters_by_season(self):
        recipes = [
            {
                "id": "a",
                "name": "A",
                "seasons": ["spring"],
                "country_tags": ["united states"],
                "dietary_tags": [],
            },
            {
                "id": "b",
                "name": "B",
                "seasons": ["winter"],
                "country_tags": ["united states"],
                "dietary_tags": [],
            },
        ]
        stats = {}
        selected = recommend_recipe(recipes, stats, "winter", "United States", {"include": [], "exclude": [], "max_time": None})
        self.assertEqual(selected["id"], "b")


class LunarTermFormattingTests(unittest.TestCase):
    def test_popular_recipe_text_in_chinese(self):
        app = RecipeApp.__new__(RecipeApp)
        app.lang = "zh"
        app.stats = {"r1": {"total_score": 8.0, "count": 2}}
        app.recipes = []

        recipe = {
            "id": "r1",
            "name": "Sweet Potato",
            "name_zh": "红薯",
            "ingredients": ["sweet potato"],
            "ingredients_zh": ["红薯"],
            "steps": ["Bake."],
            "steps_zh": ["烤制。"],
            "time_minutes": 30,
        }

        text = app._build_popular_recipe_text(recipe)
        self.assertIn("最受欢迎食谱: 红薯", text)
        self.assertIn("评分: 4.0/5", text)
        self.assertIn("时间: 30 分钟", text)
        self.assertIn("食材:", text)
        self.assertIn("步骤:", text)


if __name__ == "__main__":
    unittest.main()
