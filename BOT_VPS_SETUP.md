# Deploying the Nimku Proxy bot on your VPS — exact commands

This runs the bot in Docker, so it works the same regardless of what Python
version (or OS) your VPS happens to have — and moving to a different VPS
later is just "copy this folder, run one command" on the new machine.

Every gray box below is something you copy-paste into your terminal, in
order.

---

## 0. Get the bot files onto your VPS

You already have `nimku-proxy-bot.zip` (sent to you in chat). Get it from
your computer onto the VPS.

**From a regular computer**, from its own terminal (not the VPS):
```bash
scp nimku-proxy-bot.zip youruser@your-vps-ip:~/
```
(Replace `youruser` and `your-vps-ip`. On Windows without `scp`, use WinSCP
or FileZilla instead — drag the zip onto the VPS's home folder.)

**From an Android phone using Termux**, first run `termux-setup-storage`
once (grant the permission prompt), then:
```bash
scp ~/storage/downloads/nimku-proxy-bot.zip youruser@your-vps-ip:~/
```

---

## 1. SSH into your VPS

```bash
ssh youruser@your-vps-ip
```

## 2. Install Docker (one-time)

```bash
curl -fsSL https://get.docker.com | sh
```

This is Docker's own official install script — works on effectively any
Debian/Ubuntu-based VPS regardless of exact version.

## 3. Unzip the bot files

```bash
sudo apt update && sudo apt install -y unzip
mkdir -p ~/nimku-proxy-bot
unzip -o ~/nimku-proxy-bot.zip -d ~/nimku-proxy-bot
cd ~/nimku-proxy-bot
```

## 4. Get the three things you need before configuring the bot

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

## 5. Configure the bot

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
ADMIN_IDS=<your numeric Telegram ID from step 4c>
```

Save and exit nano: `Ctrl+O`, `Enter`, then `Ctrl+X`.

## 6. Build and start it

```bash
docker compose up -d --build
```

First run takes a minute or two (downloads the Python base image and
installs dependencies inside the container — this time it's isolated from
your VPS's own Python, so it always works the same way). `-d` means it runs
in the background from now on.

## 7. Check it's working

```bash
docker compose logs -f
```

You should see it log that it started polling Telegram. Now, in Telegram,
open your bot and send `/start` — it should reply. Also try `/admin` —
since your ID is in `ADMIN_IDS`, you should see the admin panel with
buttons for price, subscription length, free mode, stats, and broadcast.

Press `Ctrl+C` to stop *watching* logs (this does not stop the bot itself —
Docker already restarts it automatically if it ever crashes or the VPS
reboots).

---

## That's it — day-to-day use

- **Change price / subscription length / turn on free mode:** message your
  own bot with `/admin` on Telegram. No VPS access needed for any of that.
- **Watch logs:** `docker compose logs -f` (from inside `~/nimku-proxy-bot`)
- **Restart it:** `docker compose restart`
- **Stop it:** `docker compose down`
- **Update the code later:** replace the `.py` files with new versions,
  then `docker compose up -d --build` again.
- **Move to a different VPS:** copy the entire `~/nimku-proxy-bot` folder
  (it includes your `.env` and its `data/` folder) to the new VPS, install
  Docker there (step 2), then just `docker compose up -d --build` again.
  Nothing else to reconfigure.
