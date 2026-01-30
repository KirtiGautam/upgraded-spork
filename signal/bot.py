"""Signal bot helper module with commands and initialization."""

import os
import logging
import subprocess
from signalbot import SignalBot, Command, Context, regex_triggered, enable_console_logging
from core import torrents as core_torrents
from core.constants import TRACKERS


def initialize_bot():
    """Initialize and configure the Signal bot."""
    enable_console_logging(logging.INFO)
    print("Starting Signal Bot")

    bot = SignalBot({
        "signal_service": os.environ["SIGNAL_SERVICE"],
        "phone_number": os.environ["PHONE_NUMBER"]
    })
    print("Bot initialized")
    
    bot = register_handlers(bot)
    print("Commands registered: PingCommand, DownloadMovieCommand, TorrentDownloadCommand")
    
    print("Starting bot listener...")
    bot.start()



def register_handlers(bot):
    """Register all commands and handlers for the Signal bot."""
    
    class PingCommand(Command):
        @regex_triggered("Ping")
        async def handle(self, c: Context) -> None:
            await c.send("Pong")

    class DownloadMovieCommand(Command):
        @regex_triggered(r"^download movie\s+(.+)$")
        async def handle(self, c: Context) -> None:
            # Extract movie name from the regex capture group
            movie_name = c.message.text.replace("download movie", "", 1).strip()
            
            print(f"Download movie command triggered for: {movie_name}")

            if not movie_name:
                print("No movie name provided in download movie command")
                await c.send("Please specify a movie name. Format: 'download movie <movie_name>'")
                return

            # Use core library to fetch torrents
            try:
                torrents = core_torrents.list_torrents(movie_name)
                
                if not torrents:
                    print(f"No torrents found for '{movie_name}'")
                    await c.send(f"No torrents found for '{movie_name}'")
                    return

                # Filter: keep only seeders >= 5
                filtered_torrents = [t for t in torrents if int(t.get("seeders", 0)) >= 5]
                
                if not filtered_torrents:
                    print(f"No torrents with sufficient seeders found for '{movie_name}'")
                    await c.send(f"No torrents with seeders >= 5 found for '{movie_name}'")
                    return

                print(f"Found {len(filtered_torrents)} torrents for '{movie_name}'")
                response = "Found torrents:\n\n"
                for i, result in enumerate(filtered_torrents, 1):
                    # Use core library to generate magnet link with Signal trackers
                    magnet_link = core_torrents.generate_magnet_link(result['info_hash'], with_trackers=False)
                    response += f"{i}. {result['name']}\n"
                    response += f"Seeders: {result['seeders']}\n"
                    response += f"{magnet_link}\n\n"

                await c.send(response)

            except Exception as e:
                print(f"Error fetching torrents for '{movie_name}': {e}")
                await c.send(f"Error fetching torrents: {str(e)}")

    class TorrentDownloadCommand(Command):
        @regex_triggered(r"^download\s+(magnet:\?.+)$")
        async def handle(self, c: Context) -> None:
            # Extract magnet link from the regex capture group
            magnet_link = c.message.text.replace("download", "", 1).strip()
            
            print(f"Torrent download command triggered for magnet link: {magnet_link}")

            if not magnet_link.startswith("magnet:"):
                print("Invalid magnet link provided")
                await c.send("Invalid magnet link. Please provide a valid magnet link starting with 'magnet:'")
                return

            try:
                # Execute transmission-remote command
                command = ["transmission-remote", "-a", f'{magnet_link}{TRACKERS}']
                print(f"Executing command: {' '.join(command)}")
                
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    print(f"Successfully added torrent: {magnet_link}")
                    await c.send("✓ Torrent added to transmission successfully!")
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    print(f"Error adding torrent: {error_msg}")
                    await c.send(f"✗ Error adding torrent: {error_msg}")

            except subprocess.TimeoutExpired:
                print("Torrent download command timed out")
                await c.send("✗ Command timed out while adding torrent")
            except FileNotFoundError:
                print("transmission-remote not found")
                await c.send("✗ transmission-remote is not installed or not in PATH")
            except Exception as e:
                print(f"Error executing transmission-remote: {e}")
                await c.send(f"✗ Error: {str(e)}")

    # Register all commands
    bot.register(PingCommand())
    bot.register(DownloadMovieCommand())
    bot.register(TorrentDownloadCommand())
    print("Commands registered: PingCommand, DownloadMovieCommand, TorrentDownloadCommand")
    
    return bot

initialize_bot()