import logging
from typing import Any, TYPE_CHECKING

from flask import url_for

from .exceptions import DatabaseException
from .metadata import BrickMetadata
from .sql import BrickSQL
if TYPE_CHECKING:
    from .wish import BrickWish

logger = logging.getLogger(__name__)


# Lego wish owner metadata
class BrickWishOwner(BrickMetadata):
    kind: str = 'owner'

    # Wish state endpoint
    wish_state_endpoint: str = 'wish.update_owner'

    # Queries
    update_wish_state_query: str = 'wish/metadata/owner/update/state'

    # Update the selected state of this metadata item for a wish
    def update_wish_state(
        self,
        brickset: 'BrickWish',
        /,
        *,
        json: Any | None = None,
        state: Any | None = None
    ) -> Any:
        if state is None and json is not None:
            state = json.get('value', False)

        parameters = self.sql_parameters()
        parameters['set'] = brickset.fields.set
        parameters['state'] = state

        rows, _ = BrickSQL().execute_and_commit(
            self.update_wish_state_query,
            parameters=parameters,
            name=self.as_column(),
        )

        if rows != 1:
            raise DatabaseException('Could not update the {kind} "{name}" state for wish {set}'.format(  # noqa: E501
                kind=self.kind,
                name=self.fields.name,
                set=brickset.fields.set,
            ))

        # Info
        logger.info('{kind} "{name}" state changed to "{state}" for wish {set}'.format(  # noqa: E501
            kind=self.kind,
            name=self.fields.name,
            state=state,
            set=brickset.fields.set,
        ))

        return state

    # URL to change the selected state of this metadata item for a wish
    def url_for_wish_state(self, set: str, /) -> str:
        return url_for(
            self.wish_state_endpoint,
            set=set,
            metadata_id=self.fields.id
        )
