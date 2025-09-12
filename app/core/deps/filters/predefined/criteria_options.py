from app.core.deps.filters.generic.criteria_exact import GenericExactCriteria
from app.core.deps.filters.generic.criteria_ilike import GenericILikeCriteria
from app.core.deps.filters.generic.criteria_time import GenericTimeRangeCriteria


class NameFieldCriteria(GenericILikeCriteria):
    """Filter implementation for name field using case-insensitive partial matching.

    Provides a convenient filter for the common 'name' field.
    """

    def __init__(self, field="name", alias="name"):
        super().__init__(field, alias)


class NameFieldExactCriteria(GenericExactCriteria):
    """Filter implementation for exact name matching.

    Provides a convenient filter for exact matching on the 'name' field.
    """

    def __init__(self, field="name", alias="exact_name"):
        super().__init__(field, alias)


class CreatorFieldCriteria(GenericExactCriteria):
    """Filter implementation for creator field using exact matching.

    Provides a convenient filter for the common 'created_by' field.
    """

    def __init__(self, field="created_by", alias="created_by"):
        super().__init__(field, alias)


class CreationTimeRangeCriteria(GenericTimeRangeCriteria):
    """Filter implementation for creation time range.

    Provides a convenient filter for the common 'created_at' datetime field.
    """

    def __init__(self, field="created_at", alias="created_at"):
        super().__init__(field, alias)
