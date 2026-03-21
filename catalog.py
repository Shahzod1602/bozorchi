# Korzinka.uz narxlari asosida mahsulotlar katalogi

PRODUCTS = [
    # Go'sht
    {"name": "Mol go'shti", "price": 110000, "unit": "kg", "category": "Go'sht", "emoji": "🥩", "color": "#FFEAEA"},
    {"name": "Tovuq go'shti", "price": 48000, "unit": "kg", "category": "Go'sht", "emoji": "🍗", "color": "#FFEAEA"},
    {"name": "Tovuq filesi", "price": 62000, "unit": "kg", "category": "Go'sht", "emoji": "🍗", "color": "#FFEAEA"},
    {"name": "Qo'y go'shti", "price": 145000, "unit": "kg", "category": "Go'sht", "emoji": "🥩", "color": "#FFEAEA"},
    {"name": "Qiyma", "price": 90000, "unit": "kg", "category": "Go'sht", "emoji": "🥩", "color": "#FFEAEA"},
    {"name": "Sosiska", "price": 66000, "unit": "kg", "category": "Go'sht", "emoji": "🌭", "color": "#FFEAEA"},

    # Sabzavotlar
    {"name": "Kartoshka", "price": 5000, "unit": "kg", "category": "Sabzavot", "emoji": "🥔", "color": "#FFFBE6"},
    {"name": "Piyoz", "price": 4000, "unit": "kg", "category": "Sabzavot", "emoji": "🧅", "color": "#FFFBE6"},
    {"name": "Sabzi", "price": 6000, "unit": "kg", "category": "Sabzavot", "emoji": "🥕", "color": "#FFFBE6"},
    {"name": "Pomidor", "price": 12000, "unit": "kg", "category": "Sabzavot", "emoji": "🍅", "color": "#FFFBE6"},
    {"name": "Bodring", "price": 10000, "unit": "kg", "category": "Sabzavot", "emoji": "🥒", "color": "#FFFBE6"},
    {"name": "Karam", "price": 5000, "unit": "kg", "category": "Sabzavot", "emoji": "🥬", "color": "#FFFBE6"},
    {"name": "Qalampir", "price": 18000, "unit": "kg", "category": "Sabzavot", "emoji": "🫑", "color": "#FFFBE6"},
    {"name": "Ko'k piyoz", "price": 5000, "unit": "bog'", "category": "Sabzavot", "emoji": "🌿", "color": "#FFFBE6"},
    {"name": "Sarimsoq", "price": 30000, "unit": "kg", "category": "Sabzavot", "emoji": "🧄", "color": "#FFFBE6"},
    {"name": "Baqlajon", "price": 12000, "unit": "kg", "category": "Sabzavot", "emoji": "🍆", "color": "#FFFBE6"},
    {"name": "Limon", "price": 25000, "unit": "kg", "category": "Sabzavot", "emoji": "🍋", "color": "#FFFBE6"},
    {"name": "Ukrop", "price": 5000, "unit": "bog'", "category": "Sabzavot", "emoji": "🌿", "color": "#FFFBE6"},
    {"name": "Kashnich", "price": 5000, "unit": "bog'", "category": "Sabzavot", "emoji": "🌿", "color": "#FFFBE6"},

    # Mevalar
    {"name": "Olma", "price": 15000, "unit": "kg", "category": "Meva", "emoji": "🍎", "color": "#FFE8F0"},
    {"name": "Banan", "price": 18000, "unit": "kg", "category": "Meva", "emoji": "🍌", "color": "#FFE8F0"},
    {"name": "Apelsin", "price": 20000, "unit": "kg", "category": "Meva", "emoji": "🍊", "color": "#FFE8F0"},
    {"name": "Uzum", "price": 25000, "unit": "kg", "category": "Meva", "emoji": "🍇", "color": "#FFE8F0"},
    {"name": "Nok", "price": 18000, "unit": "kg", "category": "Meva", "emoji": "🍐", "color": "#FFE8F0"},
    {"name": "Qovun", "price": 12000, "unit": "kg", "category": "Meva", "emoji": "🍈", "color": "#FFE8F0"},
    {"name": "Tarvuz", "price": 6000, "unit": "kg", "category": "Meva", "emoji": "🍉", "color": "#FFE8F0"},
    {"name": "Shaftoli", "price": 22000, "unit": "kg", "category": "Meva", "emoji": "🍑", "color": "#FFE8F0"},

    # Sut mahsulotlari
    {"name": "Sut", "price": 15000, "unit": "litr", "category": "Sut", "emoji": "🥛", "color": "#EAF4FF"},
    {"name": "Tuxum", "price": 28000, "unit": "10 ta", "category": "Sut", "emoji": "🥚", "color": "#EAF4FF"},
    {"name": "Sariyog'", "price": 85000, "unit": "kg", "category": "Sut", "emoji": "🧈", "color": "#EAF4FF"},
    {"name": "Qatiq", "price": 18000, "unit": "litr", "category": "Sut", "emoji": "🍶", "color": "#EAF4FF"},
    {"name": "Pishloq", "price": 80000, "unit": "kg", "category": "Sut", "emoji": "🧀", "color": "#EAF4FF"},
    {"name": "Qaymoq", "price": 25000, "unit": "200g", "category": "Sut", "emoji": "🫙", "color": "#EAF4FF"},
    {"name": "Tvorog", "price": 35000, "unit": "kg", "category": "Sut", "emoji": "🫙", "color": "#EAF4FF"},

    # Don mahsulotlari
    {"name": "Guruch", "price": 19000, "unit": "kg", "category": "Don", "emoji": "🌾", "color": "#FFF8E1"},
    {"name": "Un", "price": 8000, "unit": "kg", "category": "Don", "emoji": "🌾", "color": "#FFF8E1"},
    {"name": "Makaron", "price": 12000, "unit": "kg", "category": "Don", "emoji": "🍝", "color": "#FFF8E1"},
    {"name": "Grechixa", "price": 25000, "unit": "kg", "category": "Don", "emoji": "🌾", "color": "#FFF8E1"},
    {"name": "Suli (ovyos)", "price": 18000, "unit": "kg", "category": "Don", "emoji": "🌾", "color": "#FFF8E1"},
    {"name": "Non (oq)", "price": 6000, "unit": "dona", "category": "Don", "emoji": "🍞", "color": "#FFF8E1"},
    {"name": "Lavash", "price": 8000, "unit": "dona", "category": "Don", "emoji": "🫓", "color": "#FFF8E1"},

    # Yog' va ziravorlar
    {"name": "O'simlik yog'i", "price": 25000, "unit": "litr", "category": "Ziravorlar", "emoji": "🫙", "color": "#F0EAFF"},
    {"name": "Shakar", "price": 15000, "unit": "kg", "category": "Ziravorlar", "emoji": "🍬", "color": "#F0EAFF"},
    {"name": "Tuz", "price": 4000, "unit": "kg", "category": "Ziravorlar", "emoji": "🧂", "color": "#F0EAFF"},
    {"name": "Qora murch", "price": 25000, "unit": "100g", "category": "Ziravorlar", "emoji": "🌶️", "color": "#F0EAFF"},
    {"name": "Zira", "price": 30000, "unit": "100g", "category": "Ziravorlar", "emoji": "🌿", "color": "#F0EAFF"},
    {"name": "Ketchup", "price": 18000, "unit": "500g", "category": "Ziravorlar", "emoji": "🍅", "color": "#F0EAFF"},
    {"name": "Majonez", "price": 16000, "unit": "500g", "category": "Ziravorlar", "emoji": "🫙", "color": "#F0EAFF"},
    {"name": "Tomato pasta", "price": 14000, "unit": "500g", "category": "Ziravorlar", "emoji": "🍅", "color": "#F0EAFF"},

    # Ichimliklar
    {"name": "Mineral suv", "price": 8000, "unit": "1.5 L", "category": "Ichimlik", "emoji": "💧", "color": "#E6FAFF"},
    {"name": "Limonid", "price": 13000, "unit": "1.5 L", "category": "Ichimlik", "emoji": "🥤", "color": "#E6FAFF"},
    {"name": "Sharbat", "price": 12000, "unit": "litr", "category": "Ichimlik", "emoji": "🧃", "color": "#E6FAFF"},
    {"name": "Choy (qora)", "price": 35000, "unit": "100g", "category": "Ichimlik", "emoji": "🍵", "color": "#E6FAFF"},
    {"name": "Kofe", "price": 60000, "unit": "100g", "category": "Ichimlik", "emoji": "☕", "color": "#E6FAFF"},
]


def search_products(query: str, limit: int = 8) -> list:
    q = query.strip().lower()
    if not q:
        return []
    results = []
    for p in PRODUCTS:
        if q in p["name"].lower():
            results.append(p)
        if len(results) >= limit:
            break
    return results


def get_all_products() -> list:
    return PRODUCTS


def get_categories() -> list:
    seen = []
    for p in PRODUCTS:
        if p["category"] not in seen:
            seen.append(p["category"])
    return seen


def get_by_category(category: str) -> list:
    return [p for p in PRODUCTS if p["category"] == category]
