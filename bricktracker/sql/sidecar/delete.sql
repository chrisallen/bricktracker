DELETE FROM "sidecar_set_cache"
WHERE "sidecar_set_cache"."set_ref" IS NOT DISTINCT FROM :set_ref
