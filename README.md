# Nimku Proxy

[![Android CI](https://github.com/nimku/mtproxy-finder-app/actions/workflows/android.yml/badge.svg)](https://github.com/nimku/mtproxy-finder-app/actions/workflows/android.yml)
[![Latest release](https://img.shields.io/github/v/release/nimku/mtproxy-finder-app)](https://github.com/nimku/mtproxy-finder-app/releases/latest)
[![Android](https://img.shields.io/badge/Android-7.0%2B-3DDC84?logo=android&logoColor=white)](https://github.com/nimku/mtproxy-finder-app/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Nimku Proxy is an Android app that collects Telegram MTProto proxies from
public sources, independently verifies each one with a real MTProto
handshake, and shows only the ones that actually work — fastest first.

**It is free.** No subscription, no payment, no account, no sign-in. There
are no ads, no analytics, and no Google or Firebase services in the build —
the app talks to public proxy feeds and to your installed Telegram client,
and to nothing else.

## Contents of this repo

| Path | What it is |
|---|---|
| `app/` | The Android app (Kotlin, Jetpack Compose, Material 3) |
| `sources_manifest.json` | The list of public proxy feeds the app pulls from |
| `.github/workflows/mirror-proxy-feeds.yml` | Scheduled job that mirrors those feeds into `proxy-feeds/` |
| `update_manifest.json` | Fallback update info for regions where the GitHub API is blocked |
| `license/status.json` | Legacy — kept only so pre-2.0 installs keep working (see below) |
| `exteragram/` | Optional companion plugin for the exteraGram Telegram client |

### A note for people who paid for the old version

Versions before 2.0 required a Telegram Stars subscription. That is gone —
2.0 and later never check a licence at all. `license/status.json` is left in
place with the "free for everyone" flag on, so anyone still running an older
build is unlocked too and nothing breaks if they never update.

## How the app gets its proxies

```
   ┌──────────────────────────┐        ┌──────────────────────────┐
   │  Public proxy feeds       │        │  Channel bot (Telegram)   │
   │  (GitHub + CDN mirrors)   │        │  scrapes + posts a file   │
   └────────────┬─────────────┘        └────────────┬─────────────┘
                │ normal path                        │ fallback where
                │                                    │ GitHub is blocked
                ▼                                    ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  Android app — re-checks every proxy with a real handshake    │
   └──────────────────────────────────────────────────────────────┘
```

The normal path reads feeds straight from GitHub, with jsDelivr/githack CDN
mirrors as backups. Where GitHub itself is unreachable — which varies by
region and even by ISP — the companion bot posts a scraped proxy list as a
plain file in Telegram. Tap the file, choose **Nimku Proxy**, and the app
checks it exactly like a normal scan. No GitHub access needed for that path.

## App features

- Four scan depths: quick, balanced, full and custom
- Full scan of up to 15,000 unique addresses
- Auto / Wi-Fi / LTE network profiles
- Parallel MTProto checks with live, streaming results
- **Priority source**: the first 20 addresses from the `dubblebyte` feed are
  always checked and shown first, in their original order (a failing one is
  skipped, never shown) — everything else fills in below, ranked as usual
- **Import a proxy list from a file** — pick one in the app, or open/share a
  file into Nimku Proxy straight from Telegram or a file manager
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

## Using the app

1. Install the APK from [Releases](https://github.com/nimku/mtproxy-finder-app/releases)
   — see [Installing the APK](#installing-the-apk) below.
2. Pick a network profile: Auto, Wi-Fi or LTE.
3. Pick a scan depth and start scanning.
4. Connect to a proxy, or add it to favorites.

Quick mode is fine for daily use. Full mode checks everything the aggregator
collected, so it takes longer.

If scanning finds nothing because the feeds themselves are unreachable from
your network, get a proxy list file from the channel bot and open it with
Nimku Proxy — the app will check that list instead.

## Installing the APK

Android blocks app installs from outside Google Play until you allow them,
and several manufacturers add extra steps on top of the standard one. This is
normal for any app distributed outside the Play Store.

**Standard Android (8.0+)**

1. Download `NimkuProxy.apk` from the
   [latest release](https://github.com/nimku/mtproxy-finder-app/releases/latest).
2. Open it. Android will say the browser (or Telegram, or your file manager)
   isn't allowed to install apps.
3. Tap **Settings** → enable **Allow from this source** → go back → **Install**.

The permission is granted per app, so allowing your browser doesn't allow
anything else.

**Xiaomi / Redmi / POCO (MIUI, HyperOS)** — the extra steps that trip most
people up:

- Settings → **Privacy protection** → **Special permissions** → **Install
  unknown apps** → pick your browser → enable.
- MIUI also runs its own scan and shows a scary full-screen warning; choose
  **Install anyway**.
- If installs still fail, turn off Settings → Privacy protection →
  **Enhanced/Increased security** (MIUI silently blocks sideloads while it's
  on). You can turn it back on afterwards.
- Some MIUI builds require a signed-in Mi account and an internet connection
  just to complete a sideload — that's MIUI's check, not the app's.

**Huawei / Honor (EMUI, HarmonyOS)**

- Settings → **Security** → **More settings** → **Install apps from external
  sources** → allow your browser or file manager.
- Optional Pure Mode: Settings → Security → **More settings** → **Pure Mode**
  → turn it off, or it will refuse anything not from AppGallery.

**Samsung (One UI)**

- Settings → **Apps** → tap your browser → **Install unknown apps** → allow.
- Samsung's Auto Blocker (One UI 6.0+) blocks sideloading outright: Settings
  → **Security and privacy** → **Auto Blocker** → turn off.

**If your phone is fully locked down** (some carrier and enterprise-managed
devices genuinely cannot sideload), install from a computer instead:

```bash
adb install NimkuProxy.apk
```

## Verifying and building it yourself

You should not install an unknown APK on trust, and you don't have to. There
are three independent checks, from quickest to strongest.

### 1. VirusTotal

Every release is submitted to VirusTotal by the release workflow itself, so
the report exists before anyone downloads the file. The link is in each
release's notes, and always points at that exact build's digest:

```
https://www.virustotal.com/gui/file/<SHA-256 of the APK>
```

### 2. Checksum

Every release ships a `.sha256` file next to the APK. Confirm the file you
downloaded is byte-for-byte the one that was published:

```bash
sha256sum NimkuProxy-v2.0.0.apk
```

### 3. Signing certificate

This is the strongest check, and the one worth doing on updates: every
release is signed with the same key, so a tampered or repackaged build cannot
match this fingerprint.

```bash
apksigner verify --print-certs NimkuProxy-v2.0.0.apk
```

Expected:

```
Signer #1 certificate SHA-256 digest: d205a5af6051d2d29b418c6094aa8da760e5fbb05f128bf031d9890f138fad96
```

Subject: `CN=Nimku Proxy, O=Nimku, C=US`. The app's built-in updater performs
this same signing-certificate check automatically before installing an
update, so an update can never silently switch keys.

### 4. Build it yourself and compare

Nothing in a release comes from anywhere but this repo at that tag. To
confirm it:

```bash
git clone https://github.com/nimku/mtproxy-finder-app
cd mtproxy-finder-app
git checkout v2.0.0
./gradlew --no-daemon assembleRelease
```

With no signing environment variables set, this produces an *unsigned* APK at
`app/build/outputs/apk/release/app-release-unsigned.apk`. Compare its
compiled code against the published build, ignoring the signature files that
by definition can't match:

```bash
mkdir -p built published
unzip -q -o app/build/outputs/apk/release/app-release-unsigned.apk -d built
unzip -q -o NimkuProxy-v2.0.0.apk -d published
sha256sum built/classes*.dex published/classes*.dex
diff -r -x 'META-INF*' built published
```

The `classes*.dex` digests are the meaningful comparison — that's the actual
compiled application code.

To match the published build you need the same toolchain the CI used:
**JDK 17** (Temurin), **Android SDK 35**, **Gradle 8.9** (via the wrapper in
this repo), **AGP 8.7.3**, **Kotlin 2.0.21**. A different JDK or AGP version
can produce a different but equally valid build.

Being straight about the limits: the Android toolchain does not guarantee
byte-identical output across machines, so treat a small diff in resource
ordering or timestamps as expected rather than as evidence of tampering. The
signing-certificate check in step 3 is the one that cryptographically proves
where a build came from.

## Security & privacy

- No advertising SDKs, analytics, or trackers, and no Google/Firebase services
- No account, no login, no payment — the app collects nothing about you
- Connects to Telegram through the installed Telegram client
- Every proxy is independently re-verified with a real MTProto handshake —
  third-party "verified" metadata is only ever used as a hint, never trusted
- User-added sources must be HTTPS and pass URL validation (no localhost/LAN/
  reserved-IP targets, bounded redirects)
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
ui/         Jetpack Compose + Material 3
updater/    self-update download and verification
work/       background checks and update jobs
```

### Release signing

`assembleRelease` is only signed if `RELEASE_KEYSTORE_PATH`,
`RELEASE_KEYSTORE_PASSWORD`, `RELEASE_KEY_ALIAS`, and `RELEASE_KEY_PASSWORD`
are set as environment variables (see `app/build.gradle.kts`) — without them
it still builds, just unsigned. In CI, `.github/workflows/release.yml` reads
the equivalent GitHub Actions secrets (`RELEASE_KEYSTORE_BASE64` instead of
`_PATH`) and falls back to a debug-signed build until those secrets exist.
The keystore itself is never committed to this repo.

### VirusTotal submission

The release workflow uploads each APK to VirusTotal and puts the report link
in the release notes. It needs a `VIRUSTOTAL_API_KEY` repository secret (a
free VirusTotal account key is enough). Without the secret the release still
publishes and still links the report URL — it just doesn't upload, so the
report only exists once someone else scans that digest.

## License

[MIT](LICENSE)
