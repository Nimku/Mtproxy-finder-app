# Nimku Proxy — subscription bot

Handles Telegram Stars payments for the app's subscription. This is the only
piece of infrastructure you run yourself (on your VPS). Everything is
controlled from inside Telegram — no website, no code changes needed to
change price, subscription length, or to make the app free.

## How it fits together

```
 User pays Stars  →  This bot (your VPS)  →  GitHub API  →  license/status.json
                                                                     │
                                            Android app  ───────────┘
                                     (reads via raw.githubusercontent.com
                                      + jsDelivr/statically CDN mirrors)
```

The app **never** talks to this bot or to your VPS. It only ever reads a
JSON file from GitHub (through several mirrors, so it keeps working even
where `raw.githubusercontent.com` itself is blocked). Only this bot writes
that file, using a GitHub token that lives only in this bot's `.env` — it is
never bundled into the app.

Individual users are stored in `license/status.json` as a SHA-256 hash of
`HASH_SALT + their Telegram numeric ID` — not the raw ID — so the file is
not a plain list of who your users are. Payment happens entirely through
Telegram's own Stars flow (`send_invoice` with currency `XTR`); this bot
never sees or stores card/payment details, Telegram handles that.

## One-time setup

1. **Create the bot**: message [@BotFather](https://t.me/BotFather), `/newbot`,
   copy the token.
2. **Create a GitHub token scoped to just this repo**: GitHub →
   Settings → Developer settings → Fine-grained tokens → generate one with
   **Contents: Read and write** on `nimku/mtproxy-finder-app` only. Nothing
   else.
3. **Find your own Telegram numeric ID** (to make yourself admin): message
   [@userinfobot](https://t.me/userinfobot).
4. Copy `.env.example` to `.env` and fill in `BOT_TOKEN`, `GITHUB_TOKEN`,
   `ADMIN_IDS` (your ID from step 3). Leave `HASH_SALT` as-is unless you also
   update the matching constant in the app
   (`app/src/main/java/com/nimku/mtproxyfinder/core/Constants.kt`,
   `LICENSE_HASH_SALT`) — **the two must always match exactly**, or every
   check will silently report "not subscribed."
5. Install and run:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python bot.py
   ```
6. For a always-on VPS deployment, copy `mtproxyfinder-bot.service` to
   `/etc/systemd/system/`, adjust the paths inside it, then:
   ```bash
   sudo systemctl enable --now mtproxyfinder-bot
   ```

That's it — no server, no ports to open, no domain/TLS certificate needed.
The bot only makes outbound connections (to Telegram and to GitHub), so it
works from behind NAT/CGNAT and doesn't need a public IP.

## Using it day to day

- `/admin` (admin only) opens an inline panel to:
  - change the **price** in Stars,
  - change the **subscription length** in days,
  - turn **free mode** on/off — when on, every user (existing and new) gets
    instant free access, no payment step; turn it back off and payment is
    required again. Nothing to redeploy, no code to touch.
  - see basic **stats** (how many users, which languages they use),
  - **broadcast** a message to every user who has ever messaged the bot.
- Regular users: `/start`, `/subscribe`, `/status`, `/language`.

All of the above take effect immediately for every subsequent interaction —
settings live in `bot/data/config.json` on the VPS (auto-created, edited
only through `/admin`, never by hand).

## Adding a language

Bot text lives entirely in `i18n.py`. Add a new language code to `LANGUAGES`
and a matching dict of translated strings to `TEXT` — that's the only file
that needs touching; no logic changes anywhere else. The app's own UI
language is independent and already supports many languages (see
`app/src/main/res/values-*/strings.xml`); users can pick either
independently of the other.

## Files

| File | Purpose |
|---|---|
| `bot.py` | Handlers: `/start`, `/subscribe`, `/status`, `/language`, `/admin`, payments |
| `i18n.py` | All bot text, per language |
| `storage.py` | Local admin settings + known-users list (VPS-only, never committed) |
| `github_store.py` | Reads/writes `license/status.json` via the GitHub API |
| `.env.example` | Template for secrets/config — copy to `.env`, never commit `.env` |
| `mtproxyfinder-bot.service` | systemd unit for always-on deployment |
