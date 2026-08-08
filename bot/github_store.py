"""
The only bridge between a Telegram payment and the app: reads/writes
license/status.json in the GitHub repo via the GitHub Contents API.

The app only ever *reads* this file (through raw.githubusercontent.com and
CDN mirrors — see Constants.kt / HttpSupport.githubCdnUrls in the app). Only
this bot, using GITHUB_TOKEN, ever writes it. The app never talks to this bot
or to this VPS directly.
"""

import base64
import json
import os
from datetime import datetime, timedelta, timezone

import httpx

GITHUB_API = "https://api.github.com"
REPO = os.environ["GITHUB_REPO"]
BRANCH = os.environ.get("GITHUB_BRANCH", "main")
TOKEN = os.environ["GITHUB_TOKEN"]
PATH = "license/status.json"

FREE_FOR_ALL_KEY = "__free_for_all__"

_HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def in_days_iso(days: int) -> str:
    dt = datetime.now(timezone.utc) + timedelta(days=days)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


async def _get_file(client: httpx.AsyncClient) -> tuple[dict, str | None]:
    resp = await client.get(
        f"{GITHUB_API}/repos/{REPO}/contents/{PATH}",
        headers=_HEADERS,
        params={"ref": BRANCH},
    )
    if resp.status_code == 404:
        return {"version": 1, "updated": now_iso(), "subscriptions": {}}, None
    resp.raise_for_status()
    data = resp.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    parsed = json.loads(content) if content.strip() else {}
    parsed.setdefault("version", 1)
    parsed.setdefault("subscriptions", {})
    return parsed, data["sha"]


async def _put_file(client: httpx.AsyncClient, obj: dict, sha: str | None, message: str) -> None:
    body = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    encoded = base64.b64encode(body.encode("utf-8")).decode("ascii")
    payload = {"message": message, "content": encoded, "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    resp = await client.put(
        f"{GITHUB_API}/repos/{REPO}/contents/{PATH}",
        headers=_HEADERS,
        json=payload,
    )
    resp.raise_for_status()


async def _mutate(mutator, message: str, attempts: int = 5) -> dict:
    """Read-modify-write with retry on sha conflicts from concurrent edits."""
    last_error: Exception | None = None
    async with httpx.AsyncClient(timeout=20.0) as client:
        for _ in range(attempts):
            obj, sha = await _get_file(client)
            mutator(obj)
            obj["updated"] = now_iso()
            try:
                await _put_file(client, obj, sha, message)
                return obj
            except httpx.HTTPStatusError as error:
                last_error = error
                if error.response.status_code in (409, 422):
                    continue
                raise
    raise last_error or RuntimeError("Failed to update license/status.json")


async def grant_subscription(hash_key: str, days: int, telegram_id: int) -> str:
    """Extends from the later of (now, current expiry). Returns the new expiry ISO string."""
    new_expiry_holder: dict[str, str] = {}

    def mutate(obj: dict) -> None:
        subs = obj["subscriptions"]
        current = subs.get(hash_key)
        base = datetime.now(timezone.utc)
        if current:
            try:
                current_dt = datetime.fromisoformat(current.replace("Z", "+00:00"))
                if current_dt > base:
                    base = current_dt
            except ValueError:
                pass
        new_expiry = (base + timedelta(days=days)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        subs[hash_key] = new_expiry
        new_expiry_holder["value"] = new_expiry

    await _mutate(mutate, f"chore(license): grant subscription for tg:{telegram_id}")
    return new_expiry_holder["value"]


async def set_free_for_all(enabled: bool) -> None:
    def mutate(obj: dict) -> None:
        subs = obj["subscriptions"]
        if enabled:
            # Far-future expiry; toggling off just removes the key again.
            subs[FREE_FOR_ALL_KEY] = in_days_iso(365 * 50)
        else:
            subs.pop(FREE_FOR_ALL_KEY, None)

    await _mutate(mutate, f"chore(license): free mode {'on' if enabled else 'off'}")


async def read_status() -> dict:
    async with httpx.AsyncClient(timeout=20.0) as client:
        obj, _ = await _get_file(client)
        return obj
