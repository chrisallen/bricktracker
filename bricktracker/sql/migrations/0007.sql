-- description: Renaming various complicated field names to something simpler

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Rename sets table
ALTER TABLE "bricktracker_sets" RENAME TO "bricktracker_sets_old";

-- Re-Create a Bricktable set table with the simplified name
CREATE TABLE "bricktracker_sets" (
    "id" TEXT NOT NULL,
    "set" TEXT NOT NULL,
    PRIMARY KEY("id"),
    FOREIGN KEY("set") REFERENCES "rebrickable_sets"("set")
);

-- Insert existing sets into the new table
INSERT INTO "bricktracker_sets" (
    "id",
    "set"
)
SELECT
    "bricktracker_sets_old"."id",
    "bricktracker_sets_old"."rebrickable_set"
FROM "bricktracker_sets_old";

-- Rename status table
ALTER TABLE "bricktracker_set_statuses" RENAME TO "bricktracker_set_statuses_old";

-- Re-create a table for the status of each checkbox
CREATE TABLE "bricktracker_set_statuses" (
    "id" TEXT NOT NULL,
    {% if structure %}{{ structure }},{% endif %}
    PRIMARY KEY("id"),
    FOREIGN KEY("id") REFERENCES "bricktracker_sets"("id")
);

-- Insert existing status into the new table
INSERT INTO "bricktracker_set_statuses" (
    {% if targets %}{{ targets }},{% endif %}
    "id"
)
SELECT
    {% if sources %}{{ sources }},{% endif %}
    "bricktracker_set_statuses_old"."bricktracker_set_id"
FROM "bricktracker_set_statuses_old";

-- Delete the original tables
DROP TABLE "bricktracker_set_statuses_old";
DROP TABLE "bricktracker_sets_old";

COMMIT;