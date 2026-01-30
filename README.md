# Torrent Bots

A project providing both **Signal** and **Telegram** bot implementations for searching and retrieving torrents. Users can search for torrents using either messaging platform and get magnet links to download content.

## Features

### Telegram Bot
- **Search torrents**: Use `/categories` to see available categories, then send `torrent - <search_term> - <category> - <subcategory>`
- **Browse results**: View top 10 torrents sorted by seeders
- **Get magnet links**: Click on a torrent to receive its magnet link
- **Help command**: Use `/help` for detailed instructions

### Signal Bot
- **Download movies**: Use `download movie <movie_name>` to search and get torrents with seeders ≥ 5
- **Download torrents**: Use `download <magnet_link>` to add torrents to transmission
- **Ping command**: Use `Ping` to verify bot is running

## Requirements

- Python 3.7+
- Telegram bot token (for Telegram bot)
- Signal service setup (for Signal bot)
- transmission-remote (for Signal bot torrent downloads)

## Setup

### Telegram Bot
1. Create a Telegram bot via BotFather and get your token
2. Set the `token` environment variable
3. Install dependencies by running following command in the telegram directory
```
pip install -r requirements.txt
```
4. Run: `python -m telegram.bot`

### Signal Bot
1. Set up Signal service with environment variables:
   - `SIGNAL_SERVICE`: Signal service endpoint
   - `PHONE_NUMBER`: Bot's phone number
2. Ensure `transmission-remote` is installed for downloading
3. Install dependencies by running following command in the signal directory
```
pip install -r requirements.txt
``` 
4. Run: `python -m signal.bot`

## Project Structure

- `core/`: Core functionality for torrent search and magnet link generation
- `telegram/`: Telegram bot implementation
- `signal/`: Signal bot implementation
- `requirements.txt`: Python dependencies

