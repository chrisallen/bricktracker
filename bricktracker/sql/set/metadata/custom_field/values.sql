{#
  Distinct values already in use for one custom field, to populate its filter
  dropdown. "column" is the field's own as_column() value, which never comes from
  user input (it is only ever built from a known BrickSetCustomField), so it is safe
  to interpolate as an identifier here.
#}
SELECT DISTINCT "{{ column }}" AS "value"
FROM "bricktracker_set_custom_fields"
WHERE "{{ column }}" IS NOT NULL AND "{{ column }}" != ''
ORDER BY "value"
