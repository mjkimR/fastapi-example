from functools import lru_cache
from typing import Generic, Any, TypedDict, Optional
from typing_extensions import TypeVar
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.repos.base import BaseRepository, ModelType, CreateSchemaType, UpdateSchemaType
from app.schemas.base import PaginatedList
from pydantic import TypeAdapter, ValidationError


class BaseContextKwargs(TypedDict):
    """Base context kwargs (empty, for extension)."""
    pass


TRepo = TypeVar("TRepo", bound=BaseRepository)
TContextKwargs = TypeVar("TContextKwargs", bound=BaseContextKwargs, default=BaseContextKwargs)


@lru_cache
def _get_adapter(cast_to: type[TContextKwargs]) -> TypeAdapter[TContextKwargs]:
    """Get Pydantic TypeAdapter for the given context type."""
    return TypeAdapter(cast_to)


def _ensure_context(context: Optional[TContextKwargs], cast_to: type[TContextKwargs] = BaseContextKwargs) -> TContextKwargs:
    """
    Ensure context is not None.

    If context is None, returns an empty dict cast to TContextKwargs.
    Note: If TContextKwargs has required fields, caller must provide a valid context.
    """
    if context is None:
        context = {}
    # Use Pydantic TypeAdapter to validate and cast the context
    try:
        adapter = _get_adapter(cast_to)
        return adapter.validate_python(context)
    except ValidationError as e:
        raise ValueError(f"Invalid context provided: {e}") from e


# ============================================================
# Create Hooks & Mixin
# ============================================================

class BaseCreateHooks:
    """Hook methods for Create operations."""

    def _prepare_create_fields(self, obj_data: CreateSchemaType, context: TContextKwargs) -> dict[str, Any]:
        """Hook to prepare additional fields before create."""
        return {}

    async def _post_create(self, session: AsyncSession, obj: ModelType, context: TContextKwargs) -> ModelType:
        """Hook executed after create."""
        return obj


class BaseCreateServiceMixin(BaseCreateHooks, Generic[TRepo, ModelType, CreateSchemaType, TContextKwargs]):
    """
    Create operation Mixin with hooks.

    Usage:
        await service.create(session, obj_data, context={})
    """
    repo: TRepo
    context_model: type[TContextKwargs] = BaseContextKwargs

    async def create(
            self, session: AsyncSession, obj_data: CreateSchemaType, context: Optional[TContextKwargs] = None
    ) -> ModelType:
        ctx = _ensure_context(context, self.context_model)
        extra_fields = self._prepare_create_fields(obj_data, context=ctx)
        obj = await self.repo.create(session, obj_in=obj_data, **extra_fields)
        return await self._post_create(session, obj, context=ctx)


# ============================================================
# Update Hooks & Mixin
# ============================================================

class BaseUpdateHooks:
    """Hook methods for Update operations."""

    def _prepare_update_fields(self, obj_data: UpdateSchemaType, context: TContextKwargs) -> dict[str, Any]:
        """Hook to prepare additional fields before update."""
        return {}

    async def _post_update(self, session: AsyncSession, obj: ModelType, context: TContextKwargs) -> ModelType:
        """Hook executed after update."""
        return obj


class BaseUpdateServiceMixin(BaseUpdateHooks, Generic[TRepo, ModelType, UpdateSchemaType, TContextKwargs]):
    """
    Update operation Mixin with hooks.

    Usage:
        await service.update(session, obj_id, obj_data, context={})
    """
    repo: TRepo
    context_model: type[TContextKwargs] = BaseContextKwargs

    async def update(
            self, session: AsyncSession, obj_id: uuid.UUID, obj_data: UpdateSchemaType,
            context: Optional[TContextKwargs] = None
    ) -> ModelType:
        ctx = _ensure_context(context, self.context_model)
        extra_fields = self._prepare_update_fields(obj_data, context=ctx)
        obj = await self.repo.update_by_pk(session, pk=obj_id, obj_in=obj_data, **extra_fields)
        return await self._post_update(session, obj, context=ctx)


# ============================================================
# Delete Hooks & Mixin
# ============================================================

class BaseDeleteHooks:
    """Hook methods for Delete operations."""

    async def _pre_delete(self, session: AsyncSession, obj_id: uuid.UUID, context: TContextKwargs) -> None:
        """Hook executed before delete (validation, cascade handling, etc.)."""
        pass

    async def _post_delete(self, session: AsyncSession, obj_id: uuid.UUID, result: bool, context: TContextKwargs) -> bool:
        """Hook executed after delete."""
        return result


class BaseDeleteServiceMixin(BaseDeleteHooks, Generic[TRepo, ModelType, TContextKwargs]):
    """
    Delete operation Mixin with hooks.

    Usage:
        await service.delete(session, obj_id, context={})
    """
    repo: TRepo
    context_model: type[TContextKwargs] = BaseContextKwargs

    async def delete(
            self, session: AsyncSession, obj_id: uuid.UUID, context: Optional[TContextKwargs] = None
    ) -> bool:
        ctx = _ensure_context(context, self.context_model)
        await self._pre_delete(session, obj_id, context=ctx)
        result = await self.repo.delete_by_pk(session, pk=obj_id)
        return await self._post_delete(session, obj_id, result, context=ctx)


# ============================================================
# Get (Single) Hooks & Mixin
# ============================================================

class BaseGetHooks:
    """Hook methods for Get (single item) operations."""

    async def _post_get(self, session: AsyncSession, obj: ModelType | None, context: TContextKwargs) -> ModelType | None:
        """Hook executed after get (data transformation, etc.)."""
        return obj


class BaseGetServiceMixin(BaseGetHooks, Generic[TRepo, ModelType, TContextKwargs]):
    """
    Get (single item) operation Mixin with hooks.

    Usage:
        await service.get(session, obj_id, context={})
    """
    repo: TRepo
    context_model: type[TContextKwargs] = BaseContextKwargs

    async def get(
            self, session: AsyncSession, obj_id: uuid.UUID, context: Optional[TContextKwargs] = None
    ) -> ModelType | None:
        ctx = _ensure_context(context, self.context_model)
        obj = await self.repo.get_by_pk(session, pk=obj_id)
        return await self._post_get(session, obj, context=ctx)


# ============================================================
# Get Multi (List) Hooks & Mixin
# ============================================================

class BaseGetMultiHooks:
    """Hook methods for Get Multi (list) operations."""

    def _prepare_get_multi_filters(self, context: TContextKwargs) -> list[Any]:
        """Hook to prepare additional filter conditions for list queries."""
        return []

    async def _post_get_multi(
            self, session: AsyncSession, result: PaginatedList[ModelType], context: TContextKwargs
    ) -> PaginatedList[ModelType]:
        """Hook executed after get multi (data transformation, etc.)."""
        return result


class BaseGetMultiServiceMixin(BaseGetMultiHooks, Generic[TRepo, ModelType, TContextKwargs]):
    """
    Get Multi (list) operation Mixin with hooks.

    Usage:
        await service.get_multi(session, offset=0, limit=100, context={})
    """
    repo: TRepo
    context_model: type[TContextKwargs] = BaseContextKwargs

    async def get_multi(
            self, session: AsyncSession,
            offset: int = 0, limit: int = 100,
            order_by=None, where=None,
            context: Optional[TContextKwargs] = None
    ) -> PaginatedList[ModelType]:
        ctx = _ensure_context(context, self.context_model)
        extra_filters = self._prepare_get_multi_filters(context=ctx)

        # Merge where conditions
        if where is None:
            where = extra_filters
        elif isinstance(where, list):
            where = where + extra_filters
        elif extra_filters:
            where = [where] + extra_filters

        result = await self.repo.get_multi(
            session, offset=offset, limit=limit, where=where, order_by=order_by
        )
        return await self._post_get_multi(session, result, context=ctx)


# ============================================================
# Combined Base Service Mixin (Full CRUD)
# ============================================================

class BaseCRUDServiceMixin(
    BaseCreateServiceMixin[TRepo, ModelType, CreateSchemaType, TContextKwargs],
    BaseUpdateServiceMixin[TRepo, ModelType, UpdateSchemaType, TContextKwargs],
    BaseDeleteServiceMixin[TRepo, ModelType, TContextKwargs],
    BaseGetServiceMixin[TRepo, ModelType, TContextKwargs],
    BaseGetMultiServiceMixin[TRepo, ModelType, TContextKwargs],
    Generic[TRepo, ModelType, CreateSchemaType, UpdateSchemaType, TContextKwargs]
):
    """
    Combined Mixin providing full CRUD operations.

    All CRUD operation hooks can be overridden.
    """
    pass
