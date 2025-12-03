# Technical Tasks – Additional Garment Fields (`warmth`, `pattern`, `pattern_intensity`)

- Update MongoDB garment schema in `app/db/mongo_models.py` to include `warmth: int | None`, `pattern: str | None`, and optional `pattern_intensity: int | None`, ensuring reasonable defaults and validation ranges (1–5 for warmth, 1–3 for pattern_intensity).
- Propagate the new fields through the garment repository in `app/db/repository/garmentitem_repository.py` so they are persisted and retrieved correctly.
- Extend request/response models in the garment API router (and related Pydantic models, if any) under `app/api/v1/garment_router.py` to support the new fields in garment creation, update, and retrieval endpoints.
- Update `app/core/garment_service.py` to accept, validate, and pass through the new fields when creating or updating garments.
- Add or update unit tests (e.g., new tests under `tests/` or extending existing ones) to cover the new fields in schema validation, service logic, and API behavior (including default values and error handling for invalid ranges).
- Update API documentation or README sections (if applicable) to describe the new garment fields and their allowed values.
