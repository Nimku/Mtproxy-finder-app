# Nimku Proxy

[![Android CI](https://github.com/nimku/mtproxy-finder-app/actions/workflows/android.yml/badge.svg)](https://github.com/nimku/mtproxy-finder-app/actions/workflows/android.yml)
[![Latest release](https://img.shields.io/github/v/release/nimku/mtproxy-finder-app)](https://github.com/nimku/mtproxy-finder-app/releases/latest)
[![Android](https://img.shields.io/badge/Android-7.0%2B-3DDC84?logo=android&logoColor=white)](https://github.com/nimku/mtproxy-finder-app/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**English** · [Русский](README.ru.md) · [فارسی](README.fa.md)

🌐 **Website: [nimku.github.io/Mtproxy-finder-app](https://nimku.github.io/Mtproxy-finder-app/)**

---

## What is this app for?

In some countries Telegram is blocked, throttled, or simply won't connect.
The usual way around that is a **proxy** — another computer, somewhere else in
the world, that passes your Telegram traffic along for you.

Telegram has its own kind of proxy, called **MTProto**. People share these
proxies publicly, in lists and channels, for free.

The problem: **those lists go stale fast.** A proxy that worked this morning
is dead by evening — it gets overloaded, blocked, or switched off. Most
addresses in any public list are already dead when you find them. Trying them
one by one, by hand, is slow and frustrating.

**Nimku Proxy does that work for you.** It gathers proxy addresses from many
public lists, tests every single one, and shows you only the ones that are
working *right now* — fastest first. Then you tap one, and you're connected.

The app is **completely free**. No payment, no subscription, no account, no
sign-up, no ads.

## What this app is *not*

Worth being clear about, so you know what you're installing:

- **It is not a VPN.** It does not send your phone's traffic anywhere. It
  finds proxy addresses and hands the one you pick to your Telegram app.
  Telegram alone uses it — your browser and other apps are unaffected.
- **It does not connect to Telegram for you.** It doesn't touch your Telegram
  account, messages, or phone number. It never asks you to log in.
- **It doesn't collect anything about you.** No account, no analytics, no
  tracking, no ads. See [Privacy](#privacy).

## How it works

```
  1. Collect          2. Test              3. Show              4. You tap
  ──────────          ────────             ───────              ──────────
  Proxy addresses     Each address is      Only the working     Telegram opens
  from many public →  contacted for real → ones are listed,  →  and asks you
  lists                                    fastest at top       to switch on
```

Step 2 is the part that matters. Public lists often mark proxies as
"verified", but that flag was true whenever the list was made — maybe days
ago. Nimku Proxy ignores those claims and performs a real MTProto handshake
with each address itself, right now, from your phone and your network. A
proxy that doesn't answer never appears in your results.

That last detail matters more than it sounds: a proxy is only "working" from
*your* network. One that's fine in one country may be blocked in another. The
test runs on your device, so the results are true for you specifically.

<a name="installing-the-apk"></a>

## Installing the app

Android does not allow installing apps from outside Google Play until you
permit it, and some manufacturers add extra steps. This is normal for any app
distributed outside the Play Store — it's not specific to this one.

### Standard Android (8.0 and newer)

1. Download `NimkuProxy.apk` from the
   [latest release](https://github.com/nimku/mtproxy-finder-app/releases/latest).
2. Open the downloaded file. Android will say your browser (or Telegram, or
   your file manager) isn't allowed to install apps.
3. Tap **Settings** → turn on **Allow from this source** → go back → **Install**.

The permission applies only to that one app, so allowing your browser doesn't
allow anything else.

### Xiaomi / Redmi / POCO (MIUI, HyperOS)

These phones need the most extra steps, and it's usually where people give up:

- Settings → **Privacy protection** → **Special permissions** → **Install
  unknown apps** → choose your browser → turn on.
- MIUI runs its own scan and shows a full-screen warning. Choose
  **Install anyway**.
- If it still refuses: Settings → Privacy protection → turn off
  **Enhanced security** / **Increased security**. MIUI silently blocks
  sideloading while that is on. You can turn it back on after installing.
- Some MIUI versions require you to be signed in to a Mi account with an
  internet connection to finish a sideload. That's MIUI's requirement, not
  the app's.

### Huawei / Honor (EMUI, HarmonyOS)

- Settings → **Security** → **More settings** → **Install apps from external
  sources** → allow your browser or file manager.
- If Pure Mode is on, it will refuse anything not from AppGallery:
  Settings → Security → **More settings** → **Pure Mode** → turn off.

### Samsung (One UI)

- Settings → **Apps** → tap your browser → **Install unknown apps** → allow.
- One UI 6.0 and newer has **Auto Blocker**, which blocks sideloading
  entirely: Settings → **Security and privacy** → **Auto Blocker** → turn off.

### If your phone won't allow it at all

Some carrier-locked and company-managed phones genuinely cannot sideload. In
that case install from a computer with a USB cable:

```bash
adb install NimkuProxy.apk
```

## How to use it

### First run

1. Open the app. There is nothing to set up, no login, no key to enter.
2. Choose a **network profile** — Auto, Wi-Fi, or LTE. Leave it on **Auto**
   unless you have a reason not to; it adjusts the test settings for the
   connection you're on.
3. Choose a **scan depth**:
   - **Quick** — a fast look, good enough for everyday use. Start here.
   - **Balanced** — more addresses, still reasonably fast.
   - **Full** — checks everything collected, up to 15,000 addresses. Slow, but
     thorough. Use it when quick scans find nothing.
   - **Custom** — your own settings.
4. Press start. Results appear **while the scan is still running** — you don't
   have to wait for it to finish. The fastest proxies rise to the top.

### Connecting to a proxy

1. Tap a proxy in the list.
2. Your Telegram app opens and asks whether to enable that proxy.
3. Confirm. Telegram is now going through it.

If it stops working later — proxies die all the time — just open Nimku Proxy
and scan again, then pick a different one.

### Useful things to know

- **Favorites** — star proxies that work well for you. The app can check them
  quietly in the background and notify you when one stops working.
- **Scan history and statistics** — see which sources actually produce working
  proxies on your network, and which are a waste of time.
- **QR codes** — show a proxy as a QR code to pass it to someone next to you,
  or import one from a photo.
- **Export a list** — save your working proxies to a file to keep or share.
- **Add your own source** — if you know a list the app doesn't use, add its
  HTTPS address in settings.
- **Appearance** — themes, colors, corner rounding, text size, and interface
  language.

## If GitHub doesn't open in your country

The app normally fetches its proxy lists from GitHub, with several mirror
services as backups. In some regions GitHub itself is unreachable — and this
often varies between cities and even between mobile operators in the same
country. If scanning finds nothing at all, this is the likely reason: the app
can't reach the lists in the first place.

**There is a second way in, that needs no GitHub access at all:**

1. Open our bot in Telegram and ask it for the current proxy list. It sends
   you a plain file.
2. Tap that file inside Telegram.
3. Choose **Open with → Nimku Proxy** (some phones say "Open in" or show a
   share menu).
4. The app reads the list and checks it exactly like a normal scan.

You can also forward a message containing proxy links and share it to Nimku
Proxy, or save any list as a `.txt` file and open it from the app with
**Check file**.

Telegram usually still works when GitHub doesn't — which is precisely why the
list travels through Telegram in this case.

<a name="verifying-and-building-it-yourself"></a>

## Is it safe to install?

You should not install an unknown APK just because someone told you to, and
you don't have to trust us either. There are several ways to check, from
easiest to strongest.

### Scan it yourself

Upload the APK to a service like VirusTotal, or check it with any antivirus
you already trust. Each release also ships a `.sha256` file — you can paste
that value into VirusTotal's search box to look the file up directly.

Note that security scanners sometimes flag proxy and network apps by
heuristics — a small number of engines flagging a file, while all the others
find nothing, is usually a false positive rather than a real finding.

### Check that your download wasn't tampered with

Every release includes a `.sha256` file next to the APK. Compare it:

```bash
sha256sum NimkuProxy-v2.0.0.apk
```

If the value matches, your copy is byte-for-byte the published one.

### Check who signed it

This is the strongest check, and the useful one for updates. Every release is
signed with the same key, so a modified or repackaged copy cannot match this:

```bash
apksigner verify --print-certs NimkuProxy-v2.0.0.apk
```

Expected:

```
Signer #1 certificate SHA-256 digest: d205a5af6051d2d29b418c6094aa8da760e5fbb05f128bf031d9890f138fad96
```

Subject: `CN=Nimku Proxy, O=Nimku, C=US`. The app's own updater runs this
same check before installing any update, so an update can never quietly
switch to a different key.

### Build it yourself and compare

The strongest possible answer to "what's actually inside this file" is to
build it from the source in this repository and compare:

```bash
git clone https://github.com/nimku/mtproxy-finder-app
cd mtproxy-finder-app
git checkout v2.0.0
./gradlew --no-daemon assembleRelease
```

Without signing credentials this produces an *unsigned* APK at
`app/build/outputs/apk/release/app-release-unsigned.apk`. Compare its compiled
code with the published one, ignoring the signature files that by definition
can't match:

```bash
mkdir -p built published
unzip -q -o app/build/outputs/apk/release/app-release-unsigned.apk -d built
unzip -q -o NimkuProxy-v2.0.0.apk -d published
sha256sum built/classes*.dex published/classes*.dex
diff -r -x 'META-INF*' built published
```

The `classes*.dex` digests are the meaningful comparison — that is the actual
program code.

To match the published build you need the same tools CI used: **JDK 17**
(Temurin), **Android SDK 35**, **Gradle 8.9** (the wrapper in this repo),
**AGP 8.7.3**, **Kotlin 2.0.21**. A different JDK or plugin version produces a
different, but equally valid, build.

Being straight about the limits: the Android build tools do not guarantee
byte-identical output on different machines, so small differences in file
ordering or timestamps are expected and are not evidence of tampering. The
signing-certificate check above is the one that cryptographically proves where
a build came from.

## Privacy

- No ads, no analytics, no trackers, and no Google or Firebase services
- No account, no login, no payment — nothing about you is collected or sent
- The app talks to public proxy lists and to your installed Telegram app.
  Nothing else.
- Your scan results and favorites stay on your phone
- Sources you add yourself must use HTTPS and are validated before use, so a
  malicious address can't make the app probe your home network
- Updates are verified by version, package name, signing certificate and
  SHA-256 before installing

One honest warning: **public proxies are run by strangers.** Whoever operates
one can see that you are connecting and how much traffic you send. Your
Telegram chats stay encrypted between you and Telegram, and secret chats stay
end-to-end encrypted, but a proxy is not a privacy tool and is not a
substitute for encryption. Use it to reach Telegram when it is blocked — not
to hide who you are.

## For people who already paid

Versions before 2.0 required a paid subscription. That is gone completely —
2.0 and later never check a licence and never ask for anything. If you are
still on an older version, it has been switched to free for everyone, so it
keeps working even if you never update.

## Where the proxies come from

The app pulls from public proxy lists maintained by several open-source
projects, all listed in [`sources_manifest.json`](sources_manifest.json).
Duplicates are removed, and then every address is verified by the app itself —
a list's own "verified" flag is never trusted on its own.

## exteraGram plugin

There is an optional companion plugin for the exteraGram Telegram client in
[`exteragram/kupu_proxy.plugin`](exteragram/kupu_proxy.plugin) — see
[`exteragram/README.md`](exteragram/README.md) for setup and commands.

---

## For developers

### Building

Requires JDK 17 and Android SDK 35.

```bash
./gradlew testDebugUnitTest lintDebug assembleDebug
```

Source layout:

```text
core/       constants and shared utilities
domain/     models, parser, sources, aggregator
data/       network, Room, DataStore, export
ui/         Jetpack Compose + Material 3
updater/    self-update download and verification
work/       background checks and update jobs
```

### Repository contents

| Path | What it is |
|---|---|
| `app/` | The Android app (Kotlin, Jetpack Compose, Material 3) |
| `sources_manifest.json` | The list of public proxy feeds the app pulls from |
| `.github/workflows/mirror-proxy-feeds.yml` | Scheduled job mirroring those feeds into `proxy-feeds/` |
| `update_manifest.json` | Fallback update info for regions where the GitHub API is blocked |
| `license/status.json` | Legacy — kept only so pre-2.0 installs keep working |
| `exteragram/` | Optional companion plugin for the exteraGram Telegram client |

### Release signing

`assembleRelease` is signed only if `RELEASE_KEYSTORE_PATH`,
`RELEASE_KEYSTORE_PASSWORD`, `RELEASE_KEY_ALIAS` and `RELEASE_KEY_PASSWORD`
are set as environment variables (see `app/build.gradle.kts`) — without them it
still builds, just unsigned. In CI, `.github/workflows/release.yml` reads the
equivalent GitHub Actions secrets (`RELEASE_KEYSTORE_BASE64` instead of
`_PATH`). The keystore itself is never committed to this repo.

### VirusTotal submission

The release workflow can upload each APK to VirusTotal automatically and put
the report link in the release notes. It needs a `VIRUSTOTAL_API_KEY`
repository secret (a free VirusTotal key is enough). Without the secret the
release still publishes and still prints the report URL — it just doesn't
upload, so the report only exists once someone scans that file themselves.

## License

[MIT](LICENSE)
