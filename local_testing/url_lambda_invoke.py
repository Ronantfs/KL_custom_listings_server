#!/usr/bin/env python3
"""
Quick local test script to invoke the custom listings Lambda via its function URL.
Fill in LAMBDA_URL before use.
"""

import json
import urllib.request

LAMBDA_URL = "https://b62gakukdi4hlmmcmhx533az3y0fgpqs.lambda-url.eu-north-1.on.aws/"


def invoke(handler_name: str, payload: dict) -> dict:
    payload["handler"] = handler_name
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        LAMBDA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    if isinstance(body.get("body"), str):
        return json.loads(body["body"])
    return body


if __name__ == "__main__":
    # --- Example calls ---

    # 0) List curators
    print("=== get_curators ===")
    print(json.dumps(invoke("get_curators", {}), indent=2))

    # 1) Get lists for a curator
    # print("=== get_custom_lists ===")
    # print(json.dumps(invoke("get_custom_lists", {"curator": "kinologue"}), indent=2))

    # 2) Create a list
    # print("=== create_custom_list ===")
    # print(json.dumps(invoke("create_custom_list", {
    #     "curator": "kinologue",
    #     "list_name": "Best of 2025",
    #     "list_caption": "Our picks for the year",
    #     "start_date": "2025-01-01",
    #     "end_date": "2025-12-31",
    # }), indent=2))

    # 3) Assign films
    # print("=== assign_films_to_list ===")
    # print(json.dumps(invoke("assign_films_to_list", {
    #     "curator": "kinologue",
    #     "list_name": "Best of 2025",
    #     "db_ids": [12345, 67890],
    # }), indent=2))

    # 3.2) Remove film
    # print("=== remove_film_from_list ===")
    # print(json.dumps(invoke("remove_film_from_list", {
    #     "curator": "kinologue",
    #     "list_name": "Best of 2025",
    #     "db_id": 12345,
    # }), indent=2))

    # 3.3) Update film caption
    # print("=== update_list_film_caption ===")
    # print(json.dumps(invoke("update_list_film_caption", {
    #     "curator": "kinologue",
    #     "list_name": "Best of 2025",
    #     "db_id": 67890,
    #     "new_caption": "A stunning debut feature",
    # }), indent=2))

    # 4) Update list info
    # print("=== update_list ===")
    # print(json.dumps(invoke("update_list", {
    #     "curator": "kinologue",
    #     "list_name": "Best of 2025",
    #     "updates": {"list_caption": "Updated caption"},
    # }), indent=2))

    # 5) Delete list
    # print("=== delete_list ===")
    # print(json.dumps(invoke("delete_list", {
    #     "curator": "kinologue",
    #     "list_name": "Best of 2025",
    # }), indent=2))
