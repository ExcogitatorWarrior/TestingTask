from collections import defaultdict

def generate(rows):
    brand_prices = defaultdict(list)

    for row in rows:
        try:
            brand = row["brand"].strip().lower()
            price = float(row["price"])
            brand_prices[brand].append(price)
        except (KeyError, ValueError, AttributeError):
            continue

    averages = {
        brand: sum(vals) / len(vals)
        for brand, vals in brand_prices.items()
        if vals
    }

    return sorted(averages.items(), key=lambda x: x[1], reverse=True)