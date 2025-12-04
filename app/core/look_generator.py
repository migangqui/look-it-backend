from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Sequence

from app.core.weather_service import get_temperature_c_for_city
from app.db.mongo_models import GarmentItem, OccasionEnum, RoleEnum
from app.db.repository.garmentitem_repository import find_by_user_id


def target_warmth_from_temperature(temp_c: float) -> float:
    if temp_c >= 28:
        return 1.5  # very light
    if temp_c >= 23:
        return 2.0  # light
    if temp_c >= 17:
        return 3.0  # medium
    if temp_c >= 10:
        return 4.0  # warm
    return 5.0  # very warm


def compute_target_warmth(temp_c: float, cold_sensitivity: float = 0) -> float:
    base = target_warmth_from_temperature(temp_c)
    adjusted = base + 0.5 * cold_sensitivity
    return max(1.0, min(5.0, adjusted))


@dataclass(frozen=True)
class OutfitTemplateRole:
    role: RoleEnum
    required: bool


@dataclass(frozen=True)
class OutfitTemplate:
    id: str
    occasion: OccasionEnum
    min_warmth: float
    max_warmth: float
    roles: List[OutfitTemplateRole]


OUTFIT_TEMPLATES: List[OutfitTemplate] = [
    OutfitTemplate(
        id="casual_hot",
        occasion=OccasionEnum.CASUAL,
        min_warmth=1.0,
        max_warmth=2.0,
        roles=[
            OutfitTemplateRole(RoleEnum.FOOTWEAR, True),
            OutfitTemplateRole(RoleEnum.BOTTOM, True),
            OutfitTemplateRole(RoleEnum.BASE_TOP, True),
        ],
    ),
    OutfitTemplate(
        id="casual_mild",
        occasion=OccasionEnum.CASUAL,
        min_warmth=2.0,
        max_warmth=3.5,
        roles=[
            OutfitTemplateRole(RoleEnum.FOOTWEAR, True),
            OutfitTemplateRole(RoleEnum.BOTTOM, True),
            OutfitTemplateRole(RoleEnum.BASE_TOP, True),
            OutfitTemplateRole(RoleEnum.MID_TOP, False),
            OutfitTemplateRole(RoleEnum.OUTWEAR_TOP, False),
        ],
    ),
    OutfitTemplate(
        id="casual_cold",
        occasion=OccasionEnum.CASUAL,
        min_warmth=3.0,
        max_warmth=5.0,
        roles=[
            OutfitTemplateRole(RoleEnum.FOOTWEAR, True),
            OutfitTemplateRole(RoleEnum.BOTTOM, True),
            OutfitTemplateRole(RoleEnum.BASE_TOP, True),
            OutfitTemplateRole(RoleEnum.MID_TOP, True),
            OutfitTemplateRole(RoleEnum.OUTWEAR_TOP, True),
        ],
    ),
    OutfitTemplate(
        id="formal_mild",
        occasion=OccasionEnum.FORMAL,
        min_warmth=2.0,
        max_warmth=3.5,
        roles=[
            OutfitTemplateRole(RoleEnum.FOOTWEAR, True),
            OutfitTemplateRole(RoleEnum.BOTTOM, False),
            OutfitTemplateRole(RoleEnum.FULL_BODY, False),
            OutfitTemplateRole(RoleEnum.BASE_TOP, True),
            OutfitTemplateRole(RoleEnum.OUTWEAR_TOP, False),
        ],
    ),
    OutfitTemplate(
        id="formal_cold",
        occasion=OccasionEnum.FORMAL,
        min_warmth=3.0,
        max_warmth=5.0,
        roles=[
            OutfitTemplateRole(RoleEnum.FOOTWEAR, True),
            OutfitTemplateRole(RoleEnum.BOTTOM, False),
            OutfitTemplateRole(RoleEnum.FULL_BODY, False),
            OutfitTemplateRole(RoleEnum.BASE_TOP, True),
            OutfitTemplateRole(RoleEnum.MID_TOP, True),
            OutfitTemplateRole(RoleEnum.OUTWEAR_TOP, True),
        ],
    ),
]


def choose_template(occasion: OccasionEnum, target_warmth: float) -> OutfitTemplate | None:
    candidates = [t for t in OUTFIT_TEMPLATES if t.occasion == occasion]

    best: OutfitTemplate | None = None
    best_distance = 999.0
    for template in candidates:
        if template.min_warmth <= target_warmth <= template.max_warmth:
            return template

        if target_warmth < template.min_warmth:
            distance = template.min_warmth - target_warmth
        else:
            distance = target_warmth - template.max_warmth

        if distance < best_distance:
            best_distance = distance
            best = template

    return best


def _garment_warmth_value(garment: GarmentItem) -> float:
    if garment.warmth is None:
        return 3.0
    return float(garment.warmth)


def _garment_warmth_in_range(garment: GarmentItem, min_warmth: float, max_warmth: float) -> bool:
    warmth_value = _garment_warmth_value(garment)
    return min_warmth <= warmth_value <= max_warmth


def _filter_garments_for_occasion(
    garments: Sequence[GarmentItem],
    occasion: OccasionEnum,
) -> List[GarmentItem]:
    return [
        g
        for g in garments
        if g.occasion in (occasion, OccasionEnum.ALL, None)
    ]


def _build_combinations_from_roles(
    role_to_items: dict[RoleEnum, List[GarmentItem]],
    roles: Sequence[OutfitTemplateRole],
) -> List[List[GarmentItem]]:
    from itertools import product

    options_per_role: List[List[GarmentItem | None]] = []
    for role_spec in roles:
        items = role_to_items.get(role_spec.role, [])
        if role_spec.required:
            options_per_role.append(items)
        else:
            options_per_role.append([None] + items)

    combinations: List[List[GarmentItem]] = []
    for combo in product(*options_per_role):
        selected = [g for g in combo if g is not None]
        if selected:
            combinations.append(selected)
    return combinations


def _map_color_name_to_rgb(color_name: str | None) -> tuple[int, int, int] | None:
    if not color_name:
        return None

    name = color_name.strip().lower()
    color_map: dict[str, tuple[int, int, int]] = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "gray": (128, 128, 128),
        "grey": (128, 128, 128),
        "red": (255, 0, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "brown": (150, 75, 0),
        "pink": (255, 192, 203),
        "purple": (128, 0, 128),
        "orange": (255, 165, 0),
        "beige": (245, 245, 220),
        "navy": (0, 0, 128),
    }
    return color_map.get(name)


def analyze_color(rgb: tuple[int, int, int]) -> dict[str, float | bool]:
    r, g, b = [c / 255.0 for c in rgb]
    max_c, min_c = max(r, g, b), min(r, g, b)
    lightness = (max_c + min_c) / 2.0

    if max_c == min_c:
        saturation = 0.0
    elif lightness < 0.5:
        saturation = (max_c - min_c) / (max_c + min_c)
    else:
        saturation = (max_c - min_c) / (2.0 - max_c - min_c)

    is_neutral = (
        saturation < 0.15
        or lightness < 0.12
        or lightness > 0.9
    )

    return {
        "lightness": lightness,
        "saturation": saturation,
        "is_neutral": is_neutral,
    }


def evaluate_color_harmony(garments: Sequence[GarmentItem]) -> float:
    analyzed: List[dict[str, float | bool]] = []
    for garment in garments:
        rgb = _map_color_name_to_rgb(garment.color)
        if rgb is None:
            analyzed.append({"lightness": 0.5, "saturation": 0.0, "is_neutral": True})
        else:
            analyzed.append(analyze_color(rgb))

    neutrals = [a for a in analyzed if a["is_neutral"]]
    colors = [a for a in analyzed if not a["is_neutral"]]

    score = 0.0
    if len(neutrals) >= 2:
        score += 2.0
    elif len(neutrals) == 1:
        score += 1.0
    else:
        score -= 2.0

    if len(colors) > 2:
        score -= float(len(colors) - 2)

    return score


def evaluate_pattern_harmony(garments: Sequence[GarmentItem]) -> float:
    intensities = [
        garment.pattern_intensity if garment.pattern_intensity is not None else 1
        for garment in garments
    ]
    strong = [i for i in intensities if i == 3]
    medium = [i for i in intensities if i == 2]

    score = 0.0
    if len(strong) > 1:
        score -= 2.0
    if len(strong) == 1 and len(medium) > 1:
        score -= 1.0
    if len(strong) == 0 and len(medium) <= 1:
        score += 1.0

    return score


def score_outfit(outfit: Sequence[GarmentItem], target_warmth: float) -> float:
    warmth_values = [_garment_warmth_value(g) for g in outfit]
    if not warmth_values:
        return -999.0

    avg_warmth = sum(warmth_values) / len(warmth_values)
    warmth_span = max(warmth_values) - min(warmth_values)

    score = 0.0

    score -= abs(avg_warmth - target_warmth)

    if warmth_span >= 3:
        score -= 1.0

    score += evaluate_color_harmony(outfit)
    score += evaluate_pattern_harmony(outfit)

    return score


async def generate_outfits(
    user_id: str,
    occasion: OccasionEnum,
    city: str,
    country_code: str,
    target_date: date | None = None,
    cold_sensitivity: float = 0,
    n_results: int = 10,
) -> List[List[GarmentItem]]:
    if n_results <= 0:
        return []
    
    print("n_results:", n_results)

    garments: List[GarmentItem] = await find_by_user_id(user_id)
    if not garments:
        return []

    temperature_c = await get_temperature_c_for_city(
        city=city,
        country_code=country_code,
        target_date=target_date,
    )

    temperature_c = 20.0  # TEMPORARY OVERRIDE FOR TESTING

    target_warmth = compute_target_warmth(temperature_c, cold_sensitivity)

    garments_for_occasion = _filter_garments_for_occasion(garments, occasion)

    template = choose_template(occasion, target_warmth)
    if template is None:
        return []

    role_to_items: dict[RoleEnum, List[GarmentItem]] = {}
    for role_spec in template.roles:
        role = role_spec.role
        items: List[GarmentItem] = [
            g
            for g in garments_for_occasion
            if g.role == role and _garment_warmth_in_range(g, template.min_warmth, template.max_warmth)
        ]

        if role_spec.required and not items:
            return []

        role_to_items[role] = items[:10]

    candidate_outfits = _build_combinations_from_roles(role_to_items, template.roles)

    scored: List[tuple[float, List[GarmentItem]]] = [
        (score_outfit(outfit, target_warmth), outfit)
        for outfit in candidate_outfits
    ]

    scored.sort(key=lambda x: x[0], reverse=True)
    return [outfit for score, outfit in scored[:n_results]]
