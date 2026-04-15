-- Track that we've seen/updated this part during refresh
INSERT OR IGNORE INTO temp_refresh_parts (id, part, color, figure, spare)
VALUES (:id, :part, :color, :figure, :spare)
