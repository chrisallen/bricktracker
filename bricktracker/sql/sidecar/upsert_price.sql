INSERT INTO "sidecar_set_cache"
    ("set_ref", "price_payload", "price_fetched_at")
VALUES
    (:set_ref, :price_payload, :price_fetched_at)
ON CONFLICT("set_ref") DO UPDATE SET
    "price_payload" = :price_payload,
    "price_fetched_at" = :price_fetched_at
