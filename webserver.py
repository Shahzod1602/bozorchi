import re
import os
from aiohttp import web
import json
from database import get_user_profile, get_last_shopping_list, update_family_size, update_weekly_budget, update_language, update_preferences
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

        if ' - ' in line_clean:
            name_part = line_clean.split(' - ')[0]
        elif ' — ' in line_clean:
            name_part = line_clean.split(' — ')[0]
        elif ':' in line_clean:
            name_part = line_clean.split(':')[0]
        else:
            name_part = line_clean.split('~')[0] if '~' in line_clean else line_clean

        name_part = clean_markdown(name_part).strip()
        key = name_part.lower()
        if name_part and len(name_part) > 1 and key not in seen:
            seen.add(key)
            ingredients.append({"name": name_part, "price": price})

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
    if not user_id:
        return web.json_response({"error": "no user_id"}, status=400)
    try:
        profile = await get_user_profile(int(user_id))
        text = await get_weekly_plan(profile['family_size'], profile['language'], profile.get('preferences', []))
        ingredients = parse_ingredients(text)
        return web.json_response({"text": text, "ingredients": ingredients})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


@routes.post('/api/budget-plan')
async def api_budget_plan(request):
    data = await request.json()
    user_id = data.get('user_id')
    budget = data.get('budget')
    if not user_id or not budget:
        return web.json_response({"error": "missing fields"}, status=400)
    try:
        profile = await get_user_profile(int(user_id))
        await update_weekly_budget(int(user_id), float(budget))
        text = await get_budget_weekly_plan(float(budget), profile['family_size'], profile['language'], profile.get('preferences', []))
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


async def start_webserver(port: int = 8090):
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server: http://localhost:{port}")
    return runner
