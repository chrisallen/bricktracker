-- Create temporary table to track which parts are being refreshed
CREATE TEMPORARY TABLE IF NOT EXISTS temp_refresh_parts (
    id TEXT NOT NULL,
    part TEXT NOT NULL,
    color INTEGER NOT NULL,
    figure TEXT,
    spare BOOLEAN NOT NULL,
    PRIMARY KEY (id, part, color, figure, spare)
)
