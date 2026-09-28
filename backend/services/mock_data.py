"""
Simulated product/vendor lookups. In place of live scraping (which is
fragile and often against ToS), these functions return realistic mock
data keyed by category/budget so the planners have something concrete
to weave into their recommendations. Swap these out for real scraping
or affiliate APIs later without touching the route code.
"""
import random

_HOME_ITEMS = [
    {"name": "Modular 3-Seater Sofa", "source": "IKEA", "price_range": (15000, 45000)},
    {"name": "Wooden Coffee Table", "source": "IKEA", "price_range": (3000, 9000)},
    {"name": "LED Floor Lamp", "source": "Amazon", "price_range": (1200, 4000)},
    {"name": "Bookshelf Unit", "source": "IKEA", "price_range": (4000, 12000)},
    {"name": "Area Rug 6x9", "source": "Amazon", "price_range": (2000, 8000)},
]

_PARTY_ITEMS = [
    {"name": "Balloon Arch Kit", "source": "Amazon", "price_range": (800, 2500)},
    {"name": "Catering Package (per plate)", "source": "Zomato", "price_range": (300, 1200)},
    {"name": "LED String Lights (10m)", "source": "Amazon", "price_range": (500, 1500)},
    {"name": "Photo Booth Props Set", "source": "Amazon", "price_range": (400, 1000)},
    {"name": "Custom Cake", "source": "Zomato", "price_range": (1000, 5000)},
]

_JEWELRY_ITEMS = [
    {"name": "Gold-Plated Statement Necklace", "source": "Amazon", "price_range": (1500, 6000)},
    {"name": "Pearl Drop Earrings", "source": "Amazon", "price_range": (800, 3000)},
    {"name": "Kundan Choker Set", "source": "Amazon", "price_range": (2500, 9000)},
    {"name": "Minimalist Chain Bracelet", "source": "Amazon", "price_range": (600, 2000)},
]

_CATALOG = {
    "home": _HOME_ITEMS,
    "party": _PARTY_ITEMS,
    "jewelry": _JEWELRY_ITEMS,
}


def get_mock_products(planner: str, budget: float, max_items: int = 4) -> list[dict]:
    """
    Return a plausible set of products for the given planner type that
    roughly fit within the stated budget. This is simulated data, not a
    live scrape — replace with real API/scraping integration later.
    """
    items = _CATALOG.get(planner, [])
    if not items:
        return []

    chosen = random.sample(items, k=min(max_items, len(items)))
    results = []
    for item in chosen:
        low, high = item["price_range"]
        # Bias price toward the lower end for smaller budgets
        price = random.randint(low, min(high, max(low, int(budget * 0.4))) or high)
        results.append(
            {
                "name": item["name"],
                "source": item["source"],
                "estimated_price": price,
            }
        )
    return results
