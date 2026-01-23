from typing import Any, Annotated

from fastapi import Query, Depends


def pagination_params(
        offset: int = Query(default=0, description="offset for pagination"),
        limit: int = Query(default=100, le=200, description="limit for pagination")
) -> dict[str, Any]:
    return {
        "offset": offset,
        "limit": limit
    }


PaginationParam = Annotated[dict, Depends(pagination_params)]
