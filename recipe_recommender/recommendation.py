import math
import re
from datetime import date

from recipe_recommender.models import Recipe, RatingsById


SOUTHERN_HEMISPHERE_KEYWORDS = {
    "australia",
    "new zealand",
    "south africa",
    "argentina",
    "chile",
    "uruguay",
    "paraguay",
    "bolivia",
    "peru",
    "brazil",
    "namibia",
    "botswana",
    "zimbabwe",
    "mozambique",
    "madagascar",
    "fiji",
}

REQUIREMENT_ALIASES = {
    "gluten free": "gluten-free",
    "gluten-free": "gluten-free",
    "vegetarian": "vegetarian",
    "vegan": "vegan",
    "quick": "quick",
    "low carb": "low-carb",
    "low-carb": "low-carb",
    "high protein": "high-protein",
    "high-protein": "high-protein",
    "dairy free": "dairy-free",
    "dairy-free": "dairy-free",
    "nut free": "nut-free",
    "nut-free": "nut-free",
    "nut": "nut-free",
    "nuts": "nut-free",
    "spicy": "spicy",
    "dairy": "dairy-free",
}


def determine_hemisphere(area: str) -> str:
    if not area:
        return "north"
    area_lower = area.lower()
    for keyword in SOUTHERN_HEMISPHERE_KEYWORDS:
        if keyword in area_lower:
            return "south"
    return "north"


def determine_season(target_date: date, hemisphere: str) -> str:
    month = target_date.month
    if hemisphere == "south":
        if month in (12, 1, 2):
            return "summer"
        if month in (3, 4, 5):
            return "autumn"
        if month in (6, 7, 8):
            return "winter"
        return "spring"
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def normalize_tag(tag: str) -> str:
    tag = tag.strip().lower()
    return REQUIREMENT_ALIASES.get(tag, tag)


def parse_requirements(text: str) -> dict[str, object]:
    if not text:
        return {"include": [], "exclude": [], "max_time": None}

    include: list[str] = []
    exclude: list[str] = []
    max_time: int | None = None

    pieces = [item.strip().lower() for item in text.split(",") if item.strip()]
    for item in pieces:
        if item.startswith(("no ", "without ", "exclude ", "avoid ")):
            cleaned = re.sub(r"^(no|without|exclude|avoid)\s+", "", item)
            if cleaned:
                exclude.append(normalize_tag(cleaned))
            continue

        time_match = re.search(r"(under|max|<=)\s*(\d{1,3})", item)
        if time_match:
            max_time = int(time_match.group(2))
            continue

        include.append(normalize_tag(item))

    return {"include": include, "exclude": exclude, "max_time": max_time}


def match_requirements(recipe: Recipe, requirements: dict[str, object]) -> bool:
    if not requirements:
        return True
    tags = {tag.lower() for tag in recipe.get("dietary_tags", [])}
    include = requirements.get("include", [])
    exclude = requirements.get("exclude", [])
    max_time = requirements.get("max_time")
    if include and not all(req in tags for req in include):
        return False
    if exclude and any(req in tags for req in exclude):
        return False
    if max_time is not None:
        time_minutes = recipe.get("time_minutes")
        if time_minutes is None or time_minutes > max_time:
            return False
    return True


def score_recipe(recipe_id: str, stats: RatingsById, total_views: int) -> float:
    entry = stats.get(recipe_id, {"views": 0, "total_score": 0.0, "count": 0})
    views = entry["views"]
    count = entry["count"]
    avg = entry["total_score"] / count if count else 3.0
    bonus = math.sqrt(math.log(total_views + 1) / (views + 1))
    return avg + bonus


def choose_recipe(candidates: list[Recipe], stats: RatingsById) -> Recipe:
    total_views = sum(entry.get("views", 0) for entry in stats.values())
    scored = [(score_recipe(recipe["id"], stats, total_views), recipe) for recipe in candidates]
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]


def recommend_recipe(
    recipes: list[Recipe],
    stats: RatingsById,
    season: str,
    area: str,
    requirements: dict[str, object],
) -> Recipe | None:
    area_lower = area.lower() if area else ""
    matched = [
        recipe
        for recipe in recipes
        if season in recipe.get("seasons", [])
        and (not area_lower or any(tag in area_lower for tag in recipe.get("country_tags", [])))
        and match_requirements(recipe, requirements)
    ]
    if not matched:
        matched = [
            recipe
            for recipe in recipes
            if season in recipe.get("seasons", []) and match_requirements(recipe, requirements)
        ]
    if not matched:
        matched = [recipe for recipe in recipes if match_requirements(recipe, requirements)]
    if not matched:
        return None
    return choose_recipe(matched, stats)
