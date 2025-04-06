import inspect
from datetime import datetime, timezone
from typing import Optional, Union, Generic, Sequence, TypeVar, Any

from sqlalchemy import (
    select, update, delete, inspect, literal, func,
)
from sqlalchemy import Column, inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Any)

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

GetMultiResponseModel = dict[str, Union[list[ModelType], int]]


class BaseRepository(
    Generic[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
    ]
):
    def __init__(
            self,
            model: type[ModelType],
            is_deleted_column: str = "is_deleted",
            deleted_at_column: str = "deleted_at",
            updated_at_column: str = "updated_at",
            default_order_by_col: Optional[str] = "updated_at",
    ) -> None:
        self.model = model
        self.is_deleted_column = is_deleted_column
        self.deleted_at_column = deleted_at_column
        self.updated_at_column = updated_at_column
        self.default_order_by_col = default_order_by_col

        self._primary_keys = self._get_primary_keys(self.model)

    def _get_primary_keys(self, model: type[ModelType]) -> Sequence[Column]:
        """Get the primary key of a SQLAlchemy model."""
        inspector_result = sa_inspect(model)
        if inspector_result is None:  # pragma: no cover
            raise ValueError("Model inspection failed, resulting in None.")
        primary_key_columns: Sequence[Column] = inspector_result.mapper.primary_key
        return primary_key_columns

    def _select(self, where=None, order_by=None) -> Select:
        stmt = select(self.model)
        if where is not None:
            stmt = stmt.where(where)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        else:
            default_order_by = getattr(self.model, self.default_order_by_col, None)
            if default_order_by is not None:
                stmt = stmt.order_by(default_order_by.desc())
        return stmt

    async def get(
            self,
            db: AsyncSession,
            where=None,
            order_by=None,
    ) -> Optional[ModelType]:
        stmt = self._select(where, order_by)
        stmt = stmt.limit(1)

        db_row = await db.execute(stmt)
        result = db_row.mappings().first()
        return self.model(**result) if result else None

    async def exists(
            self,
            db: AsyncSession,
            where=None,
    ) -> bool:
        stmt = select(literal(1))  # select 1
        stmt = stmt.select_from(self.model)
        if where is not None:
            stmt = stmt.where(where)
        stmt = stmt.limit(1)

        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(
            self,
            db: AsyncSession,
            obj_in: CreateSchemaType,
            commit: bool = True
    ) -> ModelType:
        obj_dict = obj_in.model_dump()
        db_obj: ModelType = self.model(**obj_dict)
        db.add(db_obj)
        if commit:
            await db.commit()
            await db.refresh(db_obj)
        else:
            await db.flush()
            await db.refresh(db_obj)
        return db_obj

    async def get_multi(
            self,
            db: AsyncSession,
            offset: int = 0,
            limit: Optional[int] = 100,
            where=None,
            order_by=None,
    ) -> GetMultiResponseModel[ModelType]:
        if limit is not None and limit < 0:
            raise ValueError("Limit must be non-negative.")
        if offset < 0:
            raise ValueError("Offset must be non-negative.")

        # Total count
        count_stmt = select(func.count()).select_from(self.model)
        if where is not None:
            count_stmt = count_stmt.where(where)
        total_count_result = await db.execute(count_stmt)
        total_count = total_count_result.scalar_one()

        # Query
        stmt = self._select(where=where, order_by=order_by)
        stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await db.execute(stmt)
        data = [self.model(**row) for row in result.mappings()]

        return {"data": data, "total_count": total_count}

    async def update_by_pk(
            self,
            db: AsyncSession,
            pk: Union[Sequence[Union[str, int]], Union[str, int]],
            obj_in: Union[UpdateSchemaType, dict[str, Any]],
            commit: bool = True,
    ) -> Optional[ModelType]:
        if not self._primary_keys:
            raise ValueError("No primary key defined for this model.")

        if not isinstance(pk, Sequence) or isinstance(pk, str):
            pk_values = [pk]
        else:
            pk_values = pk

        if len(self._primary_keys) != len(pk_values):
            raise ValueError(
                f"Incorrect number of primary key values provided. Expected {len(self._primary_keys)}, got {len(pk_values)}.")

        filters = [
            pk_col == value for pk_col, value in zip(self._primary_keys, pk_values)
        ]

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if not update_data:
            get_filters = [pk_col == value for pk_col, value in zip(self._primary_keys, pk_values)]
            existing_obj = await self.get(db, where=get_filters)
            return existing_obj

        model_columns = {col.key for col in sa_inspect(self.model).mapper.columns}
        extra_fields = set(update_data.keys()) - model_columns
        if extra_fields:
            raise ValueError(f"Extra fields provided that are not in the model {self.model.__name__}: {extra_fields}")

        updated_at_col_name = self.updated_at_column
        if updated_at_col_name in model_columns and updated_at_col_name not in update_data:
            update_data[updated_at_col_name] = datetime.now(timezone.utc)

        stmt = update(self.model).filter(*filters).values(**update_data)
        result = await db.execute(stmt)

        if commit:
            await db.commit()
            get_filters = [pk_col == value for pk_col, value in zip(self._primary_keys, pk_values)]
            updated_obj = await self.get(db, where=get_filters)

        else:
            await db.flush()
            get_filters = [pk_col == value for pk_col, value in zip(self._primary_keys, pk_values)]
            updated_obj = await self.get(db, where=get_filters)

        return updated_obj

    async def delete_by_pk(
            self,
            db: AsyncSession,
            pk: Union[Sequence[Union[str, int]], Union[str, int]],
            soft_delete: bool = False,
            commit: bool = True,
    ) -> bool:
        if not self._primary_keys:
            raise ValueError("No primary key defined for this model.")

        if not isinstance(pk, Sequence) or isinstance(pk, str):
            pk_values = [pk]
        else:
            pk_values = pk

        if len(self._primary_keys) != len(pk_values):
            raise ValueError(
                f"Incorrect number of primary key values provided. Expected {len(self._primary_keys)}, got {len(pk_values)}.")

        filters = [
            pk_col == value for pk_col, value in zip(self._primary_keys, pk_values)
        ]

        if soft_delete:
            # Soft delete 컬럼 존재 여부 확인
            has_is_deleted = hasattr(self.model, self.is_deleted_column)
            has_deleted_at = hasattr(self.model, self.deleted_at_column)

            if not has_is_deleted:
                raise ValueError(
                    f"Soft delete requires the column '{self.is_deleted_column}' in model {self.model.__name__}.")

            update_values = {self.is_deleted_column: True}
            if has_deleted_at:
                update_values[self.deleted_at_column] = datetime.now(timezone.utc)
            stmt = update(self.model).filter(*filters).values(**update_values)
        else:
            stmt = delete(self.model).filter(*filters)

        result = await db.execute(stmt)

        deleted_or_updated = result.rowcount() > 0

        if commit and deleted_or_updated:
            await db.commit()
        elif not commit and deleted_or_updated:
            await db.flush()

        return deleted_or_updated
