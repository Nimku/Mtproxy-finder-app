# Nimku Proxy

[![Android CI](https://github.com/nimku/mtproxy-finder-app/actions/workflows/android.yml/badge.svg)](https://github.com/nimku/mtproxy-finder-app/actions/workflows/android.yml)
[![Latest release](https://img.shields.io/github/v/release/nimku/mtproxy-finder-app)](https://github.com/nimku/mtproxy-finder-app/releases/latest)
[![Android](https://img.shields.io/badge/Android-7.0%2B-3DDC84?logo=android&logoColor=white)](https://github.com/nimku/mtproxy-finder-app/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Nimku Proxy is an Android app that collects Telegram MTProto proxies from
public sources, independently verifies each one with a real MTProto
handshake, and shows only the ones that actually work — fastest first. It
runs on a paid monthly subscription (Telegram Stars) with the subscription
check and the proxy sources both served entirely from this GitHub repo — no
Google/Firebase services, and the app never talks directly to any private
server, so it keeps working in places where direct connections get blocked.

## Contents of this repo

| Path | What it is |
|---|---|
| `app/` | The Android app (Kotlin, Jetpack Compose, Material 3) |
| `bot/` | The Telegram bot that sells subscriptions and manages `license/status.json` — see [`bot/README.md`](bot/README.md) |
| `license/status.json` | The subscription status file the app reads and the bot writes |
| `.github/workflows/mirror-proxy-feeds.yml` | Scheduled job that mirrors public proxy feeds into `proxy-feeds/` |
| `exteragram/` | Optional companion plugin for the exteraGram Telegram client |

## How the pieces talk to each other

```
                     ┌───────────────────────────┐
  User pays Stars →  │  Telegram bot (your VPS)   │
                     └─────────────┬─────────────┘
                                   │ writes (GitHub API, token on the VPS only)
                                   ▼
                     ┌───────────────────────────┐
                     │ license/status.json (repo) │
                     └─────────────┬─────────────┘
                                   │ reads (raw.githubusercontent.com +
                                   │ jsDelivr/statically CDN mirrors)
                                   ▼
                     ┌───────────────────────────┐
                     │        Android app         │
                     └───────────────────────────┘
```

The app **never** contacts the bot or the VPS directly — by design, so a
block on the VPS/bot (common in some regions) can't take the app down. It
only ever reads a small JSON file from GitHub, through the same set of
mirrors already used for proxy source feeds, and checks whether its locally
entered Telegram ID (hashed) has an active, unexpired entry. Payment itself
happens entirely inside Telegram via its native Stars flow — the bot never
sees or stores card details.

Pricing, subscription length, and even a "free for everyone" toggle are all
controlled from inside Telegram via the bot's `/admin` panel — no code
changes or redeploys needed. See [`bot/README.md`](bot/README.md).

## App features

- Four scan depths: quick, balanced, full and custom
- Full scan of up to 15,000 unique addresses
- Auto / Wi-Fi / LTE network profiles
- Parallel MTProto checks with live, streaming results
- **Priority source**: the first 20 addresses from the `dubblebyte` feed are
  always checked and shown first, in their original order (a failing one is
  skipped, never shown) — everything else fills in below, ranked as usual
- Scan history, reliability ranking, per-source stats
- Background monitoring of favorites with notifications
- Proxy QR code export, and QR import from an image
- Reorder/hide sources on the home screen
- Theming: palettes, custom hex colors, corner radius, text size
- Interface localization (falls back to English for any string a given
  language hasn't translated yet)
- Offline seed list, local cache, favorites, list export
- User-added HTTPS sources with SSRF protection
- Verified self-updates via GitHub Releases (version/signature/SHA-256 checked)
- Subscription gate: pay via the Telegram bot, link your Telegram ID once in
  the app's subscription screen

## Using the app

1. Install the APK from [Releases](https://github.com/nimku/mtproxy-finder-app/releases).
2. Pay for a subscription in the Telegram bot, then enter the same Telegram
   ID in the app's subscription screen.
3. Pick a network profile: Auto, Wi-Fi or LTE.
4. Pick a scan depth and start scanning.
5. Connect to a proxy, or add it to favorites.

Quick mode is fine for daily use. Full mode checks everything the aggregator
collected, so it takes longer.

## Security & privacy

- No advertising SDKs, analytics, or trackers, and no Google/Firebase services
- Connects to Telegram through the installed Telegram client
- Every proxy is independently re-verified with a real MTProto handshake —
  third-party "verified" metadata is only ever used as a hint, never trusted
- User-added sources must be HTTPS and pass URL validation (no localhost/LAN/
  reserved-IP targets, bounded redirects)
- Subscription check reads a public, hash-keyed JSON file — it does not
  contain raw Telegram IDs
- Self-updates are checked against version, package name, signing
  certificate, and SHA-256 before install

Public proxies belong to third-party operators. Don't use them for sensitive
traffic, and don't treat a proxy as a substitute for end-to-end encryption.

## Proxy sources

The aggregator pulls from SoliSpirit, shablin, Dubblebyte, SurfboardV2ray,
Argh94 and other public feeds listed in `sources_manifest.json`. Entries are
deduplicated, then the app verifies reachability itself — third-party
"verified" flags are never trusted on their own.

## exteraGram plugin

An optional companion plugin for the exteraGram Telegram client lives in
[`exteragram/kupu_proxy.plugin`](exteragram/kupu_proxy.plugin) — see
[`exteragram/README.md`](exteragram/README.md) for setup and commands.

## Building

Requires JDK 17 and Android SDK 35.

```bash
./gradlew testDebugUnitTest lintDebug assembleDebug
```

Main source directories:

```text
core/       constants and shared utilities
domain/     models, parser, sources, aggregator
data/       network, Room, DataStore, export
license/    subscription check (LicenseManager)
ui/         Jetpack Compose + Material 3
work/       background checks and update jobs
```

Before your first release build, update the two `TODO`-marked placeholders
in `app/src/main/java/com/nimku/proxy/core/Constants.kt`
(`TELEGRAM_CHANNEL_USERNAME`, `TELEGRAM_BOT_USERNAME`) and make sure
`LICENSE_HASH_SALT` there matches `HASH_SALT` in `bot/.env` exactly.

## Credits

Built on top of [KupuProxy](https://github.com/Kirillka645/KupuProxy)
(MIT-licensed) — see [`LICENSE`](LICENSE) for the original copyright notice,
retained as required by its license.

## License

[MIT](LICENSE)
