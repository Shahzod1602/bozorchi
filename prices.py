# O'zbekiston bozorlaridagi taxminiy narxlar (so'mda, 2024-2025)
# Manba: Korzinka, Makro, mahalliy bozorlar

PRICES = {
    # Go'sht
    "mol go'shti": {"price": 85000, "unit": "kg"},
    "qo'y go'shti": {"price": 95000, "unit": "kg"},
    "tovuq": {"price": 38000, "unit": "kg"},
    "tovuq filesi": {"price": 55000, "unit": "kg"},
    "baliq": {"price": 45000, "unit": "kg"},
    "qiyma": {"price": 80000, "unit": "kg"},

    # Sabzavotlar
    "kartoshka": {"price": 3000, "unit": "kg"},
    "sabzi": {"price": 4000, "unit": "kg"},
    "piyoz": {"price": 3000, "unit": "kg"},
    "pomidor": {"price": 8000, "unit": "kg"},
    "bodring": {"price": 6000, "unit": "kg"},
    "karam": {"price": 4000, "unit": "kg"},
    "qovoq": {"price": 3500, "unit": "kg"},
    "baklajan": {"price": 6000, "unit": "kg"},
    "bolgarcha qalampir": {"price": 10000, "unit": "kg"},
    "chesnok": {"price": 20000, "unit": "kg"},
    "limon": {"price": 15000, "unit": "kg"},

    # Don mahsulotlari
    "guruch": {"price": 14000, "unit": "kg"},
    "makaron": {"price": 8000, "unit": "kg"},
    "un": {"price": 5000, "unit": "kg"},
    "non": {"price": 3000, "unit": "dona"},
    "lavash": {"price": 4000, "unit": "dona"},

    # Sut mahsulotlari
    "sut": {"price": 8000, "unit": "litr"},
    "tuxum": {"price": 1500, "unit": "dona"},
    "tuxum o'ntalik": {"price": 15000, "unit": "o'ntalik"},
    "yog'": {"price": 28000, "unit": "kg"},
    "o'simlik yog'i": {"price": 18000, "unit": "litr"},
    "qaymoq": {"price": 25000, "unit": "kg"},
    "suzma": {"price": 18000, "unit": "kg"},
    "pishloq": {"price": 55000, "unit": "kg"},

    # Ziravorlar
    "tuz": {"price": 3000, "unit": "kg"},
    "qora murch": {"price": 25000, "unit": "100g"},
    "zira": {"price": 30000, "unit": "100g"},
    "xivich": {"price": 8000, "unit": "100g"},

    # Boshqalar
    "sholi": {"price": 14000, "unit": "kg"},
    "nohot": {"price": 16000, "unit": "kg"},
    "mosh": {"price": 14000, "unit": "kg"},
    "loviya": {"price": 15000, "unit": "kg"},
    "o'rik": {"price": 20000, "unit": "kg"},
    "olma": {"price": 10000, "unit": "kg"},
    "banan": {"price": 12000, "unit": "kg"},
    "shakar": {"price": 9000, "unit": "kg"},
}


def get_price_reference() -> str:
    """AI uchun narxlar ma'lumotnomasi"""
    text = "O'zbekiston bozorlaridagi hozirgi narxlar (so'mda):\n"
    categories = {
        "Go'sht": ["mol go'shti", "qo'y go'shti", "tovuq", "tovuq filesi", "qiyma"],
        "Sabzavot": ["kartoshka", "sabzi", "piyoz", "pomidor", "bodring", "karam"],
        "Don": ["guruch", "makaron", "un", "non"],
        "Sut": ["sut", "tuxum o'ntalik", "yog'", "o'simlik yog'i", "qaymoq"],
        "Boshqa": ["shakar", "tuz", "nohot", "mosh"],
    }
    for cat, items in categories.items():
        text += f"\n{cat}:\n"
        for item in items:
            if item in PRICES:
                p = PRICES[item]
                text += f"  - {item}: {p['price']:,} so'm/{p['unit']}\n"
    return text
