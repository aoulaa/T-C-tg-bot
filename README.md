# Telegram Community Bot

This is a Telegram bot with community management features.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the bot token:**

    Create a `.env` file in the root directory and add your bot token:
    ```
    BOT_TOKEN="YOUR_BOT_TOKEN"
    ```

## Usage

To run the bot, execute the following command:

```bash
python main.py
```

### Commands

-   `/start` — Bot introduction and basic help.

#### Scope-specific commands

- **Everyone (any chat):**
  - `/start` — Starts interaction with the bot.

- **Group admins (in group/supergroup only):**
  - `/voiceonly_on` — Enable voice-only mode for the group. Non-voice messages from non-admins will be deleted.
  - `/voiceonly_off` — Disable voice-only mode and allow all message types.

- **Bot owner (private chat only):**
  - `/export_users` — Export a CSV of users who accepted T&C across groups.
  - `/show_groups` — List all groups seen by the bot with their current settings.

Notes:

- Admin status is determined via Telegram chat membership; only admins/creators can toggle voice-only mode (`handlers/admin.py`).
- Owner is defined by `BOT_OWNER_ID` in `.env` and owner-only commands must be used in a private chat.
- When a new user joins a group, the bot restricts them until they accept the Terms & Conditions via the inline "Accept" button (`handlers/user_join.py`).

## Deployment (Docker + Nginx)

This bot runs as an HTTP server and uses a Telegram webhook. In production, you should:

- Expose the bot internally on `WEBHOOK_HOST:WEBHOOK_PORT` (default `0.0.0.0:8080`).
- Put Nginx in front to terminate TLS and reverse-proxy to the bot.
- Ensure `WEBHOOK_BASE_URL` is the public HTTPS URL that Telegram can reach (e.g., `https://bot.example.com`).

### Required environment variables

Add these to your `.env` file (see `config.py` for how they are used):

- `BOT_TOKEN` — Telegram bot token.
- `BOT_OWNER_ID` — your Telegram user ID (for owner-only commands).
- `T_AND_C_VERSION` — version string for your Terms and Conditions.
- `T_AND_C_CONTENT` — the T&C content or URL.
- `DATABASE_NAME` — SQLite filename or DB name used by the app.
- `WEBHOOK_BASE_URL` — public base URL, e.g. `https://bot.example.com`.
- `WEBHOOK_HOST` — interface the app binds to (default `0.0.0.0`).
- `WEBHOOK_PORT` — container port the app listens on (default `8080`).

The effective webhook path is `/webhook/{BOT_TOKEN}` and the full URL is `${WEBHOOK_BASE_URL}/webhook/{BOT_TOKEN}`.

### Deploy with Docker Compose

The provided `docker-compose.yml` defines a single `bot` service.

Common commands (run from the project root):

- `docker compose build` — builds the image from `Dockerfile`.
- `docker compose up -d` — starts the container in the background.
- `docker compose logs -f` — streams logs; useful for watching startup and webhook set logs.
- `docker compose ps` — shows running containers for this stack.
- `docker compose restart` — restarts the service to pick up config changes.
- `docker compose down` — stops and removes containers/networks (persistent volume remains).

Port mapping in `docker-compose.yml` defaults to `8080:8080`. You can change `WEBHOOK_PORT` in `.env` if needed.

Health check endpoint: the app exposes `GET /healthz` which returns `ok` when the process is healthy.

### Nginx reverse proxy (TLS termination)

Example Nginx server block to proxy HTTPS -> bot container:

```nginx
server {
    listen 80;
    server_name bot.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bot.example.com;

    # SSL certs (replace with your certbot paths)
    ssl_certificate     /etc/letsencrypt/live/bot.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.example.com/privkey.pem;

    # Proxy to the bot service (machine IP/port reachable from Nginx)
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 75s;
    }
}
```

Notes:

- If Nginx runs on the same host as Docker, `proxy_pass http://127.0.0.1:8080` matches the host port published by Compose.
- If Nginx is in a separate container or host, point `proxy_pass` to the reachable address of the bot service/host.

### Quick TLS with Certbot (Ubuntu example)

Replace `bot.example.com` with your domain.

```bash
sudo apt update && sudo apt install -y nginx
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
# Obtain and install a cert for Nginx
sudo certbot --nginx -d bot.example.com
# Auto-renewal test
sudo certbot renew --dry-run
```

### End-to-end bring-up sequence

1) Create and verify `.env` with all required variables.
2) Start the bot:

```bash
docker compose up -d
docker compose logs -f
```

3) Configure Nginx with your domain and TLS, proxying to the bot on `8080` (or your chosen `WEBHOOK_PORT`).

4) Point `WEBHOOK_BASE_URL` in `.env` to your HTTPS domain (e.g., `https://bot.example.com`). Then restart the bot to re-set the webhook:

```bash
docker compose restart
```

On startup, the app will attempt to set the webhook to `${WEBHOOK_BASE_URL}/webhook/{BOT_TOKEN}` and log success/failure.

### Validate and troubleshoot

- Verify the app is reachable locally from the server:

```bash
curl -sS http://127.0.0.1:8080/healthz
```

- Verify HTTPS via Nginx from outside (or using the server itself):

```bash
curl -sS https://bot.example.com/healthz
```

- Common fixes:
  - Ensure DNS points to your server and port 443 is open.
  - Check that `WEBHOOK_BASE_URL` is correct and uses `https://`.
  - Review logs for webhook errors:

```bash
docker compose logs -f
```

### What the commands do

- `docker compose build` — builds the image from your `Dockerfile`.
- `docker compose up -d` — launches the bot container detached.
- `docker compose logs -f` — tails the logs interactively.
- `docker compose restart` — restarts the running container(s).
- `docker compose ps` — shows the status of services.
- `docker compose down` — stops and removes containers and the default network (keeps named volumes).
- `curl http://127.0.0.1:8080/healthz` — checks the bot’s local health endpoint.
- `systemctl reload nginx` — reloads Nginx after config changes (if using system Nginx).
