from collections import defaultdict

def generate(rows):
    brand_ratings = defaultdict(list)

    for row in rows:
        try:
            brand = row["brand"].strip().lower()
            rating = float(row["rating"])
            brand_ratings[brand].append(rating)
        except (KeyError, ValueError, AttributeError):
            continue

    averages = {
        brand: sum(vals) / len(vals)
        for brand, vals in brand_ratings.items()
        if vals
    }

    return sorted(averages.items(), key=lambda x: x[1], reverse=True)