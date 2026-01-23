import uuid
from datetime import datetime, timezone
from typing import Optional, Union, Generic, Sequence, TypeVar, Any

from sqlalchemy import (
    select, update, delete, literal, func,
)
from sqlalchemy import Column, inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.elements import ColumnElement, UnaryExpression
from pydantic import BaseModel

from app.base.schemas.paginated import PaginatedList

ModelType = TypeVar("ModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

PrimaryKeyType = Union[Sequence[Union[str, int, uuid.UUID]], Union[str, int, uuid.UUID]]
WhereClause = ColumnElement[bool] | Sequence[ColumnElement[bool]]


class BaseRepository(
    Generic[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
    ]
):
    model: type[ModelType]
    default_order_by_col: Optional[str] = "updated_at"
    is_deleted_column: Optional[str] = "is_deleted"
    deleted_at_column: Optional[str] = "deleted_at"

    def __init__(self):
        self._primary_keys = self._get_primary_keys(self.model)

    def _get_primary_keys(self, model: type[ModelType]) -> Sequence[Column]:
        """Get the primary key of a SQLAlchemy model."""
        inspector_result = sa_inspect(model)
        if inspector_result is None:  # pragma: no cover
            raise ValueError("Model inspection failed, resulting in None.")
        primary_key_columns: Sequence[Column] = inspector_result.mapper.primary_key
        return primary_key_columns

    def _get_primary_key_filters(self, pk: PrimaryKeyType):
        if not self._primary_keys:
            raise ValueError("No primary key defined for this model.")

        if not isinstance(pk, Sequence) or isinstance(pk, str):
            pk_values = [pk]
        else:
            pk_values = pk

        if len(self._primary_keys) != len(pk_values):
            raise ValueError(
                f"Incorrect number of primary key values provided. Expected {len(self._primary_keys)}, got {len(pk_values)}.")

        return [
            pk_col == value
            for pk_col, value in zip(self._primary_keys, pk_values)
        ]

    def _select(
            self,
            where: WhereClause = (),
            order_by: Sequence[UnaryExpression] = ()
    ) -> Select:
        stmt = select(self.model)
        if where is not None:
            if isinstance(where, Sequence):
                if where:
                    stmt = stmt.where(*where)
            else:
                stmt = stmt.where(where)

        if order_by is not None and order_by != ():
            stmt = stmt.order_by(*order_by)
        else:
            default_order_by = getattr(self.model, self.default_order_by_col, None)
            if default_order_by is not None:
                stmt = stmt.order_by(default_order_by.desc())
        return stmt

    async def get(
            self,
            session: AsyncSession,
            where: WhereClause = (),
            order_by: Sequence[UnaryExpression] = ()
    ) -> Optional[ModelType]:
        stmt = self._select(where, order_by)
        stmt = stmt.limit(1)

        db_row = await session.execute(stmt)
        return db_row.scalar_one_or_none()

    async def get_by_pk(
            self,
            session: AsyncSession,
            pk: PrimaryKeyType,
            where: WhereClause = (),
            order_by: Sequence[UnaryExpression] = ()
    ) -> Optional[ModelType]:
        filters = self._get_primary_key_filters(pk)
        return await self.get(session, where=filters or where, order_by=order_by)

    async def exists(
            self,
            session: AsyncSession,
            where: WhereClause = (),
    ) -> bool:
        stmt = select(literal(1))  # select 1
        stmt = stmt.select_from(self.model)
        if where is not None:
            stmt = stmt.where(where)
        stmt = stmt.limit(1)

        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(
            self,
            session: AsyncSession,
            obj_in: CreateSchemaType,
            **update_fields: Any,
    ) -> ModelType:
        obj_dict = obj_in.model_dump()
        obj_dict.update(update_fields)
        db_obj: ModelType = self.model(**obj_dict)
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def get_multi(
            self,
            session: AsyncSession,
            offset: int = 0,
            limit: Optional[int] = 100,
            where: WhereClause = (),
            order_by: Sequence[UnaryExpression] = (),
    ) -> PaginatedList[ModelType]:
        if limit is not None and limit < 0:
            raise ValueError("Limit must be non-negative.")
        if offset < 0:
            raise ValueError("Offset must be non-negative.")

        # Total count
        count_stmt = select(func.count()).select_from(self.model)
        if where is not None:
            count_stmt = count_stmt.where(*where)
        total_count_result = await session.execute(count_stmt)
        total_count = total_count_result.scalar_one()

        # Query
        stmt = self._select(where=where, order_by=order_by)
        stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await session.execute(stmt)
        data = result.scalars().all()

        return PaginatedList(
            items=data,
            total_count=total_count,
            offset=offset,
            limit=limit,
        )

    async def get_all(
            self,
            session: AsyncSession,
            where: WhereClause = (),
            order_by: Sequence[UnaryExpression] = ()
    ) -> Sequence[ModelType]:
        res = await self.get_multi(
            session,
            offset=0,
            limit=None,
            where=where,
            order_by=order_by,
        )
        return res.items

    async def update_by_pk(
            self,
            session: AsyncSession,
            pk: PrimaryKeyType,
            obj_in: Union[UpdateSchemaType, dict[str, Any]],
            return_updated_obj: bool = True,
            **update_fields: Any,
    ) -> Optional[ModelType]:
        filters = self._get_primary_key_filters(pk)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # exclude_unset=True
            update_data = obj_in.model_dump(exclude_unset=True)
        update_data.update(update_fields)

        if not update_data:
            raise ValueError("Update data cannot be empty.")

        model_columns = {col.key for col in sa_inspect(self.model).mapper.columns}
        extra_fields = set(update_data.keys()) - model_columns
        if extra_fields:
            raise ValueError(f"Extra fields provided that are not in the model {self.model.__name__}: {extra_fields}")

        stmt = update(self.model).filter(*filters).values(**update_data)
        result = await session.execute(stmt)

        if result.rowcount == 0:
            return None
        await session.flush()
        return await self.get(session, where=filters) if return_updated_obj else None

    async def delete_by_pk(
            self,
            session: AsyncSession,
            pk: PrimaryKeyType,
            soft_delete: bool = False,
    ) -> bool:
        filters = self._get_primary_key_filters(pk)
        if soft_delete:
            has_is_deleted = hasattr(self.model, self.is_deleted_column)

            if not has_is_deleted:
                raise ValueError(
                    f"Soft delete requires the column '{self.is_deleted_column}' in model {self.model.__name__}.")

            if self.deleted_at_column and not hasattr(self.model, self.deleted_at_column):
                raise ValueError(
                    f"Soft delete is configured to use '{self.deleted_at_column}', but it's missing in model {self.model.__name__}."
                )

            update_values: dict[str, Any] = {self.is_deleted_column: True}
            if self.deleted_at_column and hasattr(self.model, self.deleted_at_column):
                update_values[self.deleted_at_column] = datetime.now(timezone.utc)

            stmt = update(self.model).filter(*filters).values(**update_values)
        else:
            stmt = delete(self.model).filter(*filters)

        result = await session.execute(stmt)

        deleted_or_updated = int(result.rowcount) > 0
        if deleted_or_updated:
            await session.flush()
        return deleted_or_updated
