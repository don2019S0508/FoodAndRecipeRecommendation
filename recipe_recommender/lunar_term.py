import datetime
import math
from typing import Dict, Optional


class LunarTermRecommender:
    """Solar-term recipe recommender (24 solar terms)."""

    def __init__(self) -> None:
        self.solar_terms = {
            "立春": 315,
            "雨水": 330,
            "惊蛰": 345,
            "春分": 0,
            "清明": 15,
            "谷雨": 30,
            "立夏": 45,
            "小满": 60,
            "芒种": 75,
            "夏至": 90,
            "小暑": 105,
            "大暑": 120,
            "立秋": 135,
            "处暑": 150,
            "白露": 165,
            "秋分": 180,
            "寒露": 195,
            "霜降": 210,
            "立冬": 225,
            "小雪": 240,
            "大雪": 255,
            "冬至": 270,
            "小寒": 285,
            "大寒": 300,
        }
        self.recipes_db = self._initialize_recipes()

    def _initialize_recipes(self) -> Dict[str, Dict]:
        return {
            "立春": {
                "name": "立春养生",
                "description": "立春阳气初生，宜升补",
                "recipes": [
                    "韭菜炒鸡蛋 - 助阳气生发",
                    "春笋炖鸡汤 - 补充元气",
                    "枸杞粥 - 养肝明目",
                ],
                "recommendations": [
                    "多吃辛甘发散食物",
                    "少食酸味食物",
                    "注意保暖，防倒春寒",
                ],
            },
            "雨水": {
                "name": "雨水养生",
                "description": "雨水时节，湿气渐重",
                "recipes": [
                    "山药薏米粥 - 健脾祛湿",
                    "鲫鱼汤 - 利水消肿",
                    "红枣莲子羹 - 养心安神",
                ],
                "recommendations": [
                    "注意防湿防潮",
                    "多吃健脾利湿食物",
                    "适当运动排湿",
                ],
            },
            "春分": {
                "name": "春分养生",
                "description": "阴阳平衡，注重调和",
                "recipes": [
                    "春菜炒肉片 - 平衡阴阳",
                    "香椿拌豆腐 - 清热健胃",
                    "荠菜饺子 - 平肝和胃",
                ],
                "recommendations": [
                    "饮食宜寒热均衡",
                    "保持情绪稳定",
                    "适量户外运动",
                ],
            },
            "清明": {
                "name": "清明养生",
                "description": "清明时节，注重养肝",
                "recipes": [
                    "艾草青团 - 祛湿散寒",
                    "菠菜猪肝汤 - 补血养肝",
                    "菊花枸杞茶 - 清肝明目",
                ],
                "recommendations": [
                    "保持心情舒畅",
                    "多吃绿色蔬菜",
                    "早睡早起养肝",
                ],
            },
            "谷雨": {
                "name": "谷雨养生",
                "description": "雨生百谷，健脾祛湿",
                "recipes": [
                    "玉米须茶 - 利尿祛湿",
                    "茯苓粥 - 健脾安神",
                    "芹菜炒百合 - 清热平肝",
                ],
                "recommendations": [
                    "防湿邪入侵",
                    "适当食用祛湿食物",
                    "避免久坐湿地",
                ],
            },
            "立夏": {
                "name": "立夏养生",
                "description": "夏季开始，养心为主",
                "recipes": [
                    "荷叶粥 - 清热解暑",
                    "凉拌苦瓜 - 清心火",
                    "绿豆汤 - 清热解毒",
                ],
                "recommendations": [
                    "保持心情愉快",
                    "午间适当休息",
                    "多吃红色食物养心",
                ],
            },
            "小满": {
                "name": "小满养生",
                "description": "小满时节，清热利湿",
                "recipes": [
                    "冬瓜汤 - 利水消肿",
                    "黄瓜拌海蜇 - 清热解暑",
                    "薏米红豆粥 - 健脾祛湿",
                ],
                "recommendations": [
                    "注意防暑降温",
                    "避免过食生冷",
                    "保持皮肤清洁",
                ],
            },
            "芒种": {
                "name": "芒种养生",
                "description": "梅雨时节，防湿防暑",
                "recipes": [
                    "酸梅汤 - 生津止渴",
                    "姜茶 - 驱寒祛湿",
                    "紫苏炒田螺 - 解表散寒",
                ],
                "recommendations": [
                    "注意防霉防潮",
                    "饮食宜清淡",
                    "适当午睡养心",
                ],
            },
            "夏至": {
                "name": "夏至养生",
                "description": "阳气最盛，注意养阴",
                "recipes": [
                    "凉面 - 清热开胃",
                    "番茄鸡蛋汤 - 生津止渴",
                    "西瓜皮炒肉 - 清热利尿",
                ],
                "recommendations": [
                    "注意防暑降温",
                    "适当午休",
                    "多补充水分",
                ],
            },
            "小暑": {
                "name": "小暑养生",
                "description": "小暑炎热，注意防暑",
                "recipes": [
                    "莲子汤 - 清心安神",
                    "丝瓜汤 - 清热凉血",
                    "薄荷茶 - 清凉解暑",
                ],
                "recommendations": [
                    "避免烈日暴晒",
                    "饮食宜清淡",
                    "保持充足睡眠",
                ],
            },
            "大暑": {
                "name": "大暑养生",
                "description": "一年最热，重在清热",
                "recipes": [
                    "冬瓜老鸭汤 - 清热滋补",
                    "绿豆百合粥 - 清热安神",
                    "凉拌黄瓜 - 清热解渴",
                ],
                "recommendations": [
                    "防中暑",
                    "多喝温水",
                    "避免过度出汗",
                ],
            },
            "立秋": {
                "name": "立秋养生",
                "description": "秋季开始，滋阴润燥",
                "recipes": [
                    "银耳莲子羹 - 滋阴润肺",
                    "梨子糖水 - 润肺止咳",
                    "芝麻糊 - 滋阴润燥",
                ],
                "recommendations": [
                    "少吃辛辣",
                    "多吃滋阴食物",
                    "早睡早起",
                ],
            },
            "处暑": {
                "name": "处暑养生",
                "description": "暑气渐消，润燥养肺",
                "recipes": [
                    "百合粥 - 润肺止咳",
                    "冰糖炖雪梨 - 清热润燥",
                    "蜂蜜水 - 润肠通便",
                ],
                "recommendations": [
                    "注意补水",
                    "避免秋燥",
                    "适当运动",
                ],
            },
            "白露": {
                "name": "白露养生",
                "description": "天气转凉，防秋燥",
                "recipes": [
                    "山药排骨汤 - 健脾润肺",
                    "桂花糯米藕 - 健脾开胃",
                    "杏仁茶 - 润肺止咳",
                ],
                "recommendations": [
                    "早晚添衣",
                    "多吃润燥食物",
                    "预防感冒",
                ],
            },
            "秋分": {
                "name": "秋分养生",
                "description": "阴阳平衡，润燥为主",
                "recipes": [
                    "秋梨膏 - 润肺止咳",
                    "核桃粥 - 补肾润肠",
                    "石榴汁 - 生津止渴",
                ],
                "recommendations": [
                    "保持情绪稳定",
                    "饮食宜滋润",
                    "适当秋冻",
                ],
            },
            "寒露": {
                "name": "寒露养生",
                "description": "寒露渐冷，防寒润燥",
                "recipes": [
                    "栗子炖鸡 - 补肾健脾",
                    "红枣桂圆茶 - 补血养颜",
                    "花生猪脚汤 - 滋阴润燥",
                ],
                "recommendations": [
                    "注意保暖",
                    "多吃温补食物",
                    "预防呼吸道疾病",
                ],
            },
            "霜降": {
                "name": "霜降养生",
                "description": "霜降时节，注意保暖",
                "recipes": [
                    "羊肉汤 - 温补驱寒",
                    "姜母鸭 - 温中散寒",
                    "枸杞炖牛肉 - 补肾壮阳",
                ],
                "recommendations": [
                    "防寒保暖",
                    "多吃温性食物",
                    "适当进补",
                ],
            },
            "立冬": {
                "name": "立冬养生",
                "description": "冬季开始，补肾藏精",
                "recipes": [
                    "当归生姜羊肉汤 - 温补气血",
                    "黑芝麻糊 - 补肾乌发",
                    "核桃炖猪腰 - 补肾强腰",
                ],
                "recommendations": [
                    "早睡晚起",
                    "注意保暖",
                    "适当进补",
                ],
            },
            "小雪": {
                "name": "小雪养生",
                "description": "小雪时节，温补为宜",
                "recipes": [
                    "红枣枸杞茶 - 补气养血",
                    "桂圆糯米粥 - 暖胃补心",
                    "炖牛腩 - 温补强身",
                ],
                "recommendations": [
                    "防寒防冻",
                    "保持心情愉快",
                    "适度运动",
                ],
            },
            "大雪": {
                "name": "大雪养生",
                "description": "大雪封河，重在温补",
                "recipes": [
                    "人参鸡汤 - 大补元气",
                    "阿胶糕 - 补血养颜",
                    "鹿茸炖汤 - 补肾壮阳",
                ],
                "recommendations": [
                    "注意头部保暖",
                    "多吃温补食物",
                    "避免过度劳累",
                ],
            },
            "冬至": {
                "name": "冬至养生",
                "description": "冬至阳生，滋阴助阳",
                "recipes": [
                    "饺子 - 寓意团圆",
                    "汤圆 - 象征圆满",
                    "八宝饭 - 滋补养生",
                ],
                "recommendations": [
                    "固本培元",
                    "适当进补",
                    "保持室内温暖",
                ],
            },
            "小寒": {
                "name": "小寒养生",
                "description": "小寒冷极，温补御寒",
                "recipes": [
                    "腊八粥 - 温补脾胃",
                    "红烧肉 - 补充能量",
                    "姜糖水 - 驱寒暖身",
                ],
                "recommendations": [
                    "注意防寒",
                    "多吃高热量食物",
                    "适度运动",
                ],
            },
            "大寒": {
                "name": "大寒养生",
                "description": "一年最冷，补肾防寒",
                "recipes": [
                    "火锅 - 驱寒温补",
                    "药膳炖汤 - 滋补强身",
                    "红糖姜茶 - 暖身驱寒",
                ],
                "recommendations": [
                    "注意保暖",
                    "适当进补",
                    "预防感冒",
                ],
            },
        }

    def calculate_julian_day(self, year: int, month: int, day: int) -> float:
        if month <= 2:
            year -= 1
            month += 12
        a = year // 100
        b = 2 - a + a // 4
        return (
            math.floor(365.25 * (year + 4716))
            + math.floor(30.6001 * (month + 1))
            + day
            + b
            - 1524.5
        )

    def calculate_solar_longitude(self, jd: float) -> float:
        T = (jd - 2451545.0) / 36525.0
        L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T * T
        M = (
            357.52910
            + 35999.05030 * T
            - 0.0001559 * T * T
            - 0.00000048 * T * T * T
        )
        e = 0.016708617 - 0.000042037 * T - 0.0000001236 * T * T
        C = (
            (1.914600 - 0.004817 * T - 0.000014 * T * T)
            * math.sin(math.radians(M))
            + (0.019993 - 0.000101 * T) * math.sin(math.radians(2 * M))
            + 0.000290 * math.sin(math.radians(3 * M))
        )
        true_longitude = L0 + C
        omega = 125.04 - 1934.136 * T
        delta_psi = -0.004778 * math.sin(math.radians(omega))
        epsilon = (
            23.43929111
            - 0.0130041667 * T
            - 0.0000001639 * T * T
            + 0.0000005036 * T * T * T
        )
        corrected_longitude = true_longitude + delta_psi - 0.00569
        corrected_longitude = corrected_longitude % 360
        if corrected_longitude < 0:
            corrected_longitude += 360
        return corrected_longitude

    def get_solar_term(self, date_str: str) -> Optional[str]:
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            jd = self.calculate_julian_day(date_obj.year, date_obj.month, date_obj.day)
            solar_longitude = self.calculate_solar_longitude(jd)
            for term, longitude in self.solar_terms.items():
                diff = abs(solar_longitude - longitude)
                diff = min(diff, 360 - diff)
                if diff < 7.5:
                    return term
            closest_term = None
            min_diff = 360
            for term, longitude in self.solar_terms.items():
                diff = abs(solar_longitude - longitude)
                diff = min(diff, 360 - diff)
                if diff < min_diff:
                    min_diff = diff
                    closest_term = term
            return closest_term
        except ValueError:
            return None

    def get_recommendation(self, solar_term: str) -> Dict:
        if solar_term in self.recipes_db:
            return self.recipes_db[solar_term]
        return {
            "name": "养生建议",
            "description": "根据季节调整饮食",
            "recipes": [
                "多吃时令蔬菜水果",
                "保持饮食均衡",
                "适量运动，保证睡眠",
            ],
            "recommendations": [
                "注意饮食卫生",
                "保持心情愉快",
                "规律作息",
            ],
        }

    def _initialize_english_recipes(self) -> Dict[str, Dict]:
        return {
            '立春': {'name': 'Beginning of Spring Wellness', 'description': 'Spring begins with rising yang energy, focus on ascending nourishment',
                'recipes': ['Stir-fried Chives with Eggs - Boosts yang energy', 'Bamboo Shoot Chicken Soup - Replenishes vitality', 'Goji Berry Congee - Nourishes liver and eyes'],
                'recommendations': ['Eat more pungent and sweet dispersing foods', 'Reduce sour foods', 'Keep warm, guard against late spring cold']},
            '雨水': {'name': 'Rain Water Wellness', 'description': 'Rain Water season, humidity increases',
                'recipes': ['Yam and Job\'s Tears Congee - Strengthens spleen, removes dampness', 'Crucian Carp Soup - Reduces water retention', 'Red Date Lotus Seed Soup - Calms heart and mind'],
                'recommendations': ['Guard against moisture and humidity', 'Eat more spleen-strengthening foods', 'Exercise appropriately to dispel dampness']},
            '惊蛰': {'name': 'Awakening of Insects Wellness', 'description': 'Spring thunder awakens insects, nourish liver and yang',
                'recipes': ['Pear Water - Moistens lungs, stops cough', 'Shepherd\'s Purse Tofu Soup - Clears heat, nourishes liver', 'Chive Shrimp - Boosts yang energy'],
                'recommendations': ['Eat light foods', 'Early to bed and rise for liver health', 'Guard against spring drowsiness']},
            '春分': {'name': 'Spring Equinox Wellness', 'description': 'Balance of yin and yang, focus on harmony',
                'recipes': ['Spring Vegetables with Pork - Balances yin and yang', 'Toon Tofu Salad - Clears heat, strengthens stomach', 'Shepherd\'s Purse Dumplings - Calms liver and stomach'],
                'recommendations': ['Diet should balance cold and hot', 'Maintain emotional stability', 'Moderate outdoor exercise']},
            '清明': {'name': 'Pure Brightness Wellness', 'description': 'Pure Brightness season, focus on liver nourishment',
                'recipes': ['Mugwort Rice Balls - Dispels dampness and cold', 'Spinach Pork Liver Soup - Nourishes blood and liver', 'Chrysanthemum Goji Tea - Clears liver, brightens eyes'],
                'recommendations': ['Maintain a cheerful mood', 'Eat more green vegetables', 'Early to bed and rise for liver health']},
            '谷雨': {'name': 'Grain Rain Wellness', 'description': 'Rain nourishes grains, strengthen spleen, remove dampness',
                'recipes': ['Corn Silk Tea - Diuretic, removes dampness', 'Poria Congee - Strengthens spleen, calms spirit', 'Celery Lily Stir-fry - Clears heat, calms liver'],
                'recommendations': ['Guard against dampness invasion', 'Eat dampness-removing foods appropriately', 'Avoid sitting on damp ground']},
            '立夏': {'name': 'Beginning of Summer Wellness', 'description': 'Summer begins, focus on heart nourishment',
                'recipes': ['Lotus Leaf Congee - Clears heat, relieves summer heat', 'Bitter Melon Salad - Clears heart fire', 'Mung Bean Soup - Clears heat, detoxifies'],
                'recommendations': ['Maintain a happy mood', 'Rest appropriately at noon', 'Eat more red foods for heart health']},
            '小满': {'name': 'Grain Buds Wellness', 'description': 'Grain Buds season, clear heat and dampness',
                'recipes': ['Winter Melon Soup - Reduces water retention', 'Cucumber Jellyfish Salad - Clears heat, relieves summer heat', 'Job\'s Tears Red Bean Congee - Strengthens spleen, removes dampness'],
                'recommendations': ['Guard against heat', 'Avoid excessive cold foods', 'Keep skin clean']},
            '芒种': {'name': 'Grain in Ear Wellness', 'description': 'Plum rain season, guard against dampness and heat',
                'recipes': ['Sour Plum Drink - Generates fluids, quenches thirst', 'Ginger Tea - Dispels cold and dampness', 'Perilla Fried River Snails - Releases exterior cold'],
                'recommendations': ['Guard against mold and humidity', 'Diet should be light', 'Nap appropriately to nourish heart']},
            '夏至': {'name': 'Summer Solstice Wellness', 'description': 'Peak yang energy, focus on yin nourishment',
                'recipes': ['Cold Noodles - Clears heat, stimulates appetite', 'Tomato Egg Soup - Generates fluids, quenches thirst', 'Watermelon Rind Stir-fry - Clears heat, diuretic'],
                'recommendations': ['Guard against heat', 'Nap appropriately', 'Drink plenty of water']},
            '小暑': {'name': 'Minor Heat Wellness', 'description': 'Minor Heat is hot, guard against heat',
                'recipes': ['Lotus Seed Soup - Clears heart, calms spirit', 'Loofah Soup - Clears heat, cools blood', 'Mint Tea - Cool and refreshing'],
                'recommendations': ['Avoid intense sun exposure', 'Diet should be light', 'Maintain adequate sleep']},
            '大暑': {'name': 'Major Heat Wellness', 'description': 'Hottest time of year, focus on clearing heat',
                'recipes': ['Winter Melon Old Duck Soup - Clears heat, nourishes', 'Mung Bean Lily Congee - Clears heat, calms spirit', 'Cucumber Salad - Clears heat, quenches thirst'],
                'recommendations': ['Guard against heat stroke', 'Drink warm water', 'Avoid excessive sweating']},
            '立秋': {'name': 'Beginning of Autumn Wellness', 'description': 'Autumn begins, nourish yin and moisten dryness',
                'recipes': ['Tremella Lotus Seed Soup - Nourishes yin, moistens lungs', 'Pear Syrup - Moistens lungs, stops cough', 'Sesame Paste - Nourishes yin, moistens dryness'],
                'recommendations': ['Reduce spicy foods', 'Eat more yin-nourishing foods', 'Early to bed and rise']},
            '处暑': {'name': 'End of Heat Wellness', 'description': 'Heat dissipates, moisten dryness, nourish lungs',
                'recipes': ['Lily Congee - Moistens lungs, stops cough', 'Rock Sugar Pear Stew - Clears heat, moistens dryness', 'Honey Water - Moistens intestines, promotes bowel movement'],
                'recommendations': ['Stay hydrated', 'Avoid autumn dryness', 'Exercise appropriately']},
            '白露': {'name': 'White Dew Wellness', 'description': 'Weather cools, guard against autumn dryness',
                'recipes': ['Yam Pork Rib Soup - Strengthens spleen, moistens lungs', 'Osmanthus Glutinous Rice Lotus Root - Strengthens spleen, stimulates appetite', 'Almond Tea - Moistens lungs, stops cough'],
                'recommendations': ['Add clothing in morning and evening', 'Eat more dryness-moistening foods', 'Prevent colds']},
            '秋分': {'name': 'Autumn Equinox Wellness', 'description': 'Balance of yin and yang, focus on moistening dryness',
                'recipes': ['Autumn Pear Paste - Moistens lungs, stops cough', 'Walnut Congee - Nourishes kidneys, moistens intestines', 'Pomegranate Juice - Generates fluids, quenches thirst'],
                'recommendations': ['Maintain emotional stability', 'Diet should be moistening', 'Allow appropriate autumn chill']},
            '寒露': {'name': 'Cold Dew Wellness', 'description': 'Cold Dew turns cold, guard against cold and dryness',
                'recipes': ['Chestnut Stewed Chicken - Nourishes kidneys, strengthens spleen', 'Red Date Longan Tea - Nourishes blood, beautifies skin', 'Peanut Pig\'s Feet Soup - Nourishes yin, moistens dryness'],
                'recommendations': ['Keep warm', 'Eat more warming foods', 'Prevent respiratory diseases']},
            '霜降': {'name': 'Frost\'s Descent Wellness', 'description': 'Frost\'s Descent season, keep warm',
                'recipes': ['Mutton Soup - Warms and dispels cold', 'Ginger Duck - Warms center, dispels cold', 'Goji Beef Stew - Nourishes kidneys, boosts yang'],
                'recommendations': ['Guard against cold', 'Eat more warming foods', 'Supplement appropriately']},
            '立冬': {'name': 'Beginning of Winter Wellness', 'description': 'Winter begins, nourish kidneys and store essence',
                'recipes': ['Angelica Ginger Mutton Soup - Warms and nourishes qi and blood', 'Black Sesame Paste - Nourishes kidneys, darkens hair', 'Walnut Pig Kidney Stew - Nourishes kidneys, strengthens waist'],
                'recommendations': ['Early to bed, late to rise', 'Keep warm', 'Supplement appropriately']},
            '小雪': {'name': 'Minor Snow Wellness', 'description': 'Minor Snow season, warming supplements appropriate',
                'recipes': ['Red Date Goji Tea - Nourishes qi and blood', 'Longan Glutinous Rice Congee - Warms stomach, nourishes heart', 'Stewed Beef Brisket - Warms and strengthens body'],
                'recommendations': ['Guard against cold and frost', 'Maintain a happy mood', 'Exercise moderately']},
            '大雪': {'name': 'Major Snow Wellness', 'description': 'Major Snow freezes rivers, focus on warming supplements',
                'recipes': ['Ginseng Chicken Soup - Greatly supplements primordial qi', 'Ejiao Cake - Nourishes blood, beautifies skin', 'Deer Antler Stew - Nourishes kidneys, boosts yang'],
                'recommendations': ['Keep head warm', 'Eat more warming foods', 'Avoid overexertion']},
            '冬至': {'name': 'Winter Solstice Wellness', 'description': 'Winter Solstice yang rises, nourish yin and assist yang',
                'recipes': ['Dumplings - Symbolizes reunion', 'Tangyuan - Symbolizes completeness', 'Eight Treasure Rice - Nourishing and healthful'],
                'recommendations': ['Consolidate foundation and cultivate vitality', 'Supplement appropriately', 'Keep indoor warm']},
            '小寒': {'name': 'Minor Cold Wellness', 'description': 'Minor Cold is extremely cold, warm and guard against cold',
                'recipes': ['Laba Congee - Warms and nourishes spleen and stomach', 'Braised Pork - Replenishes energy', 'Ginger Brown Sugar Tea - Dispels cold, warms body'],
                'recommendations': ['Guard against cold', 'Eat more high-calorie foods', 'Exercise moderately']},
            '大寒': {'name': 'Major Cold Wellness', 'description': 'Coldest time of year, nourish kidneys and guard against cold',
                'recipes': ['Hot Pot - Dispels cold, warms and supplements', 'Medicinal Stew - Nourishes and strengthens body', 'Brown Sugar Ginger Tea - Warms body, dispels cold'],
                'recommendations': ['Keep warm', 'Supplement appropriately', 'Prevent colds']}
        }

    def to_english(self, solar_term: str, recommendation: Dict) -> Dict:
        """Return fully translated English version of the recommendation."""
        term_map = {
            '立春': 'Beginning of Spring',
            '雨水': 'Rain Water',
            '惊蛰': 'Awakening of Insects',
            '春分': 'Spring Equinox',
            '清明': 'Pure Brightness',
            '谷雨': 'Grain Rain',
            '立夏': 'Beginning of Summer',
            '小满': 'Grain Buds',
            '芒种': 'Grain in Ear',
            '夏至': 'Summer Solstice',
            '小暑': 'Minor Heat',
            '大暑': 'Major Heat',
            '立秋': 'Beginning of Autumn',
            '处暑': 'End of Heat',
            '白露': 'White Dew',
            '秋分': 'Autumn Equinox',
            '寒露': 'Cold Dew',
            '霜降': 'Frost\'s Descent',
            '立冬': 'Beginning of Winter',
            '小雪': 'Minor Snow',
            '大雪': 'Major Snow',
            '冬至': 'Winter Solstice',
            '小寒': 'Minor Cold',
            '大寒': 'Major Cold',
        }

        # Use the pre-translated English recipes database
        english_recipes = self._initialize_english_recipes()
        english_version = english_recipes.get(solar_term, {
            "name": "Seasonal Wellness",
            "description": "Adjust diet according to the season",
            "recipes": [
                "Eat more seasonal vegetables and fruits",
                "Maintain a balanced diet",
                "Exercise appropriately and ensure adequate sleep",
            ],
            "recommendations": [
                "Pay attention to food hygiene",
                "Maintain a pleasant mood",
                "Keep a regular routine",
            ],
        })

        return {
            "solar_term": term_map.get(solar_term, solar_term),
            "name": english_version["name"],
            "description": english_version["description"],
            "recipes": english_version["recipes"],
            "recommendations": english_version["recommendations"],
        }
