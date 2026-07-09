from typing import Any

from .exceptions import ErrorException
from .sql import BrickSQL

# Per-bag part state (checked/missing) for sets with a sidecar bag inventory.
# The bag composition itself is never stored; only the user's progress is
# (keyed by set record id, bag number and the part identity tuple).
# Plain functions on purpose: a BrickRecord model is overkill for a
# two-column state table.


# Update one state field ('checked' or 'missing') from a changer.js payload.
# Returns the stored value.
def update_state(
    set_id: str,
    bag: str,
    part: str,
    color: int,
    spare: int,
    state: str,
    json: Any | None,
    /,
) -> Any:
    value = json.get('value', '') if json else ''

    if state == 'checked':
        value = bool(value)
    elif state == 'missing':
        # Same rules as BrickPart.update_problem: positive integer, '' -> 0
        try:
            if value == '':
                value = 0

            value = int(value)

            if value < 0:
                value = 0
        except Exception:
            raise ErrorException('"{value}" is not a valid integer'.format(
                value=value
            ))
    else:
        raise ErrorException('"{state}" is not a valid bag part state'.format(
            state=state
        ))

    BrickSQL().execute_and_commit(
        'bag_part/update/{state}'.format(state=state),
        parameters={
            'id': set_id,
            'bag': bag,
            'part': part,
            'color': color,
            'spare': spare,
            state: value,
        },
    )

    return value


# All stored state for one set:
# {(bag, part, color, spare): {'checked': bool, 'missing': int}}
def list_state(
    set_id: str,
    /,
) -> dict[tuple[str, str, int, int], dict[str, Any]]:
    rows = BrickSQL().fetchall(
        'bag_part/list',
        parameters={'id': set_id},
    )

    return {
        (row['bag'], row['part'], row['color'], row['spare']): {
            'checked': bool(row['checked']),
            'missing': row['missing'],
        }
        for row in rows
    }
