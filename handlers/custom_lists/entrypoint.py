import argparse
import json
import logging
from typing import Dict, Any

from handlers.custom_lists.get_curators_handler import get_curators_handler
from handlers.custom_lists.get_custom_lists_handler import get_custom_lists_handler
from handlers.custom_lists.create_custom_list_handler import create_custom_list_handler
from handlers.custom_lists.assign_films_to_list_handler import assign_films_to_list_handler
from handlers.custom_lists.remove_film_from_list_handler import remove_film_from_list_handler
from handlers.custom_lists.update_list_film_caption_handler import update_list_film_caption_handler
from handlers.custom_lists.update_list_handler import update_list_handler
from handlers.custom_lists.delete_list_handler import delete_list_handler
from handlers.custom_lists.create_curator_handler import create_curator_handler

HANDLER_REGISTRY = {
    "get_curators": get_curators_handler,
    "create_curator": create_curator_handler,
    "get_custom_lists": get_custom_lists_handler,
    "create_custom_list": create_custom_list_handler,
    "assign_films_to_list": assign_films_to_list_handler,
    "remove_film_from_list": remove_film_from_list_handler,
    "update_list_film_caption": update_list_film_caption_handler,
    "update_list": update_list_handler,
    "delete_list": delete_list_handler,
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def _normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    if "body" in event and isinstance(event["body"], str):
        return json.loads(event["body"])
    return event


def handler(event: Dict[str, Any], context=None) -> Dict[str, Any]:
    logger.info("Entrypoint start event_keys=%s", sorted(event.keys()))

    payload = _normalize_event(event)

    handler_name = payload.get("handler")
    if not handler_name:
        raise ValueError("Missing required 'handler' field in event")

    handler_fn = HANDLER_REGISTRY.get(handler_name)
    if not handler_fn:
        raise ValueError(f"Unknown handler '{handler_name}'")

    logger.info("Dispatching to handler=%s", handler_name)
    result = handler_fn(payload, context)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(result),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--handler", required=True)
    parser.add_argument("--payload", required=True)

    args = parser.parse_args()

    event = json.loads(args.payload)
    event["handler"] = args.handler

    handler(event, context=None)
