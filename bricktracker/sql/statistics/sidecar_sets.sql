-- description: Set refs and purchase prices for the sidecar pricing aggregation.
-- One row per set instance (matches the old per-instance JOIN), so the totals
-- are computed in Python against the sidecar bulk response instead of a local
-- cache table.
SELECT
    "bricktracker_sets"."set" AS "set_ref",
    "bricktracker_sets"."purchase_price" AS "purchase_price"
FROM "bricktracker_sets"
