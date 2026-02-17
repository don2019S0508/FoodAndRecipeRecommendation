from datetime import date

from recipe_recommender.models import Recipe, RatingsById
from recipe_recommender.recommendation import (
    determine_hemisphere,
    determine_season,
    parse_requirements,
    recommend_recipe,
)
from recipe_recommender.storage import (
    export_recipes_csv,
    import_recipes_csv,
    save_ratings,
    save_recipes,
)
from recipe_recommender.utils import generate_recipe_id, parse_date


def prompt_text(label: str, allow_blank: bool = True) -> str:
    while True:
        value = input(label).strip()
        if value or allow_blank:
            return value
        print("Please enter a value.")


def prompt_date() -> date:
    while True:
        raw = input("Enter a date (YYYY-MM-DD), or press Enter for today: ").strip()
        if not raw:
            return date.today()
        try:
            return parse_date(raw)
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")


def prompt_feedback() -> tuple[str | None, int | None]:
    raw = input(
        "\nOptional feedback: enter recipe ID and score 1-5 (or press Enter to skip): "
    ).strip()
    if not raw:
        return None, None
    parts = raw.split()
    if len(parts) < 2:
        print("Please provide both a recipe ID and a score.")
        return None, None
    recipe_id = parts[0]
    try:
        score = int(parts[1])
    except ValueError:
        print("Score must be a number between 1 and 5.")
        return None, None
    if score < 1 or score > 5:
        print("Score must be between 1 and 5.")
        return None, None
    return recipe_id, score


def display_recipe(recipe: Recipe, season: str) -> None:
    print("\nRecommendation")
    print(f"Recipe ID: {recipe['id']}")
    print(f"Name: {recipe['name']}")
    print(f"Season: {season}")
    print(f"Time: {recipe.get('time_minutes', 'N/A')} minutes")
    print("Ingredients:")
    for item in recipe.get("ingredients", []):
        print(f"- {item}")
    print("Steps:")
    for idx, step in enumerate(recipe.get("steps", []), start=1):
        print(f"{idx}. {step}")


def add_recipe(recipes: list[Recipe]) -> list[Recipe]:
    print("\nAdd a New Recipe")
    name = prompt_text("Recipe name: ", allow_blank=False)
    area = prompt_text("Country or area tags (comma-separated, optional): ")
    seasons = prompt_text("Seasons (comma-separated, e.g. spring, summer): ", allow_blank=False)
    ingredients = prompt_text("Ingredients (comma-separated): ", allow_blank=False)
    steps = prompt_text("Steps (semicolon-separated): ", allow_blank=False)
    time_raw = prompt_text("Time in minutes (optional): ")
    tags = prompt_text("Dietary tags (comma-separated, optional): ")

    recipe_id = generate_recipe_id(name)
    recipe = {
        "id": recipe_id,
        "name": name,
        "country_tags": [item.strip().lower() for item in area.split(",") if item.strip()],
        "seasons": [item.strip().lower() for item in seasons.split(",") if item.strip()],
        "ingredients": [item.strip() for item in ingredients.split(",") if item.strip()],
        "steps": [item.strip() for item in steps.split(";") if item.strip()],
        "time_minutes": int(time_raw) if time_raw.isdigit() else None,
        "dietary_tags": [item.strip().lower() for item in tags.split(",") if item.strip()],
    }
    recipes.append(recipe)
    print(f"Saved recipe with ID: {recipe_id}")
    return recipes


def update_views(stats: RatingsById, recipe_id: str) -> None:
    entry = stats.setdefault(recipe_id, {"views": 0, "total_score": 0.0, "count": 0})
    entry["views"] += 1


def update_feedback(stats: RatingsById, recipe_id: str, score: int) -> None:
    entry = stats.setdefault(recipe_id, {"views": 0, "total_score": 0.0, "count": 0})
    entry["total_score"] += score
    entry["count"] += 1


def run_menu(recipes: list[Recipe], stats: RatingsById) -> None:
    while True:
        print("\nSeasonal Recipe Recommender")
        print("1. Get a recommendation")
        print("2. Add a new recipe")
        print("3. Export recipes to CSV")
        print("4. Import recipes from CSV")
        print("5. Write CSV template")
        print("6. Quit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            target_date = prompt_date()
            area = prompt_text("Optional country or area: ")
            requirements = parse_requirements(
                prompt_text(
                    "Optional requirements (comma-separated, e.g. vegan, no nuts, max 30): "
                )
            )
            hemisphere = determine_hemisphere(area)
            season = determine_season(target_date, hemisphere)
            recipe = recommend_recipe(recipes, stats, season, area, requirements)
            if not recipe:
                print("No recipes matched your requirements yet.")
                continue
            update_views(stats, recipe["id"])
            save_ratings(stats)
            display_recipe(recipe, season)

            recipe_id, score = prompt_feedback()
            if recipe_id and score is not None:
                update_feedback(stats, recipe_id, score)
                save_ratings(stats)
                print("Thanks! Feedback recorded.")

        elif choice == "2":
            recipes = add_recipe(recipes)
            save_recipes(recipes)
        elif choice == "3":
            path = prompt_text("Enter CSV path to export (e.g. data/recipes.csv): ", allow_blank=False)
            export_recipes_csv(recipes, path)
            print(f"Exported {len(recipes)} recipes to {path}")
        elif choice == "4":
            path = prompt_text("Enter CSV path to import: ", allow_blank=False)
            new_recipes = import_recipes_csv(recipes, path, report=True)
            if new_recipes is not None:
                recipes = new_recipes
                save_recipes(recipes)
        elif choice == "5":
            path = prompt_text("Enter CSV template path to write: ", allow_blank=False)
            export_recipes_csv([], path)
            print(f"Wrote CSV template to {path}")
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Please choose 1, 2, 3, 4, 5, or 6.")
