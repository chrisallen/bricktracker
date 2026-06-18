SELECT
    "sidecar_set_cache"."set_ref" AS "set_ref",
    "sidecar_set_cache"."payload" AS "payload",
    "sidecar_set_cache"."price_payload" AS "price_payload",
    "sidecar_set_cache"."fetched_at" AS "fetched_at",
    "sidecar_set_cache"."price_fetched_at" AS "price_fetched_at"
FROM "sidecar_set_cache"
WHERE "sidecar_set_cache"."set_ref" IS NOT DISTINCT FROM :set_ref
