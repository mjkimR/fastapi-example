import logging
from enum import Enum
from typing import Any, Callable, Coroutine, Dict

from app_kit.base.schemas.event import DomainEvent

logger = logging.getLogger(__name__)

# A registry that maps event types to handler functions
EVENT_HANDLER_REGISTRY: Dict[str, Callable[[DomainEvent], Coroutine[Any, Any, None]]] = {}


def register_event_handler(event_type: str | Enum):
    """
    A decorator to register a function as a handler for a specific event type.
    """

    def decorator(func: Callable[[DomainEvent], Coroutine[Any, Any, None]]):
        event_type_str = event_type.value if isinstance(event_type, Enum) else event_type

        if event_type_str in EVENT_HANDLER_REGISTRY:
            # Raise an error if a handler for the same event type is already registered
            raise ValueError(f"Handler for event type '{event_type_str}' is already registered.")
        logger.info(f"Registering handler for event type '{event_type_str}'.")
        EVENT_HANDLER_REGISTRY[event_type_str] = func
        return func

    return decorator


async def dispatch_event(event_type: str | Enum, event: DomainEvent):
    """
    Looks up the appropriate handler in the registry and dispatches the event.
    """
    event_type_str = event_type.value if isinstance(event_type, Enum) else event_type
    handler = EVENT_HANDLER_REGISTRY.get(event_type_str)
    if handler:
        logger.info(f"Dispatching event '{event_type_str}' to handler {handler.__name__}.")
        # The handler is responsible for creating its own dependencies since it runs outside the DI container
        await handler(event)
    else:
        logger.warning(f"No handler registered for event type '{event_type_str}'.")
