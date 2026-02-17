import csv
import json
from pathlib import Path

from recipe_recommender.models import Recipe, RatingsById
from recipe_recommender.utils import generate_recipe_id


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RECIPES_PATH = DATA_DIR / "recipes.json"
RATINGS_PATH = DATA_DIR / "ratings.json"


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def load_recipes(default_recipes: list[Recipe]) -> list[Recipe]:
    return load_json(RECIPES_PATH, default_recipes)


def save_recipes(recipes: list[Recipe]) -> None:
    save_json(RECIPES_PATH, recipes)


def load_ratings() -> RatingsById:
    return load_json(RATINGS_PATH, {})


def save_ratings(stats: RatingsById) -> None:
    save_json(RATINGS_PATH, stats)


def export_recipes_csv(recipes: list[Recipe], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "name",
                "name_zh",
                "country_tags",
                "seasons",
                "ingredients",
                "ingredients_zh",
                "steps",
                "steps_zh",
                "time_minutes",
                "dietary_tags",
                "date",
                "solar_term",
            ],
        )
        writer.writeheader()
        for recipe in recipes:
            writer.writerow(
                {
                    "id": recipe.get("id", ""),
                    "name": recipe.get("name", ""),
                    "name_zh": recipe.get("name_zh", ""),
                    "country_tags": "|".join(recipe.get("country_tags", [])),
                    "seasons": "|".join(recipe.get("seasons", [])),
                    "ingredients": "|".join(recipe.get("ingredients", [])),
                    "ingredients_zh": "|".join(recipe.get("ingredients_zh") or []),
                    "steps": "|".join(recipe.get("steps", [])),
                    "steps_zh": "|".join(recipe.get("steps_zh") or []),
                    "time_minutes": recipe.get("time_minutes") or "",
                    "dietary_tags": "|".join(recipe.get("dietary_tags", [])),
                    "date": recipe.get("date", ""),
                    "solar_term": recipe.get("solar_term", ""),
                }
            )


def import_recipes_csv(
    recipes: list[Recipe],
    path: str | Path,
    report: bool = True,
    strict: bool = False,
) -> list[Recipe] | None:
    path = Path(path)
    if not path.exists():
        print("CSV file not found.")
        return recipes

    existing = {recipe["id"]: recipe for recipe in recipes if recipe.get("id")}
    existing_by_name = {
        recipe["name"].strip().lower(): recipe["id"]
        for recipe in recipes
        if recipe.get("name")
    }
    added = 0
    updated = 0
    skipped = 0
    warnings = []

    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        row_index = 1
        for row in reader:
            row_index += 1
            name = (row.get("name") or "").strip()
            if not name:
                skipped += 1
                warnings.append(f"Row {row_index}: missing name.")
                continue

            recipe_id = (row.get("id") or "").strip() or generate_recipe_id(name)
            if recipe_id in existing:
                existing_name = (existing[recipe_id].get("name") or "").strip().lower()
                if name.lower() != existing_name:
                    warnings.append(
                        f"Row {row_index}: recipe ID {recipe_id} already exists with different name."
                    )

            duplicate_name_id = existing_by_name.get(name.lower())
            if duplicate_name_id and duplicate_name_id != recipe_id:
                warnings.append(
                    f"Row {row_index}: duplicate name '{name}' already exists as {duplicate_name_id}."
                )

            name_zh = (row.get("name_zh") or "").strip()
            recipe = {
                "id": recipe_id,
                "name": name,
                "name_zh": name_zh or None,
                "country_tags": [
                    item.strip().lower()
                    for item in (row.get("country_tags") or "").split("|")
                    if item.strip()
                ],
                "seasons": [
                    item.strip().lower()
                    for item in (row.get("seasons") or "").split("|")
                    if item.strip()
                ],
                "ingredients": [
                    item.strip()
                    for item in (row.get("ingredients") or "").split("|")
                    if item.strip()
                ],
                "ingredients_zh": [
                    item.strip()
                    for item in (row.get("ingredients_zh") or "").split("|")
                    if item.strip()
                ],
                "steps": [
                    item.strip()
                    for item in (row.get("steps") or "").split("|")
                    if item.strip()
                ],
                "steps_zh": [
                    item.strip()
                    for item in (row.get("steps_zh") or "").split("|")
                    if item.strip()
                ],
                "time_minutes": int(row["time_minutes"])
                if (row.get("time_minutes") or "").isdigit()
                else None,
                "dietary_tags": [
                    item.strip().lower()
                    for item in (row.get("dietary_tags") or "").split("|")
                    if item.strip()
                ],
                "date": (row.get("date") or "").strip() or None,
                "solar_term": (row.get("solar_term") or "").strip() or None,
            }

            if recipe_id in existing:
                existing[recipe_id] = recipe
                updated += 1
            else:
                existing[recipe_id] = recipe
                added += 1
            existing_by_name[name.lower()] = recipe_id

    if report:
        print(f"Imported {added} recipes, updated {updated} recipes, skipped {skipped} rows.")
        if warnings:
            print("Validation warnings:")
            for warning in warnings:
                print(f"- {warning}")
    if strict and (warnings or skipped):
        print("Strict mode enabled: import rejected due to validation warnings or skipped rows.")
        return None
    return list(existing.values())
