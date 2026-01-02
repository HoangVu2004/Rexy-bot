import discord
import requests
import json
from discord import app_commands
import permission

# File path for YouTube channel ID
YT_ID_FILE = "YT-id.txt"

# Function to read YouTube Channel ID
def get_channel_id():
    try:
        with open(YT_ID_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

# Get YouTube Live or Upcoming Stream Chat ID
def get_chat_id(youtube_api_key):
    channel_id = get_channel_id()
    if not channel_id:
        return None

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={youtube_api_key}"
    response = requests.get(url)

    try:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            video_id = data["items"][0]["id"]["videoId"]
            return video_id
    except Exception as e:
        print(f"Error fetching YouTube live data: {e}")

    # If no live stream, check for upcoming streams
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=upcoming&key={youtube_api_key}"
    response = requests.get(url)

    try:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            video_id = data["items"][0]["id"]["videoId"]
            return video_id
    except Exception as e:
        print(f"Error fetching YouTube upcoming data: {e}")

    return None

# Register commands
def setup(bot):
    @bot.tree.command(name="chat", description="Fetches the YouTube live chat ID (or upcoming stream chat ID).")
    async def chat_slash(interaction: discord.Interaction):
        """Fetches the YouTube chat ID for the live or upcoming stream and displays it."""

        if not permission.is_whitelisted(interaction.user):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        config = json.load(open("config.json"))
        video_id = get_chat_id(config["youtube_api_key"])

        if video_id:
            chat_id_url = f"https://www.youtube.com/live_chat?v={video_id}"
            embed = discord.Embed(title="🔗 YouTube Live Chat ID", color=discord.Color.blue())
            embed.description = f"```{chat_id_url}```"
            embed.set_footer(text="Click the copy button to copy the link.")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ No live or upcoming streams found.", ephemeral=True)
