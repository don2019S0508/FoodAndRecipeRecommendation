import argparse

from recipe_recommender.gui import run_gui
from recipe_recommender.models import Recipe
from recipe_recommender.storage import (
    export_recipes_csv,
    import_recipes_csv,
    load_ratings,
    load_recipes,
    save_recipes,
)


DEFAULT_RECIPES: list[Recipe] = [
    {
        "id": "lemon-herb-salmon-5c8a1f",
        "name": "Lemon Herb Salmon with Asparagus",
        "country_tags": ["united states", "canada", "europe"],
        "seasons": ["spring", "summer"],
        "ingredients": [
            "salmon fillets",
            "asparagus",
            "lemon",
            "olive oil",
            "garlic",
            "parsley",
            "salt",
            "pepper",
        ],
        "steps": [
            "Preheat oven to 400F.",
            "Toss asparagus with olive oil, salt, and pepper on a sheet pan.",
            "Place salmon alongside asparagus, top with garlic, lemon, and parsley.",
            "Roast 12 to 15 minutes until salmon flakes easily.",
        ],
        "time_minutes": 20,
        "dietary_tags": ["gluten-free", "quick"],
    },
    {
        "id": "mushroom-barley-stew-5b1a72",
        "name": "Mushroom Barley Stew",
        "country_tags": ["united states", "europe"],
        "seasons": ["autumn", "winter"],
        "ingredients": [
            "cremini mushrooms",
            "carrots",
            "celery",
            "onion",
            "garlic",
            "pearl barley",
            "vegetable broth",
            "thyme",
            "bay leaf",
        ],
        "steps": [
            "Saute onion, carrot, celery, and garlic until soft.",
            "Add mushrooms and cook until browned.",
            "Stir in barley, broth, thyme, and bay leaf.",
            "Simmer 35 to 45 minutes until barley is tender.",
        ],
        "time_minutes": 50,
        "dietary_tags": ["vegetarian"],
    },
    {
        "id": "chilled-cucumber-noodle-bowl-2ac9e0",
        "name": "Chilled Cucumber Noodle Bowl",
        "country_tags": ["japan", "korea", "europe"],
        "seasons": ["summer"],
        "ingredients": [
            "cucumber noodles",
            "rice vinegar",
            "sesame oil",
            "soy sauce",
            "ginger",
            "scallions",
            "sesame seeds",
        ],
        "steps": [
            "Whisk vinegar, sesame oil, soy sauce, and ginger.",
            "Toss cucumber noodles in dressing.",
            "Top with scallions and sesame seeds, chill 10 minutes.",
        ],
        "time_minutes": 15,
        "dietary_tags": ["vegan", "quick"],
    },
    {
        "id": "pumpkin-sage-risotto-9b2e4d",
        "name": "Pumpkin Sage Risotto",
        "country_tags": ["italy", "europe"],
        "seasons": ["autumn"],
        "ingredients": [
            "arborio rice",
            "pumpkin puree",
            "vegetable broth",
            "onion",
            "garlic",
            "sage",
            "parmesan",
            "butter",
        ],
        "steps": [
            "Saute onion and garlic in butter.",
            "Stir in rice until lightly toasted.",
            "Add broth gradually, stirring until absorbed.",
            "Mix in pumpkin and sage, finish with parmesan.",
        ],
        "time_minutes": 40,
        "dietary_tags": ["vegetarian"],
    },
    {
        "id": "tomato-basil-pasta-41f8b2",
        "name": "Tomato Basil Pasta",
        "country_tags": ["italy", "europe", "united states"],
        "seasons": ["summer"],
        "ingredients": [
            "pasta",
            "cherry tomatoes",
            "basil",
            "garlic",
            "olive oil",
            "parmesan",
        ],
        "steps": [
            "Cook pasta until al dente.",
            "Saute garlic and tomatoes in olive oil.",
            "Toss pasta with tomatoes and basil, top with parmesan.",
        ],
        "time_minutes": 25,
        "dietary_tags": ["vegetarian", "quick"],
    },
    {
        "id": "spiced-lentil-curry-0d31aa",
        "name": "Spiced Lentil Curry",
        "country_tags": ["india", "south asia"],
        "seasons": ["autumn", "winter"],
        "ingredients": [
            "red lentils",
            "onion",
            "garlic",
            "ginger",
            "tomato",
            "curry powder",
            "coconut milk",
            "spinach",
        ],
        "steps": [
            "Saute onion, garlic, and ginger.",
            "Add lentils, tomato, curry powder, and water.",
            "Simmer until lentils are tender, stir in coconut milk and spinach.",
        ],
        "time_minutes": 35,
        "dietary_tags": ["vegan", "gluten-free"],
    },
    {
        "id": "spring-berry-yogurt-parfait-2b8c6e",
        "name": "Spring Berry Yogurt Parfait",
        "country_tags": ["united states", "europe"],
        "seasons": ["spring"],
        "ingredients": [
            "greek yogurt",
            "strawberries",
            "blueberries",
            "granola",
            "honey",
            "lemon zest",
        ],
        "steps": [
            "Layer yogurt, berries, and granola in a glass.",
            "Drizzle honey and add lemon zest before serving.",
        ],
        "time_minutes": 10,
        "dietary_tags": ["vegetarian", "quick"],
    },
    {
        "id": "roasted-root-vegetable-traybake-3a7d12",
        "name": "Roasted Root Vegetable Traybake",
        "country_tags": ["united states", "europe"],
        "seasons": ["winter", "autumn"],
        "ingredients": [
            "carrots",
            "parsnips",
            "sweet potatoes",
            "red onion",
            "olive oil",
            "rosemary",
            "salt",
            "pepper",
        ],
        "steps": [
            "Preheat oven to 425F.",
            "Toss vegetables with olive oil, rosemary, salt, and pepper.",
            "Roast 30 to 35 minutes until caramelized.",
        ],
        "time_minutes": 40,
        "dietary_tags": ["vegan", "gluten-free"],
    },
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Seasonal Recipe Recommender")
    parser.add_argument("--csv-export", dest="csv_export", help="Export recipes to CSV path.")
    parser.add_argument("--csv-import", dest="csv_import", help="Import recipes from CSV path.")
    parser.add_argument(
        "--csv-template",
        dest="csv_template",
        help="Write a CSV template header to the given path.",
    )
    parser.add_argument(
        "--csv-dry-run",
        action="store_true",
        help="Validate CSV import without saving changes.",
    )
    parser.add_argument(
        "--strict-import",
        action="store_true",
        help="Reject CSV import if validation warnings occur.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Run CSV import/export without entering the interactive menu.",
    )
    return parser


def run_cli_actions(args: argparse.Namespace) -> bool:
    recipes = load_recipes(DEFAULT_RECIPES)
    updated = False

    if args.csv_template:
        export_recipes_csv([], args.csv_template)
        print(f"Wrote CSV template to {args.csv_template}")
        updated = True

    if args.csv_import:
        new_recipes = import_recipes_csv(
            recipes, args.csv_import, report=True, strict=args.strict_import
        )
        if new_recipes is None:
            updated = True
        elif args.csv_dry_run:
            print("Dry run enabled: no changes were saved.")
            updated = True
        else:
            recipes = new_recipes
            save_recipes(recipes)
            updated = True

    if args.csv_export:
        export_recipes_csv(recipes, args.csv_export)
        print(f"Exported {len(recipes)} recipes to {args.csv_export}")
        updated = True

    return updated


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.csv_import or args.csv_export or args.csv_template:
        updated = run_cli_actions(args)
        if args.no_prompt:
            return
        if updated:
            print("CSV operation completed. Entering interactive mode.")

    recipes = load_recipes(DEFAULT_RECIPES)
    stats = load_ratings()
    run_gui(recipes, stats)
