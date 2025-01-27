-- description: Migrate the Bricktracker minifigures

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Create a Bricktable minifigures table: an amount of minifigures linked to a Bricktracker set
CREATE TABLE "bricktracker_minifigures" (
    "bricktracker_set_id" TEXT NOT NULL,
    "rebrickable_figure" TEXT NOT NULL,
    "quantity" INTEGER NOT NULL,
    PRIMARY KEY("bricktracker_set_id", "rebrickable_figure"),
    FOREIGN KEY("bricktracker_set_id") REFERENCES "bricktracker_sets"("id"),
    FOREIGN KEY("rebrickable_figure") REFERENCES "rebrickable_minifigures"("figure")
);

-- Insert existing sets into the new table
INSERT INTO "bricktracker_minifigures" (
    "bricktracker_set_id",
    "rebrickable_figure",
    "quantity"
)
SELECT
    "minifigures"."u_id",
    "minifigures"."fig_num",
    "minifigures"."quantity"
FROM "minifigures";

-- Rename the original table (don't delete it yet?)
ALTER TABLE "minifigures" RENAME TO "minifigures_old";

COMMIT;