import re
import os
import time
import aiohttp as aiohttp_client
from aiohttp import web
import json
from database import get_user_profile, get_last_shopping_list, update_family_size, update_weekly_budget, update_language, update_preferences
from catalog import search_products, get_all_products, get_categories, get_by_category
from ai_helper import get_meal_suggestion, get_recipe_by_name, get_weekly_plan, get_budget_weekly_plan

routes = web.RouteTableDef()
WEBAPP_DIR = os.path.join(os.path.dirname(__file__), "webapp")


def clean_markdown(text: str) -> str:
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'_+', '', text)
    return text.strip()


SECTION_KEYWORDS = ['МАСАЛЛИҚ', 'MASALLIQ', 'ПРОДУКТ', 'СПИСОК ПОКУПОК', 'ПОКУПОК НА НЕДЕЛЮ',
                    "BOZORLIK RO'YXATI", 'HAFTALIK BOZORLIK', 'UMUMIY MASALLIQ']

def parse_ingredients(text: str) -> list:
    lines = text.split('\n')

    # Find the LAST shopping list section header to avoid duplicates
    last_idx = -1
    for i, line in enumerate(lines):
        lu = line.strip().upper()
        if any(kw in lu for kw in SECTION_KEYWORDS):
            last_idx = i

    if last_idx == -1:
        return []

    ingredients = []
    seen = set()

    for line in lines[last_idx + 1:]:
        line = line.strip()
        if not line:
            continue
        # Stop at summary/tip/separator lines
        if re.match(r'^[💰⏱️💡━📅📝🍽️💚]', line):
            break
        if not re.match(r'^[\*\-]\s+', line):
            continue

        line_clean = re.sub(r'^[\*\-]\s+', '', line)
        line_clean = clean_markdown(line_clean)

        price_match = re.search(r'[~≈]?\s*[\d\s,]+\s*(so\'?m|сум|sum)', line_clean, re.IGNORECASE)
        price = price_match.group(0).strip() if price_match else ''

        # Split left side (before price dash) into name and qty
        if ' - ' in line_clean:
            left = line_clean.split(' - ')[0]
        elif ' — ' in line_clean:
            left = line_clean.split(' — ')[0]
        elif ':' in line_clean:
            left = line_clean  # handle below
        else:
            left = line_clean.split('~')[0] if '~' in line_clean else line_clean

        left = clean_markdown(left).strip()

        # Separate "Name: qty" → name, qty
        if ':' in left:
            parts = left.split(':', 1)
            name_part = parts[0].strip()
            qty_part = parts[1].strip()
        else:
            name_part = left
            qty_part = ''

        key = name_part.lower()
        if name_part and len(name_part) > 1 and key not in seen:
            seen.add(key)
            ingredients.append({"name": name_part, "qty": qty_part, "price": price})

    return ingredients


@routes.get('/')
async def index(request):
    return web.FileResponse(os.path.join(WEBAPP_DIR, 'index.html'))


@routes.get('/api/profile')
async def get_profile(request):
    user_id = request.rel_url.query.get('user_id')
    if not user_id:
        return web.json_response({"error": "no user_id"}, status=400)
    try:
        profile = await get_user_profile(int(user_id))
        last = await get_last_shopping_list(int(user_id))
        ingredients = parse_ingredients(last[1]) if last else []
        return web.json_response({
            **profile,
            "meal_name": last[0] if last else "",
            "ingredients": ingredients,
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/profile')
async def save_profile(request):
    data = await request.json()
    user_id = data.get('user_id')
    if not user_id:
        return web.json_response({"error": "no user_id"}, status=400)
    try:
        if 'family_size' in data:
            await update_family_size(int(user_id), int(data['family_size']))
        if 'weekly_budget' in data:
            await update_weekly_budget(int(user_id), float(data['weekly_budget']))
        if 'language' in data:
            await update_language(int(user_id), data['language'])
        if 'preferences' in data:
            await update_preferences(int(user_id), json.dumps(data['preferences']))
        return web.json_response({"ok": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/suggest')
async def api_suggest(request):
    data = await request.json()
    user_id = data.get('user_id')
    preference = data.get('preference', '')
    fridge_items = data.get('fridge_items', [])
    if not user_id or not preference:
        return web.json_response({"error": "missing fields"}, status=400)
    try:
        profile = await get_user_profile(int(user_id))
        result = await get_meal_suggestion(
            preference, profile['family_size'], profile['language'],
            profile.get('preferences', []), fridge_items
        )
        ingredients = parse_ingredients(result['full_response'])
        from database import save_shopping_list
        await save_shopping_list(int(user_id), result['meal_name'], result['full_response'], result['full_response'])
        return web.json_response({
            "text": result['full_response'],
            "meal_name": result['meal_name'],
            "ingredients": ingredients,
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/recipe')
async def api_recipe(request):
    data = await request.json()
    user_id = data.get('user_id')
    meal_name = data.get('meal_name', '')
    if not user_id or not meal_name:
        return web.json_response({"error": "missing fields"}, status=400)
    try:
        profile = await get_user_profile(int(user_id))
        text = await get_recipe_by_name(meal_name, profile['family_size'], profile['language'])
        ingredients = parse_ingredients(text)
        return web.json_response({"text": text, "ingredients": ingredients})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/weekly-plan')
async def api_weekly_plan(request):
    data = await request.json()
    user_id = data.get('user_id')
    wish = data.get('wish', '')
    if not user_id:
        return web.json_response({"error": "no user_id"}, status=400)
    try:
        profile = await get_user_profile(int(user_id))
        text = await get_weekly_plan(profile['family_size'], profile['language'], profile.get('preferences', []), wish)
        ingredients = parse_ingredients(text)
        return web.json_response({"text": text, "ingredients": ingredients})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/budget-plan')
async def api_budget_plan(request):
    data = await request.json()
    user_id = data.get('user_id')
    budget = data.get('budget')
    wish = data.get('wish', '')
    if not user_id or not budget:
        return web.json_response({"error": "missing fields"}, status=400)
    try:
        profile = await get_user_profile(int(user_id))
        await update_weekly_budget(int(user_id), float(budget))
        text = await get_budget_weekly_plan(float(budget), profile['family_size'], profile['language'], profile.get('preferences', []), wish)
        ingredients = parse_ingredients(text)
        return web.json_response({"text": text, "ingredients": ingredients})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/save-plan')
async def api_save_plan(request):
    data = await request.json()
    user_id = data.get('user_id')
    meal_name = data.get('meal_name', '')
    plan_text = data.get('plan_text', '')
    if not user_id or not plan_text:
        return web.json_response({"error": "missing fields"}, status=400)
    try:
        from database import save_shopping_list
        await save_shopping_list(int(user_id), meal_name, plan_text, plan_text)
        return web.json_response({"ok": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.get('/api/products')
async def api_products(request):
    q = request.rel_url.query.get('q', '').strip()
    category = request.rel_url.query.get('category', '').strip()
    if q:
        results = search_products(q, limit=20)
    elif category:
        results = get_by_category(category)
    else:
        results = get_all_products()
    return web.json_response(results)


@routes.get('/api/categories')
async def api_categories(request):
    return web.json_response(get_categories())


_krz_cache = {"data": None, "ts": 0}
CACHE_TTL = 1800  # 30 min

@routes.get('/api/korzinka-products')
async def api_korzinka_products(request):
    global _krz_cache
    now = time.time()
    if _krz_cache["data"] and now - _krz_cache["ts"] < CACHE_TTL:
        return web.json_response(_krz_cache["data"])
    try:
        async with aiohttp_client.ClientSession() as session:
            async with session.get(
                "https://catalog.korzinka.uz/api/catalogs/categories/",
                headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
                timeout=aiohttp_client.ClientTimeout(total=10)
            ) as resp:
                raw = await resp.json(content_type=None)
        categories = raw.get("data", raw) if isinstance(raw, dict) else raw
        result = []
        for cat in categories:
            cat_name_uz = cat.get("title_uz") or cat.get("title_ru", "")
            cat_name_ru = cat.get("title_ru", "")
            for p in cat.get("products", []):
                prices = p.get("prices", {}) or {}
                result.append({
                    "id": p.get("id"),
                    "name_uz": p.get("title_uz") or p.get("title_ru", ""),
                    "name_ru": p.get("title_ru", ""),
                    "price": prices.get("actual_price", ""),
                    "old_price": prices.get("old_price", ""),
                    "discount": prices.get("price_tag_name", ""),
                    "unit": p.get("weight_param", ""),
                    "image": p.get("small_image_url", ""),
                    "category_uz": cat_name_uz,
                    "category_ru": cat_name_ru,
                })
        _krz_cache = {"data": result, "ts": now}
        return web.json_response(result)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def start_webserver(port: int = 8090):
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server: http://localhost:{port}")
    return runner
