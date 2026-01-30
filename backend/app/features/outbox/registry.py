import logging
from typing import Callable, Coroutine, Any, Dict

logger = logging.getLogger(__name__)

# A registry that maps event types to handler functions
EVENT_HANDLER_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = {}


def register_event_handler(event_type: str):
    """
    A decorator to register a function as a handler for a specific event type.
    """

    def decorator(func: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]):
        if event_type in EVENT_HANDLER_REGISTRY:
            # Raise an error if a handler for the same event type is already registered
            raise ValueError(f"Handler for event type '{event_type}' is already registered.")
        logger.info(f"Registering handler for event type '{event_type}'.")
        EVENT_HANDLER_REGISTRY[event_type] = func
        return func

    return decorator


async def dispatch_event(event_type: str, payload: dict):
    """
    Looks up the appropriate handler in the registry and dispatches the event.
    """
    handler = EVENT_HANDLER_REGISTRY.get(event_type)
    if handler:
        logger.info(f"Dispatching event '{event_type}' to handler {handler.__name__}.")
        # The handler is responsible for creating its own dependencies since it runs outside the DI container
        await handler(payload)
    else:
        logger.warning(f"No handler registered for event type '{event_type}'.")
