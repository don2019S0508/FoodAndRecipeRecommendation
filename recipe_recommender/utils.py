import re
from datetime import date, datetime
from uuid import uuid4


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "recipe"


def generate_recipe_id(name: str) -> str:
    return f"{slugify(name)}-{uuid4().hex[:6]}"


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()
