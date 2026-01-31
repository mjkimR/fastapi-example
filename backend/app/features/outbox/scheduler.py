import logging
import datetime
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.base.schemas.event import DomainEvent
from app.core.database.transaction import AsyncTransaction
from app.features.outbox.repos import OutboxRepository
from app.features.outbox.models import EventStatus
from app.features.outbox.registry import dispatch_event
import app.features.memos.consumers.event_handlers  # noqa: F401

logger = logging.getLogger(__name__)


async def process_outbox_events_job():
    """
    A job function to be run by the scheduler.

    Simply processes pending outbox events. (Not ideal for production use. Just a demo.)

    TODO: more sophisticated scheduling, backoff, batching, exception handling, etc.
    """
    logger.info("Running outbox processor job...")

    async with AsyncTransaction() as session:
        try:
            repo = OutboxRepository()

            events_to_process = await repo.get_and_lock_pending_events(
                session, limit=10
            )

            if not events_to_process:
                logger.info("No pending outbox events found.")
                return

            logger.info(f"Found {len(events_to_process)} events to process.")

            # Mark as processing
            for event in events_to_process:
                event.status = EventStatus.PROCESSING
            await session.commit()

            # Process each event
            for event in events_to_process:
                try:
                    await dispatch_event(
                        event.event_type,
                        DomainEvent(
                            id=event.id,
                            event_type=event.event_type,
                            payload=event.payload,
                            meta={
                                "aggregate_type": event.aggregate_type,
                                "aggregate_id": event.aggregate_id,
                                "event_id": str(event.id),
                            },
                        ),
                    )
                    event.status = EventStatus.COMPLETED
                    event.processed_at = datetime.datetime.now(datetime.timezone.utc)
                except Exception as e:
                    logger.error(f"Failed to process event {event.id}: {e}")
                    event.status = EventStatus.FAILED
                    event.retry_count += 1
                session.add(event)

            await session.commit()
            logger.info("Outbox processor job finished.")

        except Exception as e:
            logger.error(f"Error during outbox processing job: {e}")
            await session.rollback()


@asynccontextmanager
async def scheduler_lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        process_outbox_events_job,
        "interval",
        seconds=10,
        id="process_outbox",
        max_instances=1,
    )
    scheduler.start()
    logger.info("Scheduler started.")
    yield
    scheduler.shutdown()
    logger.info("Scheduler shut down.")
