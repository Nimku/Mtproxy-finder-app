# Nimku Proxy — Project Handoff

**Read this if you're the owner and feel lost, or if you're an AI assistant
being asked to help with this project. This document explains everything:
what exists, what doesn't, and exactly what to do next.**

---

## 1. What this project is, in plain English

An Android app called **Nimku Proxy** that finds working "proxy" servers for
Telegram (specifically MTProxy servers — these let people reach Telegram
in countries where it's blocked or slowed down, like Russia and Iran). The
app collects proxy addresses from public lists on the internet, tests each
one itself, and shows the working ones, fastest first.

**The business model:** it's not free. A user has to pay through a Telegram
bot — 20 Telegram Stars per month by default, but that number is not fixed
in code, it's changeable any time — to unlock the app. If they don't pay
(or their month runs out), the app blocks scanning until they pay again.

**Why it's built the way it is:** because the target users are in places
like Russia and Iran, the app is deliberately built so it **never directly
contacts your bot or your server**. If it did, and your server got blocked
by a government firewall, the whole app would stop working for everyone.
Instead, the app only ever reads a small file from GitHub (which is much
harder to block outright), and your bot is the only thing that writes to
that file. See section 4 for how that actually works.

---

## 2. The three separate things, and where each one physically lives

This project is not one thing — it's three, and they live in three
different places on purpose (this was a deliberate security/reliability
decision, not an accident):

| # | What | Where it lives | Who can see it |
|---|---|---|---|
| 1 | **The Android app's source code** | GitHub repo (see §3) | Public — anyone can see the code (not a secret; the app has no embedded passwords) |
| 2 | **The Telegram bot** (sells subscriptions, talks to your bot account) | Given to you directly as a file (`nimku-proxy-bot.zip`) — **you run this on your own VPS**. It is intentionally **not** in the GitHub repo. | Private — only you, on your VPS |
| 3 | **The release signing key** (a cryptographic file that "signs" the app so Android trusts updates) | Given to you directly as a file (`nimku-proxy-release-signing.zip`) | **Only you should ever have this. If you lose it, you can never publish an app update again. If it leaks, someone could impersonate your app.** |

If you don't have items 2 and 3 anymore (e.g. you're in a new chat with a
different AI), say so — they need to be regenerated/reconfigured, they
can't be recovered from the GitHub repo because they were never put there.

---

## 3. The GitHub repo — exact facts

- **Repo:** `https://github.com/Nimku/Mtproxy-finder-app`
- **⚠️ Important:** all the work so far is on a branch called
  `claude/cloud-code-github-capabilities-tac6lr` — **not** on `main`.
  In fact `main` doesn't exist yet on this repo. If you look at the repo on
  GitHub and see nothing, you're probably looking at the (empty) default
  branch — switch the branch dropdown to see the real code.
  **This should get merged into a proper `main` branch at some point** —
  ask whoever/whatever is helping you to do that (create a `main` branch
  from this one, or open and merge a pull request).
- **App package name:** `com.nimku.proxy` (Android's internal ID for the app)
- **App display name:** "Nimku Proxy" (what shows under the icon)

---

## 4. How the subscription system actually works (plain walkthrough)

1. A user opens your Telegram bot and pays Stars (or gets free access, if
   you've turned on "free mode" — see §6).
2. Your bot computes a scrambled (hashed) version of that user's Telegram
   ID and writes `{scrambled_id: expiry_date}` into a file called
   `license/status.json`, which lives in the GitHub repo. Your bot does this
   using a private GitHub access token that only your bot has.
3. In the app, the user types in their own Telegram numeric ID once (found
   via `@userinfobot` on Telegram). The app scrambles it the same way and
   checks: "does this scrambled ID appear in that file, with a date that
   hasn't passed yet?" If yes, the app unlocks. If not, it shows a paywall
   screen.
4. The app checks that file over the internet using several different
   addresses (GitHub's own address, plus a couple of backup mirror
   services), specifically so that if one of them gets blocked in a given
   country, the others still work.

Nobody can cheat this by editing the file themselves — only your bot (using
its private token) can write to it. Reading it is public and doesn't
require any password, but reading alone doesn't let you fake a subscription.

**Changing the price, subscription length, or making it free** — all done
by messaging your own bot with `/admin` (you'll be the only one who can use
that command). No code, no GitHub, no redeploying anything. See the bot's
own `README.md` inside `nimku-proxy-bot.zip`.

---

## 5. What is DONE (you don't need to do these)

- [x] The Android app itself — all screens, proxy scanning/checking logic,
      settings, themes, etc.
- [x] The subscription paywall screen in the app
- [x] The Telegram bot code (payments, `/admin` panel, multi-language)
- [x] A GitHub Action that automatically builds an installable `.apk` file
      and publishes it as a "Release" whenever you push a version tag
      (e.g. `v1.0.0`)
- [x] Proper release-signing wired into the build (needs your 4 secret
      values added — see §6, step 4)

## 6. What is NOT done — your to-do list, in order

1. **Register your Telegram bot.** Message `@BotFather` on Telegram, send
   `/newbot`, follow the prompts, and it'll give you a token (a long
   string of letters/numbers). Save it somewhere safe.
2. **Decide/confirm your Telegram channel and bot @usernames.** Right now
   the app is configured with placeholder names: channel `@NimkuProxy`,
   bot `@NimkuProxyBot`. If you register different actual usernames on
   Telegram, someone needs to update two lines in the code
   (`app/src/main/java/com/nimku/proxy/core/Constants.kt`) to match — just
   tell an AI "update the channel/bot usernames to X and Y" and it's a
   two-minute change.
3. **Get a GitHub personal access token for the bot.** This is different
   from your bot's Telegram token — it's what lets your bot write to the
   `license/status.json` file in the repo. Steps are in the bot's own
   `README.md` (inside the zip you were given): GitHub → Settings →
   Developer settings → Fine-grained tokens → create one scoped to just
   this repo, "Contents: Read and write" only.
4. **Add your release signing secrets to GitHub** so the auto-build
   produces a properly signed app. Instructions are in
   `nimku-proxy-release-signing.zip` → `README.txt`. This is a one-time,
   copy-paste-4-values-into-a-GitHub-settings-page task.
5. **Run the bot on your VPS.** Unzip `nimku-proxy-bot.zip` there, fill in
   its `.env` file with your bot token + GitHub token + your own Telegram
   numeric ID (so you become the bot's admin), then follow its `README.md`
   to start it (it can run permanently in the background via `systemd`,
   instructions included).
6. **Create your first release** so there's an actual `.apk` file people
   can download: on GitHub, go to your repo → **Releases** → **Draft a new
   release** → type `v1.0.0` as a brand-new tag → **Publish**. Within a few
   minutes, GitHub automatically builds the app and attaches the
   installable file to that release page.
7. **(Optional but recommended)** Get this branch merged into a real `main`
   branch, so the repo looks normal to anyone who opens it.
8. Share the download link (your GitHub release page) and your bot's
   Telegram link with people, e.g. via your Telegram channel.

---

## 7. Glossary (plain-language definitions of terms you'll see)

- **Repo (repository):** the folder of all the project's code, hosted on
  GitHub's website.
- **Branch:** a named "version" of the code. Changes get made on a branch
  before (optionally) being merged into the main one.
- **Commit:** one saved snapshot of changes, with a description.
- **Push:** uploading your local changes to GitHub.
- **APK:** the installable file format for Android apps (like a `.exe` on
  Windows).
- **Release / tag:** a labeled, downloadable version of the app (e.g.
  "v1.0.0") on GitHub, with the `.apk` file attached.
- **GitHub Actions / workflow:** an automated robot that runs on GitHub's
  servers — in this project, it's what builds the `.apk` file for you
  automatically.
- **Secret:** a password/token stored privately in GitHub's settings,
  usable by the automated robot above but never visible in the code.
- **Keystore / signing key:** a cryptographic file that "signs" the app so
  Android knows updates really come from you and not an impostor.
- **VPS:** a rented server you control (where your bot runs, always on).
- **Telegram Stars:** Telegram's own in-app payment currency, used here to
  charge for subscriptions — no separate payment processor needed.

---

## 8. Key values reference (for you or an AI to copy exactly)

| Thing | Value |
|---|---|
| GitHub repo | `Nimku/Mtproxy-finder-app` |
| Current branch (not yet merged to main) | `claude/cloud-code-github-capabilities-tac6lr` |
| App package name | `com.nimku.proxy` |
| App display name | Nimku Proxy |
| Telegram channel placeholder | `@NimkuProxy` (update if your real one differs) |
| Telegram bot placeholder | `@NimkuProxyBot` (update if your real one differs) |
| Default price | 20 Stars / 30 days (change anytime via bot `/admin`, no code change) |
| Subscription file path (in repo) | `license/status.json` |
| Constants file (usernames/salt) | `app/src/main/java/com/nimku/proxy/core/Constants.kt` |
| Release workflow file | `.github/workflows/release.yml` |
| GitHub secrets needed for signed releases | `RELEASE_KEYSTORE_BASE64`, `RELEASE_KEYSTORE_PASSWORD`, `RELEASE_KEY_ALIAS`, `RELEASE_KEY_PASSWORD` |

---

## 9. Note for an AI assistant picking this up

If you're an AI reading this because the owner shared it with you: they
are **not** a developer and don't know git/GitHub terminology — explain
actions in plain language before doing them, and confirm before anything
destructive (force-push, deleting branches, rewriting history). The repo
has a CI workflow that runs tests/lint on every push
(`.github/workflows/android.yml`) and a separate release workflow
(`.github/workflows/release.yml`) triggered by version tags. The Telegram
bot and the release signing keystore are **intentionally not in this repo**
— don't assume they exist there; ask the owner for them or help them
regenerate/redeploy as needed. Never put secrets, tokens, or the signing
keystore into this repository.
