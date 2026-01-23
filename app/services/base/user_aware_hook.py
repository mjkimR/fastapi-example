from typing import Any, Required

from app.services.base.base import BaseCreateHooks, BaseUpdateHooks, BaseContextKwargs


class UserContextKwargs(BaseContextKwargs):
    """User tracking context kwargs."""
    user_id: Required[str]


class UserAwareHooksMixin(BaseCreateHooks, BaseUpdateHooks):
    def _prepare_create_fields(self, obj_data, context: UserContextKwargs) -> dict[str, Any]:
        base = super()._prepare_create_fields(obj_data, context)
        if user_id := context.get("user_id"):
            return {**base, "created_by": user_id, "updated_by": user_id}
        return base

    def _prepare_update_fields(self, obj_data, context: UserContextKwargs) -> dict[str, Any]:
        base = super()._prepare_update_fields(obj_data, context)
        if user_id := context.get("user_id"):
            return {**base, "updated_by": user_id}
        return base
