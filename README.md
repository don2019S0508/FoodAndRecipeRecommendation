# Seasonal Recipe Recommender

A Python program recommends seasonal recipes based on date, location, and optional requirements. It learns from feedback to improve future recommendations. It gives seasonal food and recipes based on Lunar Term through the panel "LunarTermRecipe".

This version launches a desktop GUI for all inputs and outputs. A user can enter a recipe with a score, and the program uses re-inforced machine learning based on the score for next time recipe recommendation.

It also includes a Lunar Term Food tab for 24 solar-term recommendations in English.

Traditional Chinese medicine emphasizes body recuperation through proper seasonal food and recipes.

**Hope that this program could give some heplful recipe recommendation to long COVID patients for body recuperation. However, a patient should discuss with a doctor before taking a recipe recommendation from this program.**

Still need domain experts to give more recipes and suggestions. This program is just a demo, need to make it better.

## Run

```bash
python main.py
```

## What It Prompts For

- Date (`YYYY-MM-DD`, or press Enter for today)
- Optional country or area
- Optional requirements (comma-separated)

Examples:

- `vegan, quick`
- `no nuts, max 30`
- `gluten free, avoid dairy, under 20`

## Feedback Learning

After a recommendation, you can provide feedback:

```
<recipe_id> <score 1-5>
```

This updates a lightweight bandit-style score stored in `data/ratings.json`.

## Add New Recipes

Choose menu option `2` to add a recipe. The program generates a unique recipe ID and saves it to `data/recipes.json`.

## Import/Export CSV

Use the CSV tools tab to export, import, or write a template.
You can also run non-interactively:

```bash
python main.py --csv-export data/recipes.csv --no-prompt
python main.py --csv-import data/recipes.csv --no-prompt
python main.py --csv-template data/recipes-template.csv --no-prompt
```

CSV columns:

`id`, `name`, `name_zh`, `country_tags`, `seasons`, `ingredients`, `ingredients_zh`, `steps`, `steps_zh`, `time_minutes`, `dietary_tags`

List fields use `|` as a separator. If `id` is missing on import, it will be generated.
Imports run validation and report duplicates or missing fields.

Strict import mode rejects the import if validation warnings occur:

```bash
python main.py --csv-import data/recipes.csv --strict-import --no-prompt
```

Dry-run validation without saving:

```bash
python main.py --csv-import data/recipes.csv --csv-dry-run --no-prompt
```

## Tests

Run tests with:

```bash
python -m unittest
```

## Files

- `main.py` app entry
- `data/recipes.json` recipe catalog
- `data/ratings.json` feedback data

**Dong Sun Wong**
**Email**: [Reach out for collaborations](mailto:donwong07@gmail.com)
