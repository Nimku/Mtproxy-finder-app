"""Every proxy source we know about, in one place.

This is the union of what the Android app pulls from and what the older
@SetProxy poster script pulled from — neither used the full set. Adding a source
here is the only change needed to start scraping it.
"""

from __future__ import annotations

# ── Telegram channels, read through Telethon ────────────────────────────────
# Only a handful of these are in both original lists; most came from one side
# or the other. Whether each actually yields *working* proxies is measured at
# runtime and reported in the run summary — prune this list from that data
# rather than from guesswork.

CHANNELS: list[str] = [
    # from the @SetProxy poster
    "ProxyMTProto", "mtp4tg", "TProxyRU", "proxies_tg", "ProxyFreeMTProto",
    "TelMTProto", "MTProxyExpress", "MTProxySpot", "MTProtoStream",
    "SecureMTProto", "MTProtoGateway", "FastMTProxyHub", "MTProxyOnly",
    "DailyProxyList", "FreeSecureProxy", "JustMTProxy",
    # from the Android app
    "mtprotoproxy", "ProxyOFF", "proxies_for_telegram", "MTProto_proxy",
    "FreeMTProto", "proxytelegram", "proxy_mtproto_list", "TelegramProxies",
    "mtproto_proxy_list", "ProxiesMTProto",
    # our own channel — people post proxies in the comments there too
    "SetProxy",
]

# ── Plain-text / JSON feeds fetched over HTTPS ──────────────────────────────
# (display name, URL). Raw GitHub first; jsDelivr is added automatically as a
# fallback for each github.com URL in scraper.py, since raw.githubusercontent
# is blocked in some of the same places our users are.

FEEDS: list[tuple[str, str]] = [
    ("dubblebyte",
     "https://raw.githubusercontent.com/dubblebyte/free-mtproto-proxies/main/all_proxies.txt"),
    ("SoliSpirit",
     "https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt"),
    ("Argh94",
     "https://raw.githubusercontent.com/Argh94/telegram-proxy-scraper/main/proxy.txt"),
    ("Surfboardv2ray",
     "https://raw.githubusercontent.com/Surfboardv2ray/TGProto/main/proxies.txt"),
    ("Surfboardv2ray-tested",
     "https://raw.githubusercontent.com/Surfboardv2ray/TGProto/main/proxies-tested.txt"),
    ("shablin",
     "https://raw.githubusercontent.com/shablin/mtproto-proxy/main/data/valid_proxy.txt"),
    ("ALIILAPRO",
     "https://raw.githubusercontent.com/ALIILAPRO/MTProtoProxy/main/mtproto.txt"),
    ("Grim1313",
     "https://raw.githubusercontent.com/Grim1313/mtproto-for-telegram/master/all_proxies.txt"),
    ("kort0881",
     "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all_mtproto.txt"),
    ("kort0881-verified",
     "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/verified/proxy_all_verified.json"),
    ("mheidari98",
     "https://raw.githubusercontent.com/mheidari98/MTProtoProxyList/main/mtproto-proxy.txt"),
    ("mtpro.xyz",
     "https://mtpro.xyz/wp-json/wp/v2/pages?slug=mtproto"),
]


def mirror_urls(url: str) -> list[str]:
    """Every way we know to fetch one feed, best-first.

    raw.githubusercontent.com is blocked in some regions and rate-limits when a
    lot of feeds are pulled at once, so each GitHub URL also gets its jsDelivr
    and githack equivalents. The bot itself normally runs somewhere unblocked,
    but the mirrors also cover raw.githubusercontent simply being down.
    """
    urls = [url]
    prefix = "https://raw.githubusercontent.com/"
    if url.startswith(prefix):
        rest = url[len(prefix):]
        parts = rest.split("/", 3)
        if len(parts) == 4:
            owner, repo, ref, path = parts
            urls.append(f"https://cdn.jsdelivr.net/gh/{owner}/{repo}@{ref}/{path}")
            urls.append(f"https://fastly.jsdelivr.net/gh/{owner}/{repo}@{ref}/{path}")
            urls.append(f"https://raw.githack.com/{owner}/{repo}/{ref}/{path}")
    return urls


TOTAL_SOURCES = len(CHANNELS) + len(FEEDS)
