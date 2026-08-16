"""Collect proxies from every source, then build the file the app reads.

Two halves:

  scrape()  — pull raw proxy links out of Telegram channels and HTTPS feeds
  build()   — deduplicate, optionally verify, and write proxies.txt

The file is deliberately plain text full of tg://proxy links. The app's parser
pulls links out of arbitrary text and ignores everything else, so the header
comments are free — they cost nothing and make the file readable to a human who
opens it in a text editor before trusting it.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone

import aiohttp

import mtproto
import sources as src

log = logging.getLogger("scraper")

PROXY_RE = re.compile(
    r'(?:https?://t\.me/proxy|tg://proxy)\?server=([^&\s"<>\n]+)'
    r'&port=(\d+)&secret=([a-zA-Z0-9+/=_-]{10,})',
    re.IGNORECASE,
)

# Some feeds publish "host:port:secret" lines rather than links.
TRIPLE_RE = re.compile(
    r'(?:^|[\s,;"\'])((?:\d{1,3}\.){3}\d{1,3}|[a-z0-9][a-z0-9.-]{2,80}\.[a-z]{2,10})'
    r'[:\s]+(\d{2,5})[:\s]+([a-fA-F0-9]{32,}|[a-zA-Z0-9+/=_-]{22,})',
    re.IGNORECASE | re.MULTILINE,
)

MAX_FEED_BYTES = 8 * 1024 * 1024
BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class Proxy:
    host: str
    port: int
    secret: str
    source: str

    @property
    def key(self) -> str:
        return f"{self.host.lower()}:{self.port}:{self.secret.lower()}"

    @property
    def link(self) -> str:
        return f"https://t.me/proxy?server={self.host}&port={self.port}&secret={self.secret}"


@dataclass
class RunStats:
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    per_source: dict[str, int] = field(default_factory=dict)
    failed_sources: dict[str, str] = field(default_factory=dict)
    scraped: int = 0
    unique: int = 0
    verified: int = 0
    published: int = 0
    verify_seconds: float = 0.0

    @property
    def working_sources(self) -> int:
        return sum(1 for n in self.per_source.values() if n)


def _extract(text: str, source: str, limit: int | None = None) -> list[Proxy]:
    found: list[Proxy] = []
    seen: set[str] = set()

    def add(host: str, port_s: str, secret: str) -> bool:
        try:
            port = int(port_s)
        except ValueError:
            return False
        if not 1 <= port <= 65535:
            return False
        # Reject anything whose secret we can't make sense of, before it ever
        # reaches the verifier — these lists carry a lot of malformed entries
        # (truncated hex, fragments of TLS dumps pasted in as secrets).
        if mtproto.decode_secret(secret) is None:
            return False
        p = Proxy(host.strip(), port, secret.strip(), source)
        if p.key in seen:
            return False
        seen.add(p.key)
        found.append(p)
        return True

    for host, port_s, secret in PROXY_RE.findall(text):
        add(host, port_s, secret)
        if limit and len(found) >= limit:
            return found
    if not found:
        for host, port_s, secret in TRIPLE_RE.findall(text):
            add(host, port_s, secret)
            if limit and len(found) >= limit:
                break
    return found


# ─────────────────────────────────────────────────────────────
#  HTTPS feeds
# ─────────────────────────────────────────────────────────────

async def _fetch_one(session: aiohttp.ClientSession, name: str, url: str) -> tuple[str, list[Proxy], str | None]:
    last_error = "no mirror responded"
    for candidate in src.mirror_urls(url):
        try:
            async with session.get(
                candidate,
                timeout=aiohttp.ClientTimeout(total=20),
                headers={"User-Agent": BROWSER_UA},
            ) as resp:
                if resp.status != 200:
                    last_error = f"HTTP {resp.status}"
                    continue
                body = await resp.content.read(MAX_FEED_BYTES)
        except Exception as exc:  # noqa: BLE001 — any failure just means try the next mirror
            last_error = f"{exc.__class__.__name__}: {exc}"
            continue

        text = body.decode("utf-8", "ignore")
        # A couple of feeds are JSON; the links are in there as strings, so
        # flattening the whole document to text finds them without needing to
        # know each feed's schema.
        if text.lstrip()[:1] in "[{":
            try:
                text = json.dumps(json.loads(text))
            except json.JSONDecodeError:
                pass
        proxies = _extract(text, name)
        if proxies:
            return name, proxies, None
        last_error = "no proxies found in response"
    return name, [], last_error


async def scrape_feeds(stats: RunStats) -> list[Proxy]:
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            *[_fetch_one(session, name, url) for name, url in src.FEEDS]
        )
    out: list[Proxy] = []
    for name, proxies, error in results:
        stats.per_source[name] = len(proxies)
        if error:
            stats.failed_sources[name] = error
            log.warning("feed %s: %s", name, error)
        else:
            log.info("feed %s: %d proxies", name, len(proxies))
        out.extend(proxies)
    return out


# ─────────────────────────────────────────────────────────────
#  Telegram channels
# ─────────────────────────────────────────────────────────────

async def scrape_channels(client, cfg, stats: RunStats) -> list[Proxy]:
    """Reads the most recent messages of each channel and keeps the newest
    `proxies_per_channel` proxies from it.

    Newest-first matters more than volume here: a proxy posted an hour ago is
    far likelier to still be alive than one from last week, and the whole point
    of running hourly is freshness.
    """
    out: list[Proxy] = []
    for channel in src.CHANNELS:
        name = f"@{channel}"
        try:
            texts: list[str] = []
            async for message in client.iter_messages(channel, limit=cfg.channel_message_limit):
                if message.text:
                    texts.append(message.text)
                # Channels very often put the proxy behind a "Connect" button
                # instead of in the message body.
                markup = getattr(message, "reply_markup", None)
                if markup is not None:
                    for row in getattr(markup, "rows", []) or []:
                        for button in getattr(row, "buttons", []) or []:
                            url = getattr(button, "url", None)
                            if url:
                                texts.append(url)
            proxies = _extract("\n".join(texts), name, limit=cfg.proxies_per_channel)
            stats.per_source[name] = len(proxies)
            log.info("channel %s: %d proxies", name, len(proxies))
            out.extend(proxies)
        except Exception as exc:  # noqa: BLE001 — one dead channel must not stop the run
            stats.per_source[name] = 0
            stats.failed_sources[name] = f"{exc.__class__.__name__}: {exc}"
            log.warning("channel %s failed: %s", name, exc)
        await asyncio.sleep(0.3)  # stay well inside Telegram's rate limits
    return out


# ─────────────────────────────────────────────────────────────
#  Verification
# ─────────────────────────────────────────────────────────────

async def verify_all(proxies: list[Proxy], cfg) -> list[tuple[Proxy, int]]:
    """Full MTProto handshake against every proxy, in parallel.

    Checks from *this server*, which is not where the user is — a proxy that
    answers here can still be blocked from inside Russia or Iran. So this is a
    filter for definitely-dead entries, not a promise. The app re-checks every
    proxy on the user's own network, which is the verdict that counts.
    """
    started = time.monotonic()
    loop = asyncio.get_running_loop()
    semaphore = asyncio.Semaphore(cfg.verify_workers)

    with ThreadPoolExecutor(max_workers=cfg.verify_workers) as pool:

        async def check(p: Proxy) -> tuple[Proxy, int] | None:
            async with semaphore:
                result = await loop.run_in_executor(
                    pool,
                    lambda: mtproto.check_link(
                        p.host, p.port, p.secret,
                        connect_timeout=cfg.connect_timeout,
                        response_timeout=cfg.response_timeout,
                    ),
                )
            return (p, result.rtt_ms) if result.ok else None

        results = await asyncio.gather(*[check(p) for p in proxies])

    alive = [r for r in results if r is not None]
    alive.sort(key=lambda pair: pair[1])
    log.info("verified %d/%d alive in %.1fs", len(alive), len(proxies), time.monotonic() - started)
    return alive


# ─────────────────────────────────────────────────────────────
#  Output file
# ─────────────────────────────────────────────────────────────

def write_file(entries: list[tuple[Proxy, int]], stats: RunStats, cfg) -> str:
    os.makedirs(cfg.output_dir, exist_ok=True)
    path = os.path.join(cfg.output_dir, "proxies.txt")
    generated = stats.started_at.strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Nimku Proxy — MTProto proxy list",
        f"# Generated: {generated}",
        f"# Proxies: {len(entries)}",
        (f"# Every proxy here passed a real MTProto handshake from our server."
         if cfg.verify else
         "# Unverified: collected but not tested — the app will test them."),
        "#",
        "# Open this file with the Nimku Proxy app; it re-checks every proxy",
        "# from your own network and shows the ones that work for you.",
        "# https://github.com/Nimku/Mtproxy-finder-app",
        "",
    ]
    lines.extend(p.link for p, _ in entries)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return path


async def run_once(client, cfg) -> tuple[str, RunStats]:
    """One full cycle: scrape everything, verify, write the file."""
    stats = RunStats()

    collected: list[Proxy] = []
    feed_task = asyncio.create_task(scrape_feeds(stats))
    if client is not None:
        collected.extend(await scrape_channels(client, cfg, stats))
    collected.extend(await feed_task)
    stats.scraped = len(collected)

    unique: dict[str, Proxy] = {}
    for proxy in collected:
        unique.setdefault(proxy.key, proxy)
    pool = list(unique.values())
    stats.unique = len(pool)
    log.info("scraped %d, %d unique", stats.scraped, stats.unique)

    if cfg.verify:
        verify_started = time.monotonic()
        entries = await verify_all(pool, cfg)
        stats.verify_seconds = time.monotonic() - verify_started
        stats.verified = len(entries)
    else:
        entries = [(p, 0) for p in pool]

    entries = entries[: cfg.max_published]
    stats.published = len(entries)
    path = write_file(entries, stats, cfg)
    return path, stats


def summary(stats: RunStats, cfg) -> str:
    """Human-readable run report — sent to the admin, and useful for working out
    which sources are worth keeping."""
    ranked = sorted(stats.per_source.items(), key=lambda kv: -kv[1])
    top = "\n".join(f"  {n:>4}  {name}" for name, n in ranked[:12] if n)
    dead = [name for name, n in stats.per_source.items() if not n]
    lines = [
        f"Scraped {stats.scraped} proxies from {stats.working_sources}/{src.TOTAL_SOURCES} sources",
        f"Unique: {stats.unique}",
    ]
    if cfg.verify:
        lines.append(
            f"Passed MTProto handshake: {stats.verified} "
            f"({stats.verified * 100 // max(stats.unique, 1)}%) in {stats.verify_seconds:.0f}s"
        )
    lines.append(f"Published: {stats.published}")
    if top:
        lines.append("\nTop sources:\n" + top)
    if dead:
        lines.append(f"\nProduced nothing ({len(dead)}): " + ", ".join(dead[:20]))
    return "\n".join(lines)
