from typing import TypedDict, List


class Recipe(TypedDict, total=False):
    id: str
    name: str
    name_zh: str
    country_tags: List[str]
    seasons: List[str]
    ingredients: List[str]
    ingredients_zh: List[str]
    steps: List[str]
    steps_zh: List[str]
    time_minutes: int | None
    dietary_tags: List[str]
    date: str
    solar_term: str


class RatingStats(TypedDict, total=False):
    views: int
    total_score: float
    count: int


RatingsById = dict[str, RatingStats]
