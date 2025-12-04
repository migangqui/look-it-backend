# Temperature-Integrated Outfit Recommendation Algorithm

This document describes the full integration of **temperature**, **warmth**, **occasion**, **roles**, **patterns**, and **color harmony** into an outfit recommendation algorithm.

---

## 1. Inputs

```python
generate_outfits(
    garments,            # list of garment objects
    occasion,            # "casual" | "formal"
    temperature_c,       # temperature in ºC
    cold_sensitivity=0,  # -1 = warm person, 0 = normal, +1 = cold-sensitive
    n_results=10
)
```

---

## 2. Temperature → Target Warmth

```python
def target_warmth_from_temperature(temp_c):
    if temp_c >= 28:
        return 1.5    # very light
    elif temp_c >= 23:
        return 2.0    # light
    elif temp_c >= 17:
        return 3.0    # medium
    elif temp_c >= 10:
        return 4.0    # warm
    else:
        return 5.0    # very warm
```

Enhanced with user sensitivity:

```python
def compute_target_warmth(temp_c, cold_sensitivity=0):
    base = target_warmth_from_temperature(temp_c)
    return max(1.0, min(5.0, base + 0.5 * cold_sensitivity))
```

---

## 3. Outfit Templates (role combinations)

```python
OUTFIT_TEMPLATES = [
    {
        "id": "casual_hot",
        "occasion": "casual",
        "min_warmth": 1.0,
        "max_warmth": 2.0,
        "roles": [
            {"role": "footwear", "required": True},
            {"role": "bottom", "required": True},
            {"role": "base_top", "required": True}
        ]
    },
    {
        "id": "casual_mild",
        "occasion": "casual",
        "min_warmth": 2.0,
        "max_warmth": 3.5,
        "roles": [
            {"role": "footwear", "required": True},
            {"role": "bottom", "required": True},
            {"role": "base_top", "required": True},
            {"role": "mid_top", "required": False},
            {"role": "outwear_top", "required": False}
        ]
    },
    {
        "id": "casual_cold",
        "occasion": "casual",
        "min_warmth": 3.0,
        "max_warmth": 5.0,
        "roles": [
            {"role": "footwear", "required": True},
            {"role": "bottom", "required": True},
            {"role": "base_top", "required": True},
            {"role": "mid_top", "required": True},
            {"role": "outwear_top", "required": True}
        ]
    },
    {
        "id": "formal_mild",
        "occasion": "formal",
        "min_warmth": 2.0,
        "max_warmth": 3.5,
        "roles": [
            {"role": "footwear", "required": True},
            {"role": "bottom", "required": False},
            {"role": "base_top_entero", "required": False},
            {"role": "base_top", "required": True},
            {"role": "outwear_top", "required": False}
        ]
    },
    {
        "id": "formal_cold",
        "occasion": "formal",
        "min_warmth": 3.0,
        "max_warmth": 5.0,
        "roles": [
            {"role": "footwear", "required": True},
            {"role": "bottom", "required": False},
            {"role": "base_top_entero", "required": False},
            {"role": "base_top", "required": True},
            {"role": "mid_top", "required": True},
            {"role": "outwear_top", "required": True}
        ]
    }
]
```

---

## 4. Choosing the Right Template

```python
def choose_template(occasion, target_warmth):
    candidates = [t for t in OUTFIT_TEMPLATES if t["occasion"] == occasion]

    best = None
    best_distance = 999
    for t in candidates:
        if t["min_warmth"] <= target_warmth <= t["max_warmth"]:
            return t

        if target_warmth < t["min_warmth"]:
            dist = t["min_warmth"] - target_warmth
        else:
            dist = target_warmth - t["max_warmth"]

        if dist < best_distance:
            best_distance = dist
            best = t

    return best
```

---

## 5. Color Harmony Evaluation

### Basic RGB → neutral check

```python
def analyze_color(rgb):
    r, g, b = [c / 255.0 for c in rgb]
    max_c, min_c = max(r, g, b), min(r, g, b)
    lightness = (max_c + min_c) / 2.0

    if max_c == min_c:
        saturation = 0
    elif lightness < 0.5:
        saturation = (max_c - min_c) / (max_c + min_c)
    else:
        saturation = (max_c - min_c) / (2.0 - max_c - min_c)

    is_neutral = (
        saturation < 0.15 or
        lightness < 0.12 or
        lightness > 0.9
    )

    return {
        "lightness": lightness,
        "saturation": saturation,
        "is_neutral": is_neutral
    }
```

### Harmony scoring

```python
def evaluate_color_harmony(garments):
    analyzed = [analyze_color(g.color_rgb) for g in garments]
    neutrals = [a for a in analyzed if a["is_neutral"]]
    colors = [a for a in analyzed if not a["is_neutral"]]

    score = 0

    if len(neutrals) >= 2:
        score += 2
    elif len(neutrals) == 1:
        score += 1
    else:
        score -= 2

    if len(colors) > 2:
        score -= (len(colors) - 2)

    return score
```

---

## 6. Pattern Harmony

```python
def evaluate_pattern_harmony(garments):
    intensities = [getattr(g, "pattern_intensity", 1) for g in garments]
    strong = [i for i in intensities if i == 3]
    medium = [i for i in intensities if i == 2]

    score = 0
    if len(strong) > 1:
        score -= 2
    if len(strong) == 1 and len(medium) > 1:
        score -= 1
    if len(strong) == 0 and len(medium) <= 1:
        score += 1

    return score
```

---

## 7. Outfit Scoring

```python
def score_outfit(outfit, target_warmth):
    warmth_values = [g.warmth for g in outfit]
    avg_warmth = sum(warmth_values) / len(warmth_values)
    warmth_span = max(warmth_values) - min(warmth_values)

    score = 0.0

    score -= abs(avg_warmth - target_warmth)

    if warmth_span >= 3:
        score -= 1.0

    score += evaluate_color_harmony(outfit)
    score += evaluate_pattern_harmony(outfit)

    return score
```

---

## 8. Full Outfit Generation Pipeline

```python
def generate_outfits(
    garments,
    occasion,
    temperature_c,
    cold_sensitivity=0,
    n_results=10
):
    target_warmth = compute_target_warmth(temperature_c, cold_sensitivity)

    garments_occ = [g for g in garments if g.ocasion in [occasion, "both"]]

    template = choose_template(occasion, target_warmth)
    if template is None:
        return []

    role_to_items = {}
    for r in template["roles"]:
        role = r["role"]
        items = [
            g for g in garments_occ
            if g.rol == role and template["min_warmth"] <= g.warmth <= template["max_warmth"]
        ]

        if r["required"] and not items:
            return []

        role_to_items[role] = items[:10]

    candidate_outfits = build_combinations_from_roles(role_to_items, template["roles"])

    scored = [
        (score_outfit(outfit, target_warmth), outfit)
        for outfit in candidate_outfits
    ]

    scored.sort(key=lambda x: x[0], reverse=True)
    return [outfit for score, outfit in scored[:n_results]]
```

---

End of document.
