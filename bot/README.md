# Nimku Proxy list bot

Scrapes Telegram proxies from 39 sources on a schedule, verifies each one with a
real MTProto handshake, and hands the result out as a file.

**Why it exists:** in parts of Russia and Iran GitHub is unreachable, so the app
can't download proxy lists on its own. Telegram usually still works — so the
list travels through Telegram instead. The user taps the file, opens it with
Nimku Proxy, and the app tests everything on their own network as usual.

The app is not changed by any of this and does not talk to this bot.

## What it does

Every hour (configurable):

1. **Scrapes** 27 Telegram channels (newest 30 proxies each) and 12 HTTPS feeds.
2. **Deduplicates** by host:port:secret.
3. **Verifies** every proxy with a real MTProto handshake — obfuscated2,
   `req_pq_multi`, `resPQ` nonce check, plus full FakeTLS for `ee` secrets.
4. **Writes** `data/proxies.txt`, fastest first.

Users then press one button and get that file.

### About verification

`mtproto.py` is a port of the app's `MtprotoChecker.kt`, so the bot and the app
agree on what "working" means.

This matters more than it sounds. The usual "is it alive" test opens a socket,
sends bytes, and passes if anything comes back — which any web server, SSH
daemon or captive portal will do. Lists built that way are mostly addresses that
answer but are not Telegram proxies. This one only passes a server that
completes a real Telegram handshake with the published secret.

One honest limit: it checks from **your server**, not from where the user is. A
proxy that answers in Germany can still be blocked inside Russia. So this
removes the definitely-dead entries; the app's own check on the user's network
is the verdict that counts. That's why the app still tests everything it's given.

Set `VERIFY=false` to publish everything scraped without testing. The file gets
several times larger and mostly dead — not recommended.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:

| Variable | Required | What it's for |
|---|---|---|
| `BOT_TOKEN` | yes | From @BotFather |
| `ADMIN_ID` | no | Your user ID — gets a report after each rebuild |
| `TG_API_ID`, `TG_API_HASH`, `TG_PHONE` | no | Reading the 27 channels. Without these only the 12 HTTPS feeds are scraped |
| `TG_SESSION` | no | Session filename — **must not collide with another Telethon process** |
| `REFRESH_MINUTES` | no | Default 60 |
| `VERIFY` | no | Default true |
| `PUBLISH_CHANNEL` | no | Also post each list to a channel, e.g. `@SetProxy` |

Get `TG_API_ID` / `TG_API_HASH` from https://my.telegram.org → API development
tools.

### First run

```bash
.venv/bin/python bot.py
```

Telethon asks for a login code on first start (once — after that the session
file is reused). The first list takes a few minutes to build; until then the bot
tells users to come back shortly.

### Check the proxy checker works on this machine

```bash
.venv/bin/python -m mtproto
```

This connects to real Telegram data centres and runs the full handshake against
them. If those pass, the implementation is working and any "dead" verdict is the
proxy's fault rather than a bug. Worth running once before trusting the output.

## Running it properly

`nohup` loses the process on reboot and won't restart it after a crash. Use
systemd:

```ini
# /etc/systemd/system/nimku-proxy-bot.service
[Unit]
Description=Nimku Proxy list bot
After=network-online.target

[Service]
WorkingDirectory=/root/nimku-proxy-bot
ExecStart=/root/nimku-proxy-bot/.venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now nimku-proxy-bot
journalctl -u nimku-proxy-bot -f
```

Or `docker compose up -d` — a `Dockerfile` and `docker-compose.yml` are included.

## Secrets

`.env`, `data/` and `*.session` are gitignored. Never put a token in a `.py`
file: anything pasted into a chat, a screenshot, or a support thread is
compromised and has to be revoked through @BotFather.

The `.session` file is more sensitive than the bot token — it is a logged-in
Telegram session for the account that created it. Anyone who copies it has that
account.

## Sources

27 Telegram channels and 12 HTTPS feeds, listed in `sources.py`. That's the
union of what the app pulls from and what the older @SetProxy poster used —
neither had the whole set.

Not all of them are worth keeping. Some channels are abandoned; some feeds
republish each other. The run report after each rebuild ranks every source by
how many proxies it produced, so prune the list from that rather than from
guesswork. Adding a source is one line in `sources.py`.

## File format

Plain text, one `https://t.me/proxy?...` link per line, with a comment header.
The app's parser pulls links out of arbitrary text and ignores everything else,
so the header is free — and it means a cautious user can open the file in a text
editor and see exactly what they're being given.
