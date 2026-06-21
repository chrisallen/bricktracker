-- Aggregate paid / retail (MSRP) / BrickLink market value across the collection.
-- MSRP and market value come from the cached sidecar payloads (JSON). Region is
-- whitelisted (US/UK/CA/DE) by the caller before being interpolated here.
SELECT
    COUNT(*) AS "total_sets",
    SUM(CASE WHEN "s"."purchase_price" IS NOT NULL THEN "s"."purchase_price" ELSE 0 END) AS "total_paid",
    SUM(CASE WHEN "s"."purchase_price" IS NOT NULL THEN 1 ELSE 0 END) AS "sets_with_paid",
    SUM("c"."msrp") AS "total_msrp",
    SUM(CASE WHEN "c"."msrp" IS NOT NULL THEN 1 ELSE 0 END) AS "sets_with_msrp",
    SUM("c"."market_new") AS "total_market_new",
    SUM("c"."market_used") AS "total_market_used",
    SUM(CASE WHEN "c"."market_new" IS NOT NULL THEN 1 ELSE 0 END) AS "sets_with_market",
    SUM(CASE WHEN "c"."market_used" IS NOT NULL THEN 1 ELSE 0 END) AS "sets_with_market_used",
    SUM(CASE WHEN "c"."msrp" IS NOT NULL AND "s"."purchase_price" IS NOT NULL THEN "s"."purchase_price" ELSE 0 END) AS "paid_where_msrp",
    SUM(CASE WHEN "c"."msrp" IS NOT NULL AND "s"."purchase_price" IS NOT NULL THEN "c"."msrp" ELSE 0 END) AS "msrp_where_paid",
    SUM(CASE WHEN "c"."market_new" IS NOT NULL AND "s"."purchase_price" IS NOT NULL THEN "s"."purchase_price" ELSE 0 END) AS "paid_where_market",
    SUM(CASE WHEN "c"."market_new" IS NOT NULL AND "s"."purchase_price" IS NOT NULL THEN "c"."market_new" ELSE 0 END) AS "market_where_paid",
    SUM(CASE WHEN "c"."market_used" IS NOT NULL AND "s"."purchase_price" IS NOT NULL THEN "s"."purchase_price" ELSE 0 END) AS "paid_where_market_used",
    SUM(CASE WHEN "c"."market_used" IS NOT NULL AND "s"."purchase_price" IS NOT NULL THEN "c"."market_used" ELSE 0 END) AS "market_used_where_paid",
    -- Currency the BrickLink market values are stored in (consistent across
    -- sets as they are all requested in the same currency); MAX picks a non-null.
    MAX("c"."market_currency") AS "market_currency"
FROM "bricktracker_sets" AS "s"
LEFT JOIN (
    SELECT
        "set_ref",
        json_extract("payload", '$.legoCom{{ region }}.retailPrice') AS "msrp",
        json_extract("price_payload", '$.new_avg') AS "market_new",
        json_extract("price_payload", '$.used_avg') AS "market_used",
        json_extract("price_payload", '$.currency_code') AS "market_currency"
    FROM "sidecar_set_cache"
) AS "c" ON "c"."set_ref" = "s"."set"
