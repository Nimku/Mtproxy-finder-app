# Deploying the Nimku Proxy bot on your VPS — exact commands

This assumes a fresh Ubuntu/Debian VPS and that you can SSH into it. Every
gray box below is something you copy-paste into your terminal, in order.

---

## 0. Get the bot files onto your VPS

You already have `nimku-proxy-bot.zip` (sent to you in chat). Get it from
your computer onto the VPS. Easiest way — from **your own computer's**
terminal (not the VPS), run:

```bash
scp nimku-proxy-bot.zip youruser@your-vps-ip:~/
```

(Replace `youruser` and `your-vps-ip` with your real VPS login and address.
If you're on Windows without a terminal that has `scp`, use a tool like
WinSCP or FileZilla instead — drag the zip onto the VPS's home folder.)

---

## 1. SSH into your VPS

```bash
ssh youruser@your-vps-ip
```

## 2. Install what the bot needs

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip unzip
```

## 3. Unzip it

```bash
mkdir -p ~/nimku-proxy-bot
unzip -o ~/nimku-proxy-bot.zip -d ~/nimku-proxy-bot
cd ~/nimku-proxy-bot
```

## 4. Create an isolated Python environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 5. Get the two things you need before configuring the bot

**a) Your bot's Telegram token:**
- Open Telegram, message `@BotFather`.
- Send `/newbot`, follow the prompts (it'll ask for a name and a username
  ending in "bot").
- It replies with a token that looks like `123456789:AAExampleTokenHere`.
  Copy it.

**b) A GitHub token for the bot** (lets it record payments — separate from
your Telegram bot token):
- Go to `github.com` → click your profile picture → **Settings**.
- Left sidebar, scroll down → **Developer settings**.
- **Personal access tokens** → **Fine-grained tokens** → **Generate new token**.
- Under "Repository access", choose **Only select repositories** → pick
  `Mtproxy-finder-app`.
- Under "Permissions" → **Repository permissions** → find **Contents** →
  set it to **Read and write**. Leave everything else as "No access".
- Generate it, copy the token (starts with `github_pat_...`). GitHub only
  shows it once.

**c) Your own Telegram numeric ID** (so you can use the bot's admin panel):
- Message `@userinfobot` on Telegram, it replies with your ID (just numbers).

## 6. Configure the bot

```bash
cp .env.example .env
nano .env
```

In the editor, fill in:

```
BOT_TOKEN=<paste the token from BotFather>
GITHUB_REPO=nimku/mtproxy-finder-app
GITHUB_BRANCH=main
GITHUB_TOKEN=<paste the github_pat_... token>
HASH_SALT=mtpf-v1-change-this-salt
ADMIN_IDS=<your numeric Telegram ID from step 5c>
```

Save and exit nano: `Ctrl+O`, `Enter`, then `Ctrl+X`.

## 7. Test it

```bash
python bot.py
```

You should see it log that it started. Now, in Telegram, open your bot and
send `/start` — it should reply. Also try `/admin` — since your ID is in
`ADMIN_IDS`, you should see the admin panel with buttons for price,
subscription length, free mode, stats, and broadcast.

If that works: press `Ctrl+C` to stop it, then move to step 8 to make it
run permanently. If it errors, read the error message — it's almost always
a typo in `.env` (missing token, extra space, etc.).

## 8. Make it run permanently (survives reboots, restarts if it crashes)

```bash
deactivate
sudo cp mtproxyfinder-bot.service /etc/systemd/system/nimku-proxy-bot.service
```

Now edit the copied service file so its paths match where you actually put
things:

```bash
sudo sed -i "s#/opt/mtproxy-finder-app/bot#$HOME/nimku-proxy-bot#g; s/User=mtproxyfinder/User=$USER/" /etc/systemd/system/nimku-proxy-bot.service
```

Then start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nimku-proxy-bot
```

Check it's actually running:

```bash
sudo systemctl status nimku-proxy-bot
```

You should see `active (running)` in green. To watch its live logs any
time:

```bash
journalctl -u nimku-proxy-bot -f
```

(`Ctrl+C` to stop watching logs — this does not stop the bot itself.)

---

## That's it — day-to-day use

- The bot now runs forever in the background, restarts itself if it
  crashes, and restarts on VPS reboot.
- To change price, subscription length, or turn on free mode: message your
  own bot with `/admin` on Telegram. No VPS/terminal access needed for any
  of that.
- To update the bot's code later: `git pull`-style replace of these files,
  then `sudo systemctl restart nimku-proxy-bot`.
- To stop it: `sudo systemctl stop nimku-proxy-bot`.
