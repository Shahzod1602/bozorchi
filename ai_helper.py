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
}

CHEF_ROLE = {
    "uz": "Sen o'zbek oshpaz assistantisan.",
    "ru": "Ты узбекский кулинарный ассистент.",
}

PREF_LABELS = {
    "vegetarian": {"uz": "vegetarian (go'sht yemaydi)", "ru": "вегетарианец (без мяса)"},
    "no_gluten": {"uz": "glutensiz (xamirli ovqat yemaydi)", "ru": "без глютена (не ест мучное)"},
    "no_pork": {"uz": "cho'chqa go'shti yemaydi", "ru": "не ест свинину"},
    "no_dairy": {"uz": "sut mahsulotlari yemaydi", "ru": "без молочных продуктов"},
    "diabetic": {"uz": "qandli diabet (shakarli ovqat yemaydi)", "ru": "диабет (без сахара)"},
    "low_calorie": {"uz": "kaloriyasi kam ovqat", "ru": "низкокалорийное питание"},
    "halal": {"uz": "faqat halol mahsulotlar", "ru": "только халяль продукты"},
    "no_spicy": {"uz": "achchiq ovqat yemaydi", "ru": "без острого"},
}


def build_pref_text(preferences: list, lang: str) -> str:
    if not preferences:
        return ""
    items = []
    for p in preferences:
        if p in PREF_LABELS:
            items.append(PREF_LABELS[p][lang])
        else:
            items.append(p)  # custom preference
    if lang == "uz":
        return f"\n⚠️ MUHIM CHEKLOVLAR (ALBATTA HISOBGA OL):\n" + "\n".join(f"  - {i}" for i in items) + "\n"
    else:
        return f"\n⚠️ ВАЖНЫЕ ОГРАНИЧЕНИЯ (ОБЯЗАТЕЛЬНО УЧТИ):\n" + "\n".join(f"  - {i}" for i in items) + "\n"


async def get_meal_suggestion(preferences: str, family_size: int, lang: str = "uz", user_prefs: list = None) -> dict:
    prices = get_price_reference()
    pref_text = build_pref_text(user_prefs or [], lang)
    prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Foydalanuvchi:
- Oila: {family_size} kishi
- Istak: {preferences}
{pref_text}
{prices}

Yuqoridagi REAL narxlardan foydalanib javob ber:

🍽️ TAVSIYA ETILGAN OVQAT: [ovqat nomi]

📝 RETSEPT:
[5-7 qadam]

🛒 MASALLIQLAR ({family_size} kishi uchun):
- [masalliq]: [miqdor] — ~[narx] so'm

💰 TAXMINIY NARX: ~[jami] so'm
⏱️ VAQT: [vaqt]
💡 MASLAHAT: [maslahat]""" if lang == "uz" else f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Пользователь:
- Семья: {family_size} человек
- Пожелание: {preferences}
{pref_text}
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

    response = client.models.generate_content(model=MODEL, contents=prompt)
    response_text = response.text

    meal_name = ""
    markers = ["TAVSIYA ETILGAN OVQAT:", "РЕКОМЕНДУЕМОЕ БЛЮДО:"]
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
    else:
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

    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


async def get_budget_weekly_plan(budget: float, family_size: int, lang: str = "uz", user_prefs: list = None) -> str:
    daily_budget = budget / 7
    prices = get_price_reference()
    pref_text = build_pref_text(user_prefs or [], lang)
    if lang == "uz":
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

{family_size} kishilik oila, haftalik byudjet: {budget:,.0f} so'm (kuniga ~{daily_budget:,.0f} so'm).
{pref_text}
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
    else:
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Семья {family_size} человек, недельный бюджет: {budget:,.0f} сум (в день ~{daily_budget:,.0f} сум).
{pref_text}
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

    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


async def get_weekly_plan(family_size: int, lang: str = "uz", user_prefs: list = None) -> str:
    pref_text = build_pref_text(user_prefs or [], lang)
    if lang == "uz":
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

{family_size} kishilik oila uchun 7 kunlik ovqat rejasi. O'zbek taomlarini ko'proq qo'sh.
{pref_text}

📅 HAFTALIK OVQAT REJASI ({family_size} kishi)

DUSHANBA:
☀️ Nonushta: [ovqat]
🌞 Tushlik: [ovqat]
🌙 Kechki: [ovqat]

[Qolgan kunlar ham]

🛒 UMUMIY MASALLIQLAR: [ro'yxat]"""
    else:
        prompt = f"""{CHEF_ROLE[lang]} {LANG_INSTRUCTION[lang]}

Меню на 7 дней для семьи {family_size} человек. Больше узбекских блюд.
{pref_text}

📅 НЕДЕЛЬНОЕ МЕНЮ ({family_size} человек)

ПОНЕДЕЛЬНИК:
☀️ Завтрак: [блюдо]
🌞 Обед: [блюдо]
🌙 Ужин: [блюдо]

[Остальные дни аналогично]

🛒 ОБЩИЙ СПИСОК ПРОДУКТОВ: [список]"""

    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text
