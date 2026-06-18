INSERT INTO "sidecar_set_cache"
    ("set_ref", "payload", "fetched_at")
VALUES
    (:set_ref, :payload, :fetched_at)
ON CONFLICT("set_ref") DO UPDATE SET
    "payload" = :payload,
    "fetched_at" = :fetched_at
