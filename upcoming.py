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

# Get YouTube Scheduled Live Streams
def get_upcoming_streams(youtube_api_key):
    channel_id = get_channel_id()
    if not channel_id:
        return None

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=upcoming&key={youtube_api_key}"
    response = requests.get(url)

    try:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            streams = []
            for item in data["items"]:
                title = item["snippet"]["title"]
                channel_name = item["snippet"]["channelTitle"]
                video_id = item["id"]["videoId"]
                live_url = f"https://www.youtube.com/watch?v={video_id}"
                scheduled_time = item["snippet"]["publishedAt"]  # Scheduled time of the stream
                streams.append((channel_name, title, live_url, scheduled_time))
            return streams
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")

    return None

# Register command
def setup(bot):
    @bot.tree.command(name="upcoming", description="Check for upcoming YouTube live streams")
    async def upcoming_slash(interaction: discord.Interaction):
        """Checks for upcoming YouTube live streams and sends a message in the same channel (Slash Command)."""

        if not permission.is_whitelisted(interaction.user):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        config = json.load(open("config.json"))
        upcoming_streams = get_upcoming_streams(config["youtube_api_key"])

        if upcoming_streams:
            message = "**Upcoming Live Streams:**\n"
            for channel_name, title, live_url, scheduled_time in upcoming_streams:
                message += f"📅 **{title}** by **{channel_name}**\n🔗 Watch: {live_url}\n🕒 Scheduled: {scheduled_time}\n\n"
            await interaction.response.send_message(message)
        else:
            await interaction.response.send_message("No upcoming live streams found.", ephemeral=True)
