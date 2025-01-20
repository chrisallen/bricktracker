BEGIN transaction;

DROP TABLE IF EXISTS "wishlist";
DROP TABLE IF EXISTS "sets";
DROP TABLE IF EXISTS "inventory";
DROP TABLE IF EXISTS "minifigures";
DROP TABLE IF EXISTS "missing";

COMMIT;