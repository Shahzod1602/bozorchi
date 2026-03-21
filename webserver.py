import json
import re
import os
from aiohttp import web
from database import get_user_profile, get_last_shopping_list

routes = web.RouteTableDef()
WEBAPP_DIR = os.path.join(os.path.dirname(__file__), "webapp")


def parse_ingredients(text: str) -> list:
    """Shopping list textidan ingredientlarni ajratib olish"""
    ingredients = []
    in_section = False

    for line in text.split('\n'):
        line = line.strip()

        # Masalliqlar bo'limi boshlanishi
        if any(kw in line.upper() for kw in ['МАСАЛЛИҚ', 'MASALLIQ', 'ПРОДУКТ', 'СПИСОК', 'BOZORLIK']):
            in_section = True
            continue

        # Bo'lim tugashi
        if in_section and line.startswith(('💰', '⏱️', '💡', '━', '📅', '📝')):
            in_section = False

        if in_section and line.startswith('-'):
            # "- kartoshka: 1 kg — ~3,000 so'm" formatini parse qilish
            line_clean = line.lstrip('- ').strip()
            # Narxni ajratish
            price_match = re.search(r'[~≈]?\s*[\d,\s]+\s*(so\'?m|сум)', line_clean, re.IGNORECASE)
            price = price_match.group(0).strip() if price_match else ''

            # Nomni ajratish (narxdan oldingi qism)
            if '—' in line_clean:
                name_part = line_clean.split('—')[0].strip()
            elif '-' in line_clean[2:]:
                name_part = line_clean.rsplit('-', 1)[0].strip()
            else:
                name_part = line_clean.split('~')[0].strip() if '~' in line_clean else line_clean

            name_part = name_part.rstrip(':').strip()

            if name_part and len(name_part) > 1:
                ingredients.append({"name": name_part, "price": price})

    return ingredients


@routes.get('/')
async def index(request):
    return web.FileResponse(os.path.join(WEBAPP_DIR, 'index.html'))


@routes.get('/api/webapp')
async def webapp_api(request):
    user_id = request.rel_url.query.get('user_id')
    if not user_id:
        return web.json_response({"error": "no user_id"}, status=400)

    try:
        user_id = int(user_id)
    except ValueError:
        return web.json_response({"error": "invalid user_id"}, status=400)

    profile = await get_user_profile(user_id)
    last_list = await get_last_shopping_list(user_id)

    if not last_list:
        return web.json_response({"ingredients": [], "meal_name": "", "budget": 0, "family_size": 2})

    meal_name, ingredients_text = last_list
    ingredients = parse_ingredients(ingredients_text)

    return web.json_response({
        "meal_name": meal_name,
        "ingredients": ingredients,
        "budget": profile["weekly_budget"],
        "family_size": profile["family_size"],
    })


async def start_webserver(port: int = 8090):
    app = web.Application()
    app.add_routes(routes)
    app.router.add_static('/static', WEBAPP_DIR)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server: http://localhost:{port}")
    return runner
