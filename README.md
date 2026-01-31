# Torrent Bots

A project providing both **Signal** and **Telegram** bot implementations for searching and retrieving torrents. Users can search for torrents using either messaging platform and get magnet links to download content.

## Features

### Telegram Bot
- **Search torrents**: Use `/categories` to see available categories, then send `torrent - <search_term> - <category> - <subcategory>`
- **Browse results**: View top 10 torrents sorted by seeders
- **Get magnet links**: Click on a torrent to receive its magnet link
- **Help command**: Use `/help` for detailed instructions

## Requirements

- Python 3.7+
- Telegram bot token (for Telegram bot)


## Setup

### Telegram Bot
1. Create a Telegram bot via BotFather and get your token
2. Set the `token` environment variable
3. Install dependencies by running following command in the telegram directory
```
pip install -r requirements.txt
```
4. Run: `python -m telegram.bot`


## Project Structure

- `core/`: Core functionality for torrent search and magnet link generation
- `telegram/`: Telegram bot implementation
- `signal/`: Signal bot implementation
- `requirements.txt`: Python dependencies


# Rust Signal Bot

A Rust-based bot that interfaces with `signal-cli` to handle messages, search for torrents, and manage downloads via Transmission.

## Features

* **Message Polling:** Efficiently listens for messages using `signal-cli` in JSON-RPC mode.
* **Search Torrents:**
    * Command: `Links for <query>`
    * Searches a configured API (e.g., APIBay).
    * Sorts by seeders (descending) and filters out low-health torrents.
    * Returns formatted magnet links.
* **Download Manager:**
    * Command: `download <magnet_link>`
    * Adds torrents directly to a local Transmission daemon.
* **Status Monitoring:**
    * Command: `status`
    * Reports the progress, name, and status (Downloading/Seeding/Idle) of active torrents.
* **Self-Interaction:** Works with "Note to Self" for easy testing.

## Prerequisites

1.  **Rust:** Installed via [rustup](https://rustup.rs/).
2.  **signal-cli:**
    * Must be installed and in your system `PATH`.
    * **Important:** You must link or register an account before running the bot.
    * *Example:* `signal-cli link -n "bot-device"`
3.  **Transmission:**
    * `transmission-daemon` and `transmission-cli` (specifically `transmission-remote`) must be installed.
    * *Ubuntu/Debian:* `sudo apt install transmission-daemon transmission-cli`

## Project Structure

This project is modularized into the following structure:

```text
signal_bot/
├── Cargo.toml       # Dependencies (tokio, serde, reqwest, etc.)
└── src/
    ├── main.rs      # Entry point and main event loop
    ├── commands.rs  # Business logic (Links, Download, Status commands)
    ├── models.rs    # Data structures (Torrent structs)
    └── rpc.rs       # JSON-RPC request/response handling

```

## Installation & Setup

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd signal_bot

```


2. **Build the project:**
```bash
cargo build --release

```



## Usage

The bot requires the `API_URL` and `PARAMS` environment variables to be set. This allows you to configure the torrent search provider and trackers.

### Running the Bot

**Linux / macOS:**

```bash
API_URL="<>" 
PARAMS="<>"
cargo run

```
You can contact me(@kirtigautam) on my handles for these details.


### Bot Commands

Send these commands to the bot via Signal:

| Command | Example | Description |
| --- | --- | --- |
| **Ping** | `Ping` | Checks if the bot is alive. Responds with "Pong! 🏓". |
| **Links** | `Links for Ubuntu` | Searches for torrents. Returns top 10 results with magnet links. |
| **Download** | `download magnet:?xt=...` | Adds the provided magnet link to Transmission. |
| **Status** | `status` | Shows a list of current downloads with percentage and status. |

## Troubleshooting

* **Error: System configuration missing (API_URL)**
* You forgot to set the environment variable. See the "Running the Bot" section.


* **Error: Could not execute 'transmission-remote'**
* Ensure `transmission-cli` is installed and `transmission-remote` is available in your terminal.
* Verify the daemon is running (`systemctl status transmission-daemon`).


* **Bot starts but doesn't reply**
* Ensure `signal-cli` is working manually first by running `signal-cli receive`.
* Check if you are sending the message to the correct linked number.



## License

[MIT](https://www.google.com/search?q=LICENSE)

