SELECT
    "bricktracker_set_checkboxes"."id",
    "bricktracker_set_checkboxes"."name",
    "bricktracker_set_checkboxes"."displayed_on_grid"
FROM "bricktracker_set_checkboxes"

{% block where %}{% endblock %}