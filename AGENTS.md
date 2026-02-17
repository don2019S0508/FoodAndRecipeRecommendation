# AGENTS.md - Developer Guide for Recipe Recommender

This document provides guidelines for agentic coding operations in this repository.

## Project Overview

- **Type**: Python CLI application with desktop GUI (tkinter)
- **Purpose**: Seasonal recipe recommendation system based on date, location, and dietary requirements
- **Data Storage**: JSON files in `data/` directory
- **Testing**: Python unittest framework

## Running the Application

```bash
# Run the application
python main.py

# Run with CSV export (non-interactive)
python main.py --csv-export data/recipes.csv --no-prompt

# Run with CSV import (non-interactive)
python main.py --csv-import data/recipes.csv --no-prompt

# Generate CSV template
python main.py --csv-template data/template.csv --no-prompt
```

## Running Tests

```bash
# Run all tests
python -m unittest

# Run a specific test file
python -m unittest tests.test_recommender

# Run a specific test class
python -m unittest tests.test_recommender.RequirementParsingTests

# Run a specific test method
python -m unittest tests.test_recommender.RequirementParsingTests.test_parse_requirements_includes -v
```

## Code Style Guidelines

### General Principles

- Use Python 3.10+ features (TypedDict, | union types, match/case)
- Prefer explicit over implicit
- Write self-documenting code with clear variable names

### Type Hints

- Always use type hints for function parameters and return types
- Use `TypedDict` for structured data (see `recipe_recommender/models.py`)
- Use `| None` instead of `Optional[]` for simple unions

```python
# Good
def recommend_recipe(recipes: list[Recipe], stats: RatingsById, season: str) -> Recipe | None:
    ...

# Bad
def recommend_recipe(recipes, stats, season):
    ...
```

### Naming Conventions

- **Functions/variables**: `snake_case` (e.g., `parse_requirements`, `total_views`)
- **Classes**: `PascalCase` (e.g., `RequirementParsingTests`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `SOUTHERN_HEMISPHERE_KEYWORDS`)
- **Files**: `snake_case.py`

### Imports

Organize imports in three sections (separate with blank line):

1. Standard library
2. Third-party packages
3. Local modules

```python
import csv
import json
from pathlib import Path

from recipe_recommender.models import Recipe, RatingsById
from recipe_recommender.utils import generate_recipe_id
```

### Data Models

Use `TypedDict` for all data structures:

```python
from typing import TypedDict, List

class Recipe(TypedDict, total=False):
    id: str
    name: str
    seasons: List[str]
    dietary_tags: List[str]
    time_minutes: int | None
```

### Error Handling

- Use exceptions for unexpected errors; let them propagate
- Handle expected error cases with conditional checks
- Never silently swallow exceptions

### File Paths

Use `pathlib.Path` for file operations:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RECIPES_PATH = DATA_DIR / "recipes.json"
```

### JSON Operations

- Use `json.dump` with `indent=2` and `sort_keys=True` for consistent formatting
- Always specify `encoding="utf-8"`
- Use helper functions in `storage.py` for loading/saving data

## Project Structure

```
.
├── main.py                 # Application entry point
├── recipe_recommender/
│   ├── __init__.py        # Package marker
│   ├── app.py             # CLI argument parsing, main logic
│   ├── gui.py             # Tkinter GUI implementation
│   ├── cli.py             # Command-line interface
│   ├── models.py          # TypedDict data models
│   ├── recommendation.py  # Core recommendation algorithms
│   ├── storage.py         # JSON file operations, CSV import/export
│   ├── utils.py           # Utility functions
│   └── lunar_term.py      # Lunar term calculations
├── data/
│   ├── recipes.json       # Recipe catalog
│   └── ratings.json       # User feedback data
└── tests/
    └── test_recommender.py # Unit tests
```

## Testing Guidelines

- Test file naming: `test_<module>.py`
- Test class naming: `<ModuleName>Tests`
- Test method naming: `test_<description>`
- Use descriptive test method names that explain the scenario

```python
class RequirementParsingTests(unittest.TestCase):
    def test_parse_requirements_includes(self):
        ...
```

## Data File Formats

### recipes.json

```json
{
  "id": "lemon-herb-salmon-5c8a1f",
  "name": "Lemon Herb Salmon with Asparagus",
  "name_zh": null,
  "country_tags": ["united states", "canada", "europe"],
  "seasons": ["spring", "summer"],
  "ingredients": ["salmon fillets", "asparagus", ...],
  "ingredients_zh": null,
  "steps": ["Preheat oven to 400F.", ...],
  "steps_zh": null,
  "time_minutes": 20,
  "dietary_tags": ["gluten-free", "quick"]
}
```

### ratings.json

```json
{
  "lemon-herb-salmon-5c8a1f": {
    "views": 10,
    "total_score": 35.0,
    "count": 7
  }
}
```

## CSV Import/Export

CSV columns use `|` as separator for list fields:
- `id`, `name`, `name_zh`, `country_tags`, `seasons`, `ingredients`, `ingredients_zh`, `steps`, `steps_zh`, `time_minutes`, `dietary_tags`

## Adding New Recipes

1. Use menu option `2` in the GUI, OR
2. Import via CSV: `python main.py --csv-import data/recipes.csv --no-prompt`
