# Technical Tasks – Temperature-Integrated Outfit Recommendation

- Implementar helpers de temperatura → calidez objetivo (`target_warmth_from_temperature` y `compute_target_warmth`) en `app/core/look_generator.py` (o un nuevo módulo dedicado) usando la escala de 1–5 ya definida para `warmth`.
- Definir y centralizar `OUTFIT_TEMPLATES` en la capa de generación de looks, alineando los nombres de rol de los templates con los valores de `RoleEnum` y asegurando que los rangos de `min_warmth`/`max_warmth` sean coherentes con la escala de calidez.
- Implementar `choose_template(occasion, target_warmth)` para seleccionar el template más adecuado según ocasión y calidez objetivo.
- Aprovechar el campo de color existente de las prendas para obtener una representación utilizable por el algoritmo (p. ej. mapeo a RGB o categorías de color) e implementar `analyze_color` y `evaluate_color_harmony` en el módulo de generación de looks.
- Implementar `evaluate_pattern_harmony(garments)` utilizando `pattern_intensity`, manejando valores ausentes con un valor por defecto razonable.
- Implementar `score_outfit(outfit, target_warmth)` combinando desviación de calidez media, rango de calidez, armonía de color y armonía de patrón en una puntuación numérica única.
- Implementar el pipeline completo `generate_outfits(garments, occasion, temperature_c, cold_sensitivity, n_results)` en `app/core/look_generator.py`, incluyendo: filtrado por ocasión, agrupación por roles, validación de roles obligatorios, construcción de combinaciones y ordenación por puntuación.
- Añadir una capa de obtención de temperatura (actual o para una fecha concreta) a partir de la ubicación del usuario usando la API de OpenWeatherMap, de forma que `temperature_c` se derive automáticamente del lugar y día seleccionados.
- Exponer un endpoint en `app/api/v1/look_router.py` para solicitar sugerencias de looks a partir de `occasion`, información de ubicación/fecha del usuario, `cold_sensitivity` y `n_results`, resolviendo internamente `temperature_c` vía OpenWeatherMap, delegando en el generador core y devolviendo una lista estructurada de outfits.
