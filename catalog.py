# Korzinka.uz narxlari asosida mahsulotlar katalogi
# Narxlar taxminiy (so'm), yangilanishi mumkin

PRODUCTS = [
    # Go'sht
    {"name": "Mol go'shti", "price": 110000, "unit": "kg", "category": "Go'sht"},
    {"name": "Tovuq go'shti", "price": 48000, "unit": "kg", "category": "Go'sht"},
    {"name": "Tovuq filesi", "price": 62000, "unit": "kg", "category": "Go'sht"},
    {"name": "Qo'y go'shti", "price": 145000, "unit": "kg", "category": "Go'sht"},
    {"name": "Qiyma (mol)", "price": 90000, "unit": "kg", "category": "Go'sht"},
    {"name": "Sosiska", "price": 66000, "unit": "kg", "category": "Go'sht"},

    # Sabzavotlar
    {"name": "Kartoshka", "price": 5000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Piyoz", "price": 4000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Sabzi", "price": 6000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Pomidor", "price": 12000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Bodring", "price": 10000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Karam", "price": 5000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Qalampir (bolgar)", "price": 18000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Ko'k piyoz", "price": 6000, "unit": "bog'", "category": "Sabzavot"},
    {"name": "Sarimsoq", "price": 30000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Baqlajon", "price": 12000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Qovoq", "price": 8000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Limon", "price": 25000, "unit": "kg", "category": "Sabzavot"},
    {"name": "Ukrop", "price": 5000, "unit": "bog'", "category": "Sabzavot"},
    {"name": "Kashnich", "price": 5000, "unit": "bog'", "category": "Sabzavot"},

    # Mevalar
    {"name": "Olma", "price": 15000, "unit": "kg", "category": "Meva"},
    {"name": "Banan", "price": 18000, "unit": "kg", "category": "Meva"},
    {"name": "Apelsin", "price": 20000, "unit": "kg", "category": "Meva"},
    {"name": "Uzum", "price": 25000, "unit": "kg", "category": "Meva"},
    {"name": "Nok", "price": 18000, "unit": "kg", "category": "Meva"},

    # Sut mahsulotlari
    {"name": "Sut", "price": 15000, "unit": "litr", "category": "Sut"},
    {"name": "Tuxum", "price": 28000, "unit": "10 ta", "category": "Sut"},
    {"name": "Sariyog'", "price": 85000, "unit": "kg", "category": "Sut"},
    {"name": "Qatiq", "price": 18000, "unit": "litr", "category": "Sut"},
    {"name": "Pishloq", "price": 80000, "unit": "kg", "category": "Sut"},
    {"name": "Qaymoq", "price": 25000, "unit": "200g", "category": "Sut"},
    {"name": "Tvorog", "price": 35000, "unit": "kg", "category": "Sut"},

    # Don mahsulotlari
    {"name": "Guruch", "price": 19000, "unit": "kg", "category": "Don"},
    {"name": "Un", "price": 8000, "unit": "kg", "category": "Don"},
    {"name": "Makaron", "price": 12000, "unit": "kg", "category": "Don"},
    {"name": "Semolina (manno)", "price": 14000, "unit": "kg", "category": "Don"},
    {"name": "Grechixa", "price": 25000, "unit": "kg", "category": "Don"},
    {"name": "Suli (ovyos)", "price": 18000, "unit": "kg", "category": "Don"},

    # Yog' va ziravorlar
    {"name": "O'simlik yog'i", "price": 25000, "unit": "litr", "category": "Yog'"},
    {"name": "Shakar", "price": 15000, "unit": "kg", "category": "Ziravorlar"},
    {"name": "Tuz", "price": 4000, "unit": "kg", "category": "Ziravorlar"},
    {"name": "Qora murch", "price": 25000, "unit": "100g", "category": "Ziravorlar"},
    {"name": "Zira", "price": 30000, "unit": "100g", "category": "Ziravorlar"},
    {"name": "Ketchup", "price": 18000, "unit": "500g", "category": "Ziravorlar"},
    {"name": "Majonez", "price": 16000, "unit": "500g", "category": "Ziravorlar"},
    {"name": "Tomato pasta", "price": 14000, "unit": "500g", "category": "Ziravorlar"},

    # Ichimliklar
    {"name": "Mineral suv", "price": 8000, "unit": "1.5 L", "category": "Ichimlik"},
    {"name": "Limonid", "price": 13000, "unit": "1.5 L", "category": "Ichimlik"},
    {"name": "Sharbat", "price": 12000, "unit": "litr", "category": "Ichimlik"},
    {"name": "Choy (qora)", "price": 35000, "unit": "100g", "category": "Ichimlik"},

    # Non-pishloq
    {"name": "Non (oq)", "price": 6000, "unit": "dona", "category": "Non"},
    {"name": "Lavaş", "price": 8000, "unit": "dona", "category": "Non"},
    {"name": "Печенье", "price": 20000, "unit": "kg", "category": "Non"},
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
