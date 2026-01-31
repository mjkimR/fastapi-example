from abc import abstractmethod
from typing import Any, TypedDict
import uuid
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from app.base.repos.base import ModelType
from app.base.services.base import (
    BaseCreateHooks,
    BaseDeleteHooks,
    BaseUpdateHooks,
    TContextKwargs,
)
from app.features.outbox.repos import OutboxRepository
from app.features.outbox.schemas import OutboxCreate, OutboxIdentityDict


class NotificationEventTypeDict(TypedDict):
    CREATE: str
    UPDATE: str
    DELETE: str


class NotificationOutboxHook(
    BaseCreateHooks,
    BaseUpdateHooks,
    BaseDeleteHooks,
):
    @abstractmethod
    def _get_notification_payload(
        self,
        obj: Any,
        context: TContextKwargs,
        outbox_identity: OutboxIdentityDict,
    ) -> dict[str, Any]:
        """
        Generate the notification payload for outbox events.
        JSON-serializable dictionary containing the notification payload.
        """
        pass

    @property
    @abstractmethod
    def outbox_repo(self) -> OutboxRepository:
        pass

    @property
    @abstractmethod
    def notification_event_type_dict(self) -> NotificationEventTypeDict:
        pass

    async def _post_create(
        self, session: AsyncSession, obj: ModelType, context: TContextKwargs
    ) -> ModelType:
        outbox_identity: OutboxIdentityDict = {
            "aggregate_type": self.repo.model_name(),
            "aggregate_id": str(obj.id),
            "event_type": self.notification_event_type_dict["CREATE"],
        }
        await self.outbox_repo.create(
            session=session,
            obj_in=OutboxCreate(
                **outbox_identity,
                payload=self._get_notification_payload(obj, context, outbox_identity),
            ),
        )

        return await super()._post_create(session, obj, context)

    async def _post_update(
        self, session: AsyncSession, obj: ModelType, context: TContextKwargs
    ) -> ModelType:
        outbox_identity: OutboxIdentityDict = {
            "aggregate_type": self.repo.model_name(),
            "aggregate_id": str(obj.id),
            "event_type": self.notification_event_type_dict["UPDATE"],
        }
        await self.outbox_repo.create(
            session=session,
            obj_in=OutboxCreate(
                **outbox_identity,
                payload=self._get_notification_payload(obj, context, outbox_identity),
            ),
        )

        return await super()._post_update(session, obj, context)

    @asynccontextmanager
    async def _context_delete(
        self, session: AsyncSession, obj_id: uuid.UUID, context: TContextKwargs
    ):
        """Use context manager to ensure outbox event is created after deletion."""
        async with super()._context_delete(session, obj_id, context):
            obj = await self.repo.get_by_pk(session, obj_id)
            outbox_identity: OutboxIdentityDict = {
                "aggregate_type": self.repo.model_name(),
                "aggregate_id": str(obj_id),
                "event_type": self.notification_event_type_dict["DELETE"],
            }

            if obj:
                payload = self._get_notification_payload(obj, context, outbox_identity)
            else:
                payload = None

            yield

            if payload is not None:
                await self.outbox_repo.create(
                    session=session,
                    obj_in=OutboxCreate(
                        **outbox_identity,
                        payload=payload,
                    ),
                )
