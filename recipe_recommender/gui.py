from datetime import date
import re

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

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
from recipe_recommender.lunar_term import LunarTermRecommender


class RecipeApp(tk.Tk):
    def __init__(self, recipes: list[Recipe], stats: RatingsById) -> None:
        super().__init__()
        self.title("Seasonal Recipe Recommender")
        self.geometry("820x640")
        self.recipes = recipes
        self.stats = stats
        self.last_recipe_id: str | None = None
        self.lang = "en"
        self.widgets: dict[str, object] = {}
        self.lunar = LunarTermRecommender()

        self._build_ui()

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=10, pady=(10, 0))
        self.lang_button = ttk.Button(toolbar, command=self._toggle_language)
        self.lang_button.pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.notebook = notebook

        recommend_tab = ttk.Frame(notebook)
        add_tab = ttk.Frame(notebook)
        csv_tab = ttk.Frame(notebook)
        lunar_tab = ttk.Frame(notebook)

        notebook.add(recommend_tab, text="Recommend")
        notebook.add(add_tab, text="Add Recipe")
        notebook.add(csv_tab, text="CSV Tools")
        notebook.add(lunar_tab, text="Lunar Term Food")
        self.tabs = {
            "recommend": recommend_tab,
            "add": add_tab,
            "csv": csv_tab,
            "lunar": lunar_tab,
        }

        self._build_recommend_tab(recommend_tab)
        self._build_add_tab(add_tab)
        self._build_csv_tab(csv_tab)
        self._build_lunar_tab(lunar_tab)
        self._apply_language()

    def _build_recommend_tab(self, parent: ttk.Frame) -> None:
        form = ttk.Frame(parent)
        form.pack(fill="x", pady=5)

        date_label = ttk.Label(form, text="Date (YYYY-MM-DD or blank for today):")
        date_label.grid(
            row=0, column=0, sticky="w", pady=4
        )
        self.date_entry = ttk.Entry(form)
        self.date_entry.grid(row=0, column=1, sticky="ew", pady=4)
        self.date_entry.insert(0, date.today().isoformat())

        area_label = ttk.Label(form, text="Country or area (optional):")
        area_label.grid(
            row=1, column=0, sticky="w", pady=4
        )
        self.area_entry = ttk.Entry(form)
        self.area_entry.grid(row=1, column=1, sticky="ew", pady=4)

        req_label = ttk.Label(form, text="Requirements (comma-separated):")
        req_label.grid(
            row=2, column=0, sticky="w", pady=4
        )
        self.requirements_entry = ttk.Entry(form)
        self.requirements_entry.grid(row=2, column=1, sticky="ew", pady=4)

        form.columnconfigure(1, weight=1)

        recommend_button = ttk.Button(parent, text="Recommend", command=self._on_recommend)
        recommend_button.pack(
            pady=6
        )

        self.recommend_output = tk.Text(parent, height=14, wrap="word")
        self.recommend_output.pack(fill="both", expand=True, padx=4, pady=6)

        feedback_frame = ttk.LabelFrame(parent, text="Feedback")
        feedback_frame.pack(fill="x", padx=4, pady=6)

        feedback_id_label = ttk.Label(feedback_frame, text="Recipe ID:")
        feedback_id_label.grid(
            row=0, column=0, sticky="w", padx=4, pady=4
        )
        self.feedback_id_entry = ttk.Entry(feedback_frame)
        self.feedback_id_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=4)

        feedback_score_label = ttk.Label(feedback_frame, text="Score (1-5):")
        feedback_score_label.grid(
            row=0, column=2, sticky="w", padx=4, pady=4
        )
        self.feedback_score = tk.Spinbox(feedback_frame, from_=1, to=5, width=6)
        self.feedback_score.grid(row=0, column=3, sticky="w", padx=4, pady=4)

        feedback_button = ttk.Button(
            feedback_frame, text="Submit Feedback", command=self._on_feedback
        )
        feedback_button.grid(row=0, column=4, padx=4, pady=4)

        feedback_frame.columnconfigure(1, weight=1)
        self.widgets.update(
            {
                "date_label": date_label,
                "area_label": area_label,
                "req_label": req_label,
                "recommend_button": recommend_button,
                "feedback_frame": feedback_frame,
                "feedback_id_label": feedback_id_label,
                "feedback_score_label": feedback_score_label,
                "feedback_button": feedback_button,
            }
        )

    def _build_add_tab(self, parent: ttk.Frame) -> None:
        form = ttk.Frame(parent)
        form.pack(fill="both", expand=True, pady=6)

        self.add_name = self._add_labeled_entry(form, "Recipe name:", 0, key="add_name_label")
        self.add_area = self._add_labeled_entry(
            form, "Country/area tags (comma-separated):", 1, key="add_area_label"
        )
        self.add_seasons = self._add_labeled_entry(
            form, "Seasons (comma-separated):", 2, key="add_seasons_label"
        )
        self.add_ingredients = self._add_labeled_entry(
            form, "Ingredients (comma-separated):", 3, key="add_ingredients_label"
        )
        self.add_steps = self._add_labeled_entry(
            form, "Steps (semicolon-separated):", 4, key="add_steps_label"
        )
        self.add_time = self._add_labeled_entry(
            form, "Time in minutes (optional):", 5, key="add_time_label"
        )
        self.add_tags = self._add_labeled_entry(
            form, "Dietary tags (comma-separated):", 6, key="add_tags_label"
        )
        self.add_date = self._add_labeled_entry(
            form, "Date (YYYY-MM-DD, blank for today):", 7, key="add_date_label"
        )

        add_button = ttk.Button(parent, text="Add Recipe", command=self._on_add_recipe)
        add_button.pack(
            pady=8
        )
        self.widgets["add_button"] = add_button

    def _build_csv_tab(self, parent: ttk.Frame) -> None:
        options = ttk.Frame(parent)
        options.pack(fill="x", pady=6)

        self.strict_var = tk.BooleanVar(value=False)
        self.dry_run_var = tk.BooleanVar(value=False)

        strict_check = ttk.Checkbutton(
            options, text="Strict import", variable=self.strict_var
        )
        strict_check.pack(
            side="left", padx=6
        )
        dry_check = ttk.Checkbutton(options, text="Dry run", variable=self.dry_run_var)
        dry_check.pack(
            side="left", padx=6
        )

        export_button = ttk.Button(
            parent, text="Export Recipes CSV", command=self._on_export_csv
        )
        export_button.pack(
            pady=6
        )
        import_button = ttk.Button(
            parent, text="Import Recipes CSV", command=self._on_import_csv
        )
        import_button.pack(
            pady=6
        )
        template_button = ttk.Button(
            parent, text="Write CSV Template", command=self._on_template_csv
        )
        template_button.pack(
            pady=6
        )
        self.widgets.update(
            {
                "strict_check": strict_check,
                "dry_check": dry_check,
                "export_button": export_button,
                "import_button": import_button,
                "template_button": template_button,
            }
        )

    def _build_lunar_tab(self, parent: ttk.Frame) -> None:
        form = ttk.Frame(parent)
        form.pack(fill="x", pady=6)

        lunar_date_label = ttk.Label(form, text="Date (YYYY-MM-DD or blank for today):")
        lunar_date_label.grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.lunar_date_entry = ttk.Entry(form)
        self.lunar_date_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        self.lunar_date_entry.insert(0, date.today().isoformat())

        form.columnconfigure(1, weight=1)

        lunar_button = ttk.Button(parent, text="LunarTermFood", command=self._on_lunar)
        lunar_button.pack(pady=6)

        self.lunar_output = tk.Text(parent, height=14, wrap="word")
        self.lunar_output.pack(fill="both", expand=True, padx=4, pady=6)

        self.widgets.update(
            {
                "lunar_date_label": lunar_date_label,
                "lunar_button": lunar_button,
            }
        )

    def _add_labeled_entry(
        self, parent: ttk.Frame, label: str, row: int, key: str
    ) -> ttk.Entry:
        label_widget = ttk.Label(parent, text=label)
        label_widget.grid(row=row, column=0, sticky="w", padx=4, pady=4)
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=1, sticky="ew", padx=4, pady=4)
        parent.columnconfigure(1, weight=1)
        self.widgets[key] = label_widget
        return entry

    def _toggle_language(self) -> None:
        self.lang = "zh" if self.lang == "en" else "en"
        self._apply_language()

    def _apply_language(self) -> None:
        labels = {
            "en": {
                "lang_button": "中文",
                "tab_recommend": "Recommend",
                "tab_add": "Add Recipe",
                "tab_csv": "CSV Tools",
                "date_label": "Date (YYYY-MM-DD or blank for today):",
                "area_label": "Country or area (optional):",
                "req_label": "Requirements (comma-separated):",
                "recommend_button": "Recommend",
                "feedback_frame": "Feedback",
                "feedback_id_label": "Recipe ID:",
                "feedback_score_label": "Score (1-5):",
                "feedback_button": "Submit Feedback",
                "add_name_label": "Recipe name:",
                "add_area_label": "Country/area tags (comma-separated):",
                "add_seasons_label": "Seasons (comma-separated):",
                "add_ingredients_label": "Ingredients (comma-separated):",
                "add_steps_label": "Steps (semicolon-separated):",
                "add_time_label": "Time in minutes (optional):",
                "add_tags_label": "Dietary tags (comma-separated):",
                "add_date_label": "Date (YYYY-MM-DD, blank for today):",
                "add_button": "Add Recipe",
                "strict_check": "Strict import",
                "dry_check": "Dry run",
                "export_button": "Export Recipes CSV",
                "import_button": "Import Recipes CSV",
                "template_button": "Write CSV Template",
                "lunar_tab": "Lunar Term Food",
                "lunar_date_label": "Date (YYYY-MM-DD or blank for today):",
                "lunar_button": "LunarTermFood",
                "msg_invalid_date": "Please use YYYY-MM-DD.",
                "msg_no_match": "No recipes matched your requirements yet.",
                "msg_missing_id": "Please enter a recipe ID.",
                "msg_invalid_score": "Score must be between 1 and 5.",
                "msg_saved": "Recipe saved with ID: {id}",
                "msg_exported": "Exported {count} recipes.",
                "msg_imported": "Recipes loaded: {count}",
                "msg_dry_run": "Validation complete. No changes saved.",
                "msg_import_rejected": "Strict mode rejected the import due to validation warnings.",
                "msg_template": "CSV template written.",
                "msg_feedback": "Feedback recorded.",
                "msg_missing_name": "Recipe name is required.",
                "label_recommend": "Recommendation",
                "label_name": "Name",
                "label_season": "Season",
                "label_time": "Time",
                "label_ingredients": "Ingredients",
                "label_steps": "Steps",
                "minutes": "minutes",
            },
            "zh": {
                "lang_button": "English",
                "tab_recommend": "推荐",
                "tab_add": "添加菜谱",
                "tab_csv": "CSV 工具",
                "date_label": "日期（YYYY-MM-DD，留空为今天）：",
                "area_label": "国家或地区（可选）：",
                "req_label": "需求（逗号分隔）：",
                "recommend_button": "推荐",
                "feedback_frame": "反馈",
                "feedback_id_label": "菜谱 ID：",
                "feedback_score_label": "评分（1-5）：",
                "feedback_button": "提交反馈",
                "add_name_label": "菜谱名称：",
                "add_area_label": "国家/地区标签（逗号分隔）：",
                "add_seasons_label": "季节（逗号分隔）：",
                "add_ingredients_label": "食材（逗号分隔）：",
                "add_steps_label": "步骤（分号分隔）：",
                "add_time_label": "时间（分钟，可选）：",
                "add_tags_label": "饮食标签（逗号分隔）：",
                "add_date_label": "日期（YYYY-MM-DD，留空为今天）：",
                "add_button": "添加菜谱",
                "strict_check": "严格导入",
                "dry_check": "只校验不保存",
                "export_button": "导出 CSV",
                "import_button": "导入 CSV",
                "template_button": "写入 CSV 模板",
                "lunar_tab": "二十四节气",
                "lunar_date_label": "日期（YYYY-MM-DD，留空为今天）：",
                "lunar_button": "节气推荐",
                "msg_invalid_date": "请输入 YYYY-MM-DD 格式的日期。",
                "msg_no_match": "没有找到符合条件的菜谱。",
                "msg_missing_id": "请输入菜谱 ID。",
                "msg_invalid_score": "评分必须在 1 到 5 之间。",
                "msg_saved": "已保存菜谱，ID：{id}",
                "msg_exported": "已导出 {count} 个菜谱。",
                "msg_imported": "已加载菜谱：{count}",
                "msg_dry_run": "校验完成，未保存更改。",
                "msg_import_rejected": "严格模式：因校验警告而拒绝导入。",
                "msg_template": "CSV 模板已写入。",
                "msg_feedback": "反馈已记录。",
                "msg_missing_name": "菜谱名称为必填。",
                "label_recommend": "推荐结果",
                "label_name": "名称",
                "label_season": "季节",
                "label_time": "时间",
                "label_ingredients": "食材",
                "label_steps": "步骤",
                "minutes": "分钟",
            },
        }

        text = labels[self.lang]
        self.lang_button.config(text=text["lang_button"])
        self.notebook.tab(self.tabs["recommend"], text=text["tab_recommend"])
        self.notebook.tab(self.tabs["add"], text=text["tab_add"])
        self.notebook.tab(self.tabs["csv"], text=text["tab_csv"])
        self.notebook.tab(self.tabs["lunar"], text=text["lunar_tab"])
        self.widgets["date_label"].config(text=text["date_label"])
        self.widgets["area_label"].config(text=text["area_label"])
        self.widgets["req_label"].config(text=text["req_label"])
        self.widgets["recommend_button"].config(text=text["recommend_button"])
        self.widgets["feedback_frame"].config(text=text["feedback_frame"])
        self.widgets["feedback_id_label"].config(text=text["feedback_id_label"])
        self.widgets["feedback_score_label"].config(text=text["feedback_score_label"])
        self.widgets["feedback_button"].config(text=text["feedback_button"])
        self.widgets["add_name_label"].config(text=text["add_name_label"])
        self.widgets["add_area_label"].config(text=text["add_area_label"])
        self.widgets["add_seasons_label"].config(text=text["add_seasons_label"])
        self.widgets["add_ingredients_label"].config(text=text["add_ingredients_label"])
        self.widgets["add_steps_label"].config(text=text["add_steps_label"])
        self.widgets["add_time_label"].config(text=text["add_time_label"])
        self.widgets["add_tags_label"].config(text=text["add_tags_label"])
        self.widgets["add_date_label"].config(text=text["add_date_label"])
        self.widgets["add_button"].config(text=text["add_button"])
        self.widgets["strict_check"].config(text=text["strict_check"])
        self.widgets["dry_check"].config(text=text["dry_check"])
        self.widgets["export_button"].config(text=text["export_button"])
        self.widgets["import_button"].config(text=text["import_button"])
        self.widgets["template_button"].config(text=text["template_button"])
        self.widgets["lunar_date_label"].config(text=text["lunar_date_label"])
        self.widgets["lunar_button"].config(text=text["lunar_button"])

    def _translate_requirements(self, text: str) -> str:
        if self.lang != "zh" or not text:
            return text

        replacements = {
            "纯素": "vegan",
            "素食": "vegetarian",
            "无麸质": "gluten free",
            "无乳制品": "no dairy",
            "无奶": "no dairy",
            "无坚果": "no nuts",
            "避免坚果": "no nuts",
            "低碳": "low carb",
            "高蛋白": "high protein",
            "辣": "spicy",
            "快速": "quick",
        }
        normalized = text
        for cn, en in replacements.items():
            normalized = normalized.replace(cn, en)

        match = re.search(r"(不超过|最多|少于|少於|<=|<)\s*(\d{1,3})", normalized)
        if match:
            normalized = re.sub(
                r"(不超过|最多|少于|少於|<=|<)\s*(\d{1,3})",
                lambda m: f"max {m.group(2)}",
                normalized,
            )

        return normalized

    def _normalize_seasons(self, text: str) -> str:
        if self.lang != "zh":
            return text
        replacements = {
            "春": "spring",
            "夏": "summer",
            "秋": "autumn",
            "冬": "winter",
            "春季": "spring",
            "夏季": "summer",
            "秋季": "autumn",
            "冬季": "winter",
        }
        normalized = text
        for cn, en in replacements.items():
            normalized = normalized.replace(cn, en)
        return normalized

    def _normalize_tags(self, text: str) -> str:
        if self.lang != "zh":
            return text
        replacements = {
            "纯素": "vegan",
            "素食": "vegetarian",
            "无麸质": "gluten-free",
            "无乳制品": "dairy-free",
            "无奶": "dairy-free",
            "无坚果": "nut-free",
            "低碳": "low-carb",
            "高蛋白": "high-protein",
            "辣": "spicy",
            "快速": "quick",
        }
        normalized = text
        for cn, en in replacements.items():
            normalized = normalized.replace(cn, en)
        return normalized

    def _season_label(self, season: str) -> str:
        if self.lang != "zh":
            return season
        mapping = {
            "spring": "春",
            "summer": "夏",
            "autumn": "秋",
            "winter": "冬",
        }
        return mapping.get(season, season)

    def _ensure_chinese_fields(self, recipe: Recipe) -> None:
        if recipe.get("name_zh") and recipe.get("ingredients_zh") and recipe.get("steps_zh"):
            return
        name = recipe.get("name", "")
        ingredients = recipe.get("ingredients", [])
        steps = recipe.get("steps", [])
        recipe["name_zh"] = recipe.get("name_zh") or self._translate_text(name)
        recipe["ingredients_zh"] = recipe.get("ingredients_zh") or [
            self._translate_text(item) for item in ingredients
        ]
        recipe["steps_zh"] = recipe.get("steps_zh") or [
            self._translate_sentence(item) for item in steps
        ]
        save_recipes(self.recipes)

    def _translate_text(self, text: str) -> str:
        glossary = {
            "salmon": "三文鱼",
            "asparagus": "芦笋",
            "lemon": "柠檬",
            "olive oil": "橄榄油",
            "garlic": "大蒜",
            "parsley": "欧芹",
            "salt": "盐",
            "pepper": "黑胡椒",
            "mushroom": "蘑菇",
            "carrot": "胡萝卜",
            "celery": "芹菜",
            "onion": "洋葱",
            "barley": "大麦",
            "broth": "高汤",
            "thyme": "百里香",
            "bay leaf": "月桂叶",
            "cucumber": "黄瓜",
            "rice vinegar": "米醋",
            "sesame oil": "香油",
            "soy sauce": "酱油",
            "ginger": "姜",
            "scallion": "葱",
            "sesame seeds": "芝麻",
            "pumpkin": "南瓜",
            "parmesan": "帕玛森",
            "butter": "黄油",
            "tomato": "番茄",
            "basil": "罗勒",
            "pasta": "意面",
            "lentil": "扁豆",
            "curry": "咖喱",
            "coconut milk": "椰奶",
            "spinach": "菠菜",
            "yogurt": "酸奶",
            "strawberry": "草莓",
            "blueberry": "蓝莓",
            "granola": "格兰诺拉",
            "honey": "蜂蜜",
            "lemon zest": "柠檬皮屑",
            "sweet potato": "红薯",
            "rosemary": "迷迭香",
            "chicken": "鸡肉",
            "lime": "青柠",
            "lettuce": "生菜",
            "chickpeas": "鹰嘴豆",
            "feta": "菲达奶酪",
            "oregano": "牛至",
            "broccoli": "西兰花",
            "bell pepper": "彩椒",
            "snap peas": "荷兰豆",
            "chili": "辣椒",
            "oats": "燕麦",
            "apple": "苹果",
            "cinnamon": "肉桂",
            "maple syrup": "枫糖浆",
            "vanilla": "香草精",
            "steak": "牛排",
            "green beans": "四季豆",
            "leek": "韭葱",
            "peas": "豌豆",
            "egg": "鸡蛋",
            "milk": "牛奶",
            "cauliflower": "花椰菜",
            "sumac": "苏木香",
            "corn": "玉米",
        }
        translated = text
        for en, zh in glossary.items():
            translated = re.sub(rf"\\b{re.escape(en)}\\b", zh, translated, flags=re.IGNORECASE)
        return translated

    def _translate_sentence(self, text: str) -> str:
        templates = {
            "Preheat oven to": "预热烤箱至",
            "Saute": "炒香",
            "Add": "加入",
            "Mix": "混合",
            "Toss": "拌匀",
            "Simmer": "小火炖",
            "Roast": "烤",
            "Cook": "煮",
            "Stir in": "拌入",
            "Bake": "烤",
            "Whisk": "搅匀",
            "Top with": "撒上",
            "Finish with": "最后加入",
            "Stir-fry": "快炒",
        }
        translated = text
        for en, zh in templates.items():
            translated = re.sub(rf"\\b{re.escape(en)}\\b", zh, translated, flags=re.IGNORECASE)
        translated = self._translate_text(translated)
        return translated

    def _on_recommend(self) -> None:
        raw_date = self.date_entry.get().strip()
        area = self.area_entry.get().strip()
        requirements_text = self.requirements_entry.get().strip()

        try:
            target_date = parse_date(raw_date) if raw_date else None
        except ValueError:
            messagebox.showerror("Invalid date", self._t("msg_invalid_date"))
            return

        if target_date is None:
            from datetime import date as dt_date

            target_date = dt_date.today()

        requirements = parse_requirements(self._translate_requirements(requirements_text))
        hemisphere = determine_hemisphere(area)
        season = determine_season(target_date, hemisphere)
        recipe = recommend_recipe(self.recipes, self.stats, season, area, requirements)
        if not recipe:
            messagebox.showinfo("No match", self._t("msg_no_match"))
            return

        if self.lang == "zh":
            self._ensure_chinese_fields(recipe)

        self._update_views(recipe["id"])
        save_ratings(self.stats)
        self.last_recipe_id = recipe["id"]
        self.feedback_id_entry.delete(0, tk.END)
        self.feedback_id_entry.insert(0, recipe["id"])

        self.recommend_output.delete("1.0", tk.END)
        name = recipe.get("name")
        ingredients = recipe.get("ingredients", [])
        steps = recipe.get("steps", [])
        if self.lang == "zh":
            name = recipe.get("name_zh") or name
            ingredients = recipe.get("ingredients_zh") or ingredients
            steps = recipe.get("steps_zh") or steps

        self.recommend_output.insert(
            tk.END,
            f"{self._t('label_recipe_id')}: {recipe['id']}\n"
            f"{self._t('label_name')}: {name}\n"
            f"{self._t('label_season')}: {self._season_label(season)}\n"
            f"{self._t('label_time')}: {recipe.get('time_minutes', 'N/A')} {self._t('minutes')}\n\n"
            f"{self._t('label_ingredients')}:\n"
            + "\n".join(f"- {item}" for item in ingredients)
            + f"\n\n{self._t('label_steps')}:\n"
            + "\n".join(f"{idx}. {step}" for idx, step in enumerate(steps, start=1))
        )

    def _on_feedback(self) -> None:
        recipe_id = self.feedback_id_entry.get().strip()
        score_raw = self.feedback_score.get().strip()
        if not recipe_id:
            messagebox.showerror("Missing ID", self._t("msg_missing_id"))
            return
        try:
            score = int(score_raw)
        except ValueError:
            messagebox.showerror("Invalid score", self._t("msg_invalid_score"))
            return
        if score < 1 or score > 5:
            messagebox.showerror("Invalid score", self._t("msg_invalid_score"))
            return
        self._update_feedback(recipe_id, score)
        save_ratings(self.stats)
        messagebox.showinfo("Thanks!", self._t("msg_feedback"))

    def _on_add_recipe(self) -> None:
        from datetime import date as dt_date

        name = self.add_name.get().strip()
        if not name:
            messagebox.showerror("Missing name", self._t("msg_missing_name"))
            return

        recipe_id = generate_recipe_id(name)
        name_zh = self.add_name.get().strip() if self.lang == "zh" else None

        raw_date = self.add_date.get().strip()
        if raw_date:
            try:
                from recipe_recommender.utils import parse_date
                parsed_date = parse_date(raw_date)
                date_str = parsed_date.isoformat()
            except ValueError:
                messagebox.showerror("Invalid date", self._t("msg_invalid_date"))
                return
        else:
            date_str = dt_date.today().isoformat()
        solar_term = self.lunar.get_solar_term(date_str)

        recipe = {
            "id": recipe_id,
            "name": name,
            "name_zh": name_zh,
            "country_tags": [
                item.strip().lower()
                for item in self.add_area.get().split(",")
                if item.strip()
            ],
            "seasons": [
                item.strip().lower()
                for item in self._normalize_seasons(self.add_seasons.get()).split(",")
                if item.strip()
            ],
            "ingredients": [
                item.strip()
                for item in self.add_ingredients.get().split(",")
                if item.strip()
            ],
            "ingredients_zh": [
                item.strip()
                for item in self.add_ingredients.get().split(",")
                if item.strip()
            ]
            if self.lang == "zh"
            else [],
            "steps": [
                item.strip()
                for item in self.add_steps.get().split(";")
                if item.strip()
            ],
            "steps_zh": [
                item.strip()
                for item in self.add_steps.get().split(";")
                if item.strip()
            ]
            if self.lang == "zh"
            else [],
            "time_minutes": int(self.add_time.get())
            if self.add_time.get().isdigit()
            else None,
            "dietary_tags": [
                item.strip().lower()
                for item in self._normalize_tags(self.add_tags.get()).split(",")
                if item.strip()
            ],
            "date": date_str,
            "solar_term": solar_term or "",
        }

        self.recipes.append(recipe)
        save_recipes(self.recipes)
        messagebox.showinfo("Saved", self._t("msg_saved").format(id=recipe_id))

        for entry in (
            self.add_name,
            self.add_area,
            self.add_seasons,
            self.add_ingredients,
            self.add_steps,
            self.add_time,
            self.add_tags,
            self.add_date,
        ):
            entry.delete(0, tk.END)

    def _on_export_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export Recipes CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        export_recipes_csv(self.recipes, path)
        messagebox.showinfo("Exported", self._t("msg_exported").format(count=len(self.recipes)))

    def _on_import_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Recipes CSV",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        new_recipes = import_recipes_csv(
            self.recipes,
            path,
            report=False,
            strict=self.strict_var.get(),
        )
        if new_recipes is None:
            messagebox.showwarning(
                "Import rejected",
                self._t("msg_import_rejected"),
            )
            return
        if self.dry_run_var.get():
            messagebox.showinfo("Dry run", self._t("msg_dry_run"))
            return
        self.recipes = new_recipes
        save_recipes(self.recipes)
        messagebox.showinfo("Imported", self._t("msg_imported").format(count=len(self.recipes)))

    def _on_template_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Write CSV Template",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        export_recipes_csv([], path)
        messagebox.showinfo("Template", self._t("msg_template"))

    def _on_lunar(self) -> None:
        raw_date = self.lunar_date_entry.get().strip()
        try:
            target_date = parse_date(raw_date) if raw_date else None
        except ValueError:
            messagebox.showerror("Invalid date", self._t("msg_invalid_date"))
            return

        if target_date is None:
            from datetime import date as dt_date

            target_date = dt_date.today()

        date_str = target_date.strftime("%Y-%m-%d")
        term = self.lunar.get_solar_term(date_str)
        if not term:
            messagebox.showinfo("No match", self._t("msg_no_match"))
            return

        recommendation = self.lunar.get_recommendation(term)
        english = self.lunar.to_english(term, recommendation)

        if self.lang == "zh":
            title = recommendation["name"]
            description = recommendation["description"]
            recipes = recommendation["recipes"]
            tips = recommendation["recommendations"]
            term_display = term
        else:
            title = english["name"]
            description = english["description"]
            recipes = english["recipes"]
            tips = english["recommendations"]
            term_display = english["solar_term"]

        matching_recipes = [
            r for r in self.recipes
            if r.get("solar_term") == term
        ]

        popular_recipe_text = ""
        if matching_recipes:
            def get_rating(recipe):
                recipe_id = recipe.get("id", "")
                stats = self.stats.get(recipe_id, {})
                total_score = stats.get("total_score", 0)
                count = stats.get("count", 0)
                if count > 0:
                    return total_score / count
                return 0

            matching_recipes.sort(key=get_rating, reverse=True)
            most_popular = matching_recipes[0]
            popular_name = most_popular.get("name", "")
            popular_id = most_popular.get("id", "")
            popular_stats = self.stats.get(popular_id, {})
            popular_count = popular_stats.get("count", 0)
            popular_total = popular_stats.get("total_score", 0)

            if popular_count > 0:
                popular_rating = popular_total / popular_count
                if self.lang == "zh":
                    popular_recipe_text = f"\n\n⭐ 最受欢迎食谱: {popular_name} (评分: {popular_rating:.1f}/5)"
                else:
                    popular_recipe_text = f"\n\n⭐ Most Popular Recipe: {popular_name} (Rating: {popular_rating:.1f}/5)"
            else:
                if self.lang == "zh":
                    popular_recipe_text = f"\n\n⭐ 最受欢迎食谱: {popular_name}"
                else:
                    popular_recipe_text = f"\n\n⭐ Most Popular Recipe: {popular_name}"

            popular_ingredients = most_popular.get("ingredients", [])
            popular_steps = most_popular.get("steps", [])
            popular_time = most_popular.get("time_minutes")

            if self.lang == "zh":
                popular_recipe_text += f"\n   时间: {popular_time} 分钟" if popular_time else ""
                popular_recipe_text += "\n   食材:\n" + "\n".join(f"     - {item}" for item in popular_ingredients)
                popular_recipe_text += "\n   步骤:\n" + "\n".join(f"     {idx}. {step}" for idx, step in enumerate(popular_steps, start=1))
            else:
                popular_recipe_text += f"\n   Time: {popular_time} minutes" if popular_time else ""
                popular_recipe_text += "\n   Ingredients:\n" + "\n".join(f"     - {item}" for item in popular_ingredients)
                popular_recipe_text += "\n   Steps:\n" + "\n".join(f"     {idx}. {step}" for idx, step in enumerate(popular_steps, start=1))

        self.lunar_output.delete("1.0", tk.END)
        self.lunar_output.insert(
            tk.END,
            f"{self._t('label_date')}: {date_str}\n"
            f"{self._t('label_solar_term')}: {term_display}\n"
            f"{title}: {description}\n\n"
            f"{self._t('label_recipes')}:\n"
            + "\n".join(f"- {item}" for item in recipes)
            + f"\n\n{self._t('label_tips')}:\n"
            + "\n".join(f"- {item}" for item in tips)
            + popular_recipe_text
        )

    def _update_views(self, recipe_id: str) -> None:
        entry = self.stats.setdefault(recipe_id, {"views": 0, "total_score": 0.0, "count": 0})
        entry["views"] += 1

    def _update_feedback(self, recipe_id: str, score: int) -> None:
        entry = self.stats.setdefault(recipe_id, {"views": 0, "total_score": 0.0, "count": 0})
        entry["total_score"] += score
        entry["count"] += 1

    def _t(self, key: str) -> str:
        labels = {
            "en": {
                "msg_invalid_date": "Please use YYYY-MM-DD.",
                "msg_no_match": "No recipes matched your requirements yet.",
                "msg_missing_id": "Please enter a recipe ID.",
                "msg_invalid_score": "Score must be between 1 and 5.",
                "msg_saved": "Recipe saved with ID: {id}",
                "msg_exported": "Exported {count} recipes.",
                "msg_imported": "Recipes loaded: {count}",
                "msg_dry_run": "Validation complete. No changes saved.",
                "msg_import_rejected": "Strict mode rejected the import due to validation warnings.",
                "msg_template": "CSV template written.",
                "msg_feedback": "Feedback recorded.",
                "msg_missing_name": "Recipe name is required.",
                "label_recipe_id": "Recipe ID",
                "label_name": "Name",
                "label_season": "Season",
                "label_time": "Time",
                "label_ingredients": "Ingredients",
                "label_steps": "Steps",
                "minutes": "minutes",
                "label_date": "Date",
                "label_solar_term": "Solar Term",
                "label_recipes": "Recipes",
                "label_tips": "Tips",
            },
            "zh": {
                "msg_invalid_date": "请输入 YYYY-MM-DD 格式的日期。",
                "msg_no_match": "没有找到符合条件的菜谱。",
                "msg_missing_id": "请输入菜谱 ID。",
                "msg_invalid_score": "评分必须在 1 到 5 之间。",
                "msg_saved": "已保存菜谱，ID：{id}",
                "msg_exported": "已导出 {count} 个菜谱。",
                "msg_imported": "已加载菜谱：{count}",
                "msg_dry_run": "校验完成，未保存更改。",
                "msg_import_rejected": "严格模式：因校验警告而拒绝导入。",
                "msg_template": "CSV 模板已写入。",
                "msg_feedback": "反馈已记录。",
                "msg_missing_name": "菜谱名称为必填。",
                "label_recipe_id": "菜谱 ID",
                "label_name": "名称",
                "label_season": "季节",
                "label_time": "时间",
                "label_ingredients": "食材",
                "label_steps": "步骤",
                "minutes": "分钟",
                "label_date": "日期",
                "label_solar_term": "节气",
                "label_recipes": "推荐食谱",
                "label_tips": "养生注意事项",
            },
        }
        return labels[self.lang][key]


def run_gui(recipes: list[Recipe], stats: RatingsById) -> None:
    app = RecipeApp(recipes, stats)
    app.mainloop()
