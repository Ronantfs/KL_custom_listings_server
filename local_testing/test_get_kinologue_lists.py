#!/usr/bin/env python3
"""Fetch and print the kinologue filmLists from the Lambda."""

import json
import urllib.request

LAMBDA_URL = "https://b62gakukdi4hlmmcmhx533az3y0fgpqs.lambda-url.eu-north-1.on.aws/"

payload = json.dumps({
    "handler": "get_custom_lists",
    "curator": "kinologue",
}).encode("utf-8")

req = urllib.request.Request(
    LAMBDA_URL,
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(req) as resp:
    raw = json.loads(resp.read().decode("utf-8"))

body = json.loads(raw["body"]) if isinstance(raw.get("body"), str) else raw

print(json.dumps(body, indent=2))
