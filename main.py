import discord
import json
import datetime
import os
import sys
import asyncio
from discord.ext import commands
from discord import app_commands

# Import modules
import live
import whitelist
import permission
import upcoming
import chat
import vid
import sync


# File paths
CONFIG_FILE = "config.json"
LOG_FILE = "run-log.txt"

# Load configuration
def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {CONFIG_FILE} not found!")
        exit()
    except json.JSONDecodeError as e:
        print(f"Error parsing {CONFIG_FILE}: {e}")
        exit()

config = load_config()
BOT_TOKEN = config["bot_token"]
GUILD_ID = discord.Object(id=int(config["guild_id"]))

# Log bot startup
with open(LOG_FILE, 'a') as file:
    file.write(f'[{datetime.datetime.now()}] Bot started\n')

# Bot intents
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("/"), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        try:
            await self.tree.sync()
            print("✅ Slash commands synced globally!")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

bot = MyBot()

# Restart the bot
async def restart_bot():
    await bot.close()  # Close bot connection
    os.execv(sys.executable, ['python'] + sys.argv)  # Restart bot process

# Shutdown the bot
async def shutdown_bot():
    await bot.close()  # Close the bot connection
    os._exit(0)  # Force exit without throwing an exception


# Restart command
@bot.tree.command(name="restart", description="Restart the bot (Admins/Whitelisted users only)")
async def restart(interaction: discord.Interaction):
    if not permission.is_whitelisted(interaction.user):
        return  # Ignore command if not authorized

    await interaction.response.send_message("🟢 **Restarting...**", ephemeral=True)
    await asyncio.sleep(2)  # Small delay for user response visibility
    await restart_bot()

# Shutdown command
@bot.tree.command(name="shutdown", description="Shutdown the bot (Admins/Whitelisted users only)")
async def shutdown(interaction: discord.Interaction):
    if not permission.is_whitelisted(interaction.user):
        return  # Ignore command if not authorized

    await interaction.response.send_message("🔴 **Shutting down...**", ephemeral=True)
    await asyncio.sleep(2)  # Small delay for user response visibility
    await shutdown_bot()

# Load commands
live.setup(bot)
whitelist.setup(bot)
upcoming.setup(bot)
chat.setup(bot)
vid.setup(bot)
sync.setup(bot)

# Run the bots
bot.run(BOT_TOKEN)
