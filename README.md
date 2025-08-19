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

-   `/start`: The bot will reply with "Hello, World!".
