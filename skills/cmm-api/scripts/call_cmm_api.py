#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.request


DEFAULT_BASE_URL = "https://ai-api.chanmama.com"
EXECUTE_PATH = "/v1/cmm/api/execute"
POLLING_API_MAP = {
    "video_understanding": "video_understanding_task_info",
}
ACTIVE_TASK_STATUSES = {"pending", "running", "retrying"}


def task_from_response(response):
    if not isinstance(response, dict):
        return {}
    payload = response.get("data")
    if not isinstance(payload, dict):
        return {}
    if payload.get("task_id"):
        return payload
    nested = payload.get("data")
    return nested if isinstance(nested, dict) and nested.get("task_id") else {}


def call_cmm_api(base_url, auth, api, query):
    body = {"api": api, "query": query}
    url = base_url.rstrip("/") + EXECUTE_PATH
    req = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=240) as resp:
        return json.loads(resp.read().decode("utf-8"))


def execute_api(base_url, auth, api, query, poll_interval=2.0, task_timeout=1800):
    task_info_api = POLLING_API_MAP.get(api)
    if not task_info_api:
        return call_cmm_api(base_url, auth, api, query)

    response = call_cmm_api(base_url, auth, api, query)
    if not isinstance(response, dict) or response.get("code") != 0:
        return response
    task = task_from_response(response)
    task_id = task.get("task_id")
    if not task_id:
        return response

    deadline = time.monotonic() + task_timeout
    while time.monotonic() < deadline:
        response = call_cmm_api(
            base_url,
            auth,
            task_info_api,
            {"task_id": task_id},
        )
        if not isinstance(response, dict) or response.get("code") != 0:
            return response
        task = task_from_response(response)
        status = task.get("status")
        if status not in ACTIVE_TASK_STATUSES:
            return response
        time.sleep(poll_interval)
    raise TimeoutError(f"{api} task timed out: {task_id}")


def main():
    parser = argparse.ArgumentParser(description="Call the CMM API execute endpoint.")
    parser.add_argument("--base-url", default=os.getenv("CMM_API_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--auth", default=os.getenv("CMM_API_KEY"))
    parser.add_argument("--api", required=True)
    parser.add_argument("--query", required=True, help="JSON object")
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--task-timeout", type=int, default=1800)
    args = parser.parse_args()

    if not args.auth:
        raise SystemExit("CMM_API_KEY or --auth is required")

    parsed = execute_api(
        args.base_url,
        args.auth,
        args.api,
        json.loads(args.query),
        poll_interval=args.poll_interval,
        task_timeout=args.task_timeout,
    )
    json.dump(parsed, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
