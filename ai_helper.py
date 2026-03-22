import os
from google import genai
from dotenv import load_dotenv
from prices import get_price_reference

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.0-flash"

LANG_INSTRUCTION = {
    "uz": "Faqat O'ZBEK tilida javob ber.",
    "ru": "Отвечай ТОЛЬКО на РУССКОМ языке.",
    "en": "Reply ONLY in ENGLISH.",
}

CHEF_ROLE = {
    "uz": "Sen o'zbek oshpaz assistantisan.",
    "ru": "Ты узбекский кулинарный ассистент.",
    "en": "You are an Uzbek culinary assistant.",
}

PREF_LABELS = {
    "vegetarian": {"uz": "vegetarian (go'sht yemaydi)", "ru": "вегетарианец (без мяса)", "en": "vegetarian (no meat)"},
    "no_gluten": {"uz": "glutensiz (xamirli ovqat yemaydi)", "ru": "без глютена (не ест мучное)", "en": "gluten-free"},
    "no_dairy": {"uz": "sut mahsulotlari yemaydi", "ru": "без молочных продуктов", "en": "no dairy products"},
    "diabetic": {"uz": "qandli diabet (shakarli ovqat yemaydi)", "ru": "диабет (без сахара)", "en": "diabetic (no sugar)"},
    "low_calorie": {"uz": "kaloriyasi kam ovqat", "ru": "низкокалорийное питание", "en": "low-calorie diet"},
    "halal": {"uz": "faqat halol mahsulotlar", "ru": "только халяль продукты", "en": "halal only"},
    "no_spicy": {"uz": "achchiq ovqat yemaydi", "ru": "без острого", "en": "no spicy food"},
}


def build_pref_text(preferences: list, lang: str) -> str:
    if not preferences:
        return ""
    items = []
    for p in preferences:
        if p in PREF_LABELS:
            items.append(PREF_LABELS[p].get(lang, PREF_LABELS[p]["en"]))
        else:
            items.append(p)
    if lang == "uz":
        return f"\n⚠️ MUHIM CHEKLOVLAR (ALBATTA HISOBGA OL):\n" + "\n".join(f"  - {i}" for i in items) + "\n"
    elif lang == "ru":
        return f"\n⚠️ ВАЖНЫЕ ОГРАНИЧЕНИЯ (ОБЯЗАТЕЛЬНО УЧТИ):\n" + "\n".join(f"  - {i}" for i in items) + "\n"
    else:
        return f"\n⚠️ IMPORTANT RESTRICTIONS (MUST FOLLOW):\n" + "\n".join(f"  - {i}" for i in items) + "\n"


async def get_meal_suggestion(preferences: str, family_size: int, lang: str = "uz", user_prefs: list = None, fridge_items: list = None) -> dict:
    prices = get_price_reference()
    pref_text = build_pref_text(user_prefs or [], lang)

    fridge_text = ""
    if fridge_items:
        items_str = ", ".join(fridge_items)
        if lang == "uz":
            fridge_text = f"\n🧊 MUZLATGICHDAGI MAVJUD MAHSULOTLAR (albatta shu mahsulotlardan foydalanib tavsiya ber):\n{items_str}\n"
        elif lang == "ru":
            fridge_text = f"\n🧊 ПРОДУКТЫ В ХОЛОДИЛЬНИКЕ (обязательно используй эти продукты в рецепте):\n{items_str}\n"
        else:
            fridge_text = f"\n🧊 FRIDGE ITEMS (must use these in the recipe):\n{items_str}\n"

    if lang == "uz":
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Foydalanuvchi:
- Oila: {family_size} kishi
- Istak: {preferences}
{pref_text}{fridge_text}
{prices}

Yuqoridagi REAL narxlardan foydalanib javob ber:

🍽️ TAVSIYA ETILGAN OVQAT: [ovqat nomi]

📝 RETSEPT:
[5-7 qadam]

🛒 MASALLIQLAR ({family_size} kishi uchun):
- [masalliq]: [miqdor] — ~[narx] so'm

💰 TAXMINIY NARX: ~[jami] so'm
⏱️ VAQT: [vaqt]
💡 MASLAHAT: [maslahat]"""
    elif lang == "ru":
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Пользователь:
- Семья: {family_size} человек
- Пожелание: {preferences}
{pref_text}{fridge_text}
{prices}

Используй РЕАЛЬНЫЕ цены выше и отвечай:

🍽️ РЕКОМЕНДУЕМОЕ БЛЮДО: [название]

📝 РЕЦЕПТ:
[5-7 шагов]

🛒 ПРОДУКТЫ (на {family_size} человек):
- [продукт]: [количество] — ~[цена] сум

💰 ПРИМЕРНАЯ СТОИМОСТЬ: ~[итого] сум
⏱️ ВРЕМЯ: [время]
💡 СОВЕТ: [совет]"""
    else:
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

User:
- Family: {family_size} people
- Preference: {preferences}
{pref_text}{fridge_text}
{prices}

Use the REAL prices above and reply:

🍽️ SUGGESTED DISH: [dish name]

📝 RECIPE:
[5-7 steps]

🛒 INGREDIENTS (for {family_size} people):
- [ingredient]: [amount] — ~[price] sum

💰 ESTIMATED COST: ~[total] sum
⏱️ TIME: [time]
💡 TIP: [tip]"""

    response = client.models.generate_content(model=MODEL, contents=prompt)
    response_text = response.text

    meal_name = ""
    markers = ["TAVSIYA ETILGAN OVQAT:", "РЕКОМЕНДУЕМОЕ БЛЮДО:", "SUGGESTED DISH:"]
    for marker in markers:
        if marker in response_text:
            lines = [l for l in response_text.split('\n') if marker in l]
            if lines:
                meal_name = lines[0].split(marker)[-1].strip()
                break

    return {"full_response": response_text, "meal_name": meal_name}


async def get_recipe_by_name(meal_name: str, family_size: int, lang: str = "uz") -> str:
    prices = get_price_reference()
    if lang == "uz":
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

"{meal_name}" ovqati uchun {family_size} kishilik to'liq retsept.

{prices}

Format:
🍽️ {meal_name.upper()}

📝 RETSEPT:
[batafsil retsept]

🛒 MASALLIQLAR ({family_size} kishi uchun):
- [masalliq]: [miqdor] — ~[narx] so'm

💰 JAMI XARAJAT: ~[narx] so'm
⏱️ VAQT: [vaqt]
💡 MASLAHAT: [maslahat]"""
    elif lang == "ru":
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Полный рецепт блюда "{meal_name}" на {family_size} человек.

{prices}

Формат:
🍽️ {meal_name.upper()}

📝 РЕЦЕПТ:
[подробный рецепт]

🛒 ПРОДУКТЫ (на {family_size} человек):
- [продукт]: [количество] — ~[цена] сум

💰 ИТОГО: ~[цена] сум
⏱️ ВРЕМЯ: [время]
💡 СОВЕТ: [совет]"""
    else:
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Full recipe for "{meal_name}" for {family_size} people.

{prices}

Format:
🍽️ {meal_name.upper()}

📝 RECIPE:
[detailed recipe]

🛒 INGREDIENTS (for {family_size} people):
- [ingredient]: [amount] — ~[price] sum

💰 TOTAL COST: ~[price] sum
⏱️ TIME: [time]
💡 TIP: [tip]"""

    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


async def get_budget_weekly_plan(budget: float, family_size: int, lang: str = "uz", user_prefs: list = None, wish: str = "") -> str:
    daily_budget = budget / 7
    prices = get_price_reference()
    pref_text = build_pref_text(user_prefs or [], lang)
    if wish:
        if lang == "uz":
            wish_text = f"\n🗒️ Foydalanuvchi istagi: {wish}\n"
        elif lang == "ru":
            wish_text = f"\n🗒️ Пожелание пользователя: {wish}\n"
        else:
            wish_text = f"\n🗒️ User's wish: {wish}\n"
    else:
        wish_text = ""
    if lang == "uz":
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

{family_size} kishilik oila, haftalik byudjet: {budget:,.0f} so'm (kuniga ~{daily_budget:,.0f} so'm).
{pref_text}{wish_text}
{prices}

Yuqoridagi REAL narxlardan foydalanib byudjet doirasida 7 kunlik reja tuz:

💰 HAFTALIK BYUDJET REJASI
💵 Byudjet: {budget:,.0f} so'm | 👨‍👩‍👧‍👦 {family_size} kishi | 📅 7 kun
━━━━━━━━━━━━━━━━━━━━━━

📅 DUSHANBA (~{daily_budget:,.0f} so'm):
☀️ Nonushta: [ovqat] — [narx] so'm
🌞 Tushlik: [ovqat] — [narx] so'm
🌙 Kechki: [ovqat] — [narx] so'm
💸 Kun: [jami] so'm

[Qolgan 6 kun ham xuddi shunday]

━━━━━━━━━━━━━━━━━━━━━━
🛒 HAFTALIK BOZORLIK RO'YXATI:
- [masalliq]: [miqdor] — ~[narx] so'm

💰 JAMI: ~[narx] so'm
💚 TEJASH: ~[qolgan] so'm

💡 TEJAMKORLIK MASLAHATLARI:
1. [maslahat]
2. [maslahat]"""
    elif lang == "ru":
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Семья {family_size} человек, недельный бюджет: {budget:,.0f} сум (в день ~{daily_budget:,.0f} сум).
{pref_text}{wish_text}
{prices}

Используй РЕАЛЬНЫЕ цены и составь план на 7 дней в рамках бюджета:

💰 НЕДЕЛЬНЫЙ ПЛАН ПИТАНИЯ
💵 Бюджет: {budget:,.0f} сум | 👨‍👩‍👧‍👦 {family_size} чел. | 📅 7 дней
━━━━━━━━━━━━━━━━━━━━━━

📅 ПОНЕДЕЛЬНИК (~{daily_budget:,.0f} сум):
☀️ Завтрак: [блюдо] — [цена] сум
🌞 Обед: [блюдо] — [цена] сум
🌙 Ужин: [блюдо] — [цена] сум
💸 День: [итого] сум

[Остальные 6 дней аналогично]

━━━━━━━━━━━━━━━━━━━━━━
🛒 СПИСОК ПОКУПОК НА НЕДЕЛЮ:
- [продукт]: [количество] — ~[цена] сум

💰 ИТОГО: ~[цена] сум
💚 ЭКОНОМИЯ: ~[остаток] сум

💡 СОВЕТЫ ПО ЭКОНОМИИ:
1. [совет]
2. [совет]"""
    else:
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Family of {family_size}, weekly budget: {budget:,.0f} sum (~{daily_budget:,.0f} sum/day).
{pref_text}{wish_text}
{prices}

Use REAL prices and build a 7-day plan within budget:

💰 WEEKLY MEAL PLAN
💵 Budget: {budget:,.0f} sum | 👨‍👩‍👧‍👦 {family_size} people | 📅 7 days
━━━━━━━━━━━━━━━━━━━━━━

📅 MONDAY (~{daily_budget:,.0f} sum):
☀️ Breakfast: [dish] — [price] sum
🌞 Lunch: [dish] — [price] sum
🌙 Dinner: [dish] — [price] sum
💸 Day total: [total] sum

[Remaining 6 days similarly]

━━━━━━━━━━━━━━━━━━━━━━
🛒 WEEKLY SHOPPING LIST:
- [ingredient]: [amount] — ~[price] sum

💰 TOTAL: ~[price] sum
💚 SAVINGS: ~[remaining] sum

💡 MONEY-SAVING TIPS:
1. [tip]
2. [tip]"""

    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


async def get_weekly_plan(family_size: int, lang: str = "uz", user_prefs: list = None, wish: str = "") -> str:
    pref_text = build_pref_text(user_prefs or [], lang)
    if wish:
        if lang == "uz":
            wish_text = f"\n🗒️ Foydalanuvchi istagi: {wish}\n"
        elif lang == "ru":
            wish_text = f"\n🗒️ Пожелание пользователя: {wish}\n"
        else:
            wish_text = f"\n🗒️ User's wish: {wish}\n"
    else:
        wish_text = ""
    if lang == "uz":
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

{family_size} kishilik oila uchun 7 kunlik ovqat rejasi. O'zbek taomlarini ko'proq qo'sh.
{pref_text}{wish_text}

📅 HAFTALIK OVQAT REJASI ({family_size} kishi)

DUSHANBA:
☀️ Nonushta: [ovqat]
🌞 Tushlik: [ovqat]
🌙 Kechki: [ovqat]

[Qolgan kunlar ham]

🛒 UMUMIY MASALLIQLAR ({family_size} kishi, 7 kun):
- [masalliq]: [miqdor] — ~[narx] so'm

💰 TAXMINIY JAMI: ~[narx] so'm"""
    elif lang == "ru":
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Меню на 7 дней для семьи {family_size} человек. Больше узбекских блюд.
{pref_text}{wish_text}

📅 НЕДЕЛЬНОЕ МЕНЮ ({family_size} человек)

ПОНЕДЕЛЬНИК:
☀️ Завтрак: [блюдо]
🌞 Обед: [блюдо]
🌙 Ужин: [блюдо]

[Остальные дни аналогично]

🛒 ОБЩИЙ СПИСОК ПРОДУКТОВ ({family_size} чел., 7 дней):
- [продукт]: [количество] — ~[цена] сум

💰 ПРИМЕРНАЯ СТОИМОСТЬ: ~[цена] сум"""
    else:
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

7-day meal plan for a family of {family_size}. Include Uzbek dishes.
{pref_text}{wish_text}

📅 WEEKLY MENU ({family_size} people)

MONDAY:
☀️ Breakfast: [dish]
🌞 Lunch: [dish]
🌙 Dinner: [dish]

[Remaining days similarly]

🛒 FULL SHOPPING LIST ({family_size} people, 7 days):
- [ingredient]: [amount] — ~[price] sum

💰 ESTIMATED TOTAL: ~[price] sum"""

    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text
