import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.outbox.models import EventStatus
from app.features.outbox.repos import OutboxRepository
from app.features.outbox.schemas import OutboxCreate
from app.features.outbox.services import OutboxService


class TestOutboxServiceIntegration:
    """Integration app_tests for OutboxService."""

    @pytest.fixture
    def repo(self) -> OutboxRepository:
        return OutboxRepository()

    @pytest.fixture
    def service(self, repo: OutboxRepository) -> OutboxService:
        return OutboxService(repo=repo)

    @pytest.mark.asyncio
    async def test_add_event(self, session: AsyncSession, service: OutboxService):
        event_data = OutboxCreate(
            aggregate_type="test",
            aggregate_id=str(uuid.uuid4()),
            event_type="TEST_ADDED",
            payload={"test_key": "test_value"},
        )
        created_event = await service.add_event(session, event_data)
        await session.commit()

        assert created_event is not None
        assert created_event.id is not None
        assert created_event.event_type == "TEST_ADDED"
        assert created_event.status == EventStatus.PENDING

        retrieved_event = await service.repo.get_by_pk(session, created_event.id)
        assert retrieved_event == created_event

    @pytest.mark.asyncio
    async def test_update_event_status(self, session: AsyncSession, service: OutboxService):
        event_data = OutboxCreate(
            aggregate_type="test",
            aggregate_id=str(uuid.uuid4()),
            event_type="TEST_STATUS_UPDATE",
            payload={},
        )
        created_event = await service.add_event(session, event_data)
        await session.commit()

        updated_event = await service.update_event_status(session, created_event.id, EventStatus.COMPLETED)
        await session.commit()

        assert updated_event is not None
        assert updated_event.id == created_event.id
        assert updated_event.status == EventStatus.COMPLETED
        assert updated_event.processed_at is not None

        retrieved_event = await service.repo.get_by_pk(session, created_event.id)
        assert retrieved_event is not None
        assert retrieved_event.status == EventStatus.COMPLETED
