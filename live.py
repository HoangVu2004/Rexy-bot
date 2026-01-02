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

# Function to update YouTube Channel ID
def set_channel_id(new_id):
    with open(YT_ID_FILE, "w") as file:
        file.write(new_id.strip())

# Get YouTube Live Stream Info
def get_live_stream(youtube_api_key):
    channel_id = get_channel_id()
    if not channel_id:
        return None

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={youtube_api_key}"
    response = requests.get(url)

    try:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            stream = data["items"][0]["snippet"]
            title = stream["title"]
            channel_name = stream["channelTitle"]
            video_id = data["items"][0]["id"]["videoId"]
            live_url = f"https://www.youtube.com/watch?v={video_id}"
            return channel_name, title, live_url
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")

    return None

# Get YouTube Scheduled Live Streams (Upcoming)
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
                streams.append((channel_name, title, live_url))
            return streams
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")

    return None

# Register commands
def setup(bot):
    @bot.tree.command(name="live", description="Check if the YouTube channel is live (falls back to upcoming streams)")
    async def live_slash(interaction: discord.Interaction):
        """Checks if the YouTube channel is live, and if not, fetches upcoming streams instead."""

        if not permission.is_whitelisted(interaction.user):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        config = json.load(open("config.json"))
        live_stream = get_live_stream(config["youtube_api_key"])

        if live_stream:
            channel_name, title, live_url = live_stream
            message = f"**{channel_name}** is now live! 🎥\n**Title:** {title}\n🔴 Watch here: {live_url}"
            await interaction.response.send_message(message)
        else:
            # No live streams, check for upcoming ones
            upcoming_streams = get_upcoming_streams(config["youtube_api_key"])
            if upcoming_streams:
                message = ""
                for channel_name, title, live_url in upcoming_streams:
                    message += f"📅 **{title}** by **{channel_name}**\n🔗 Watch: {live_url}\n\n"
                await interaction.response.send_message(message)
            else:
                await interaction.response.send_message("The channel is **not live** and has no upcoming streams.", ephemeral=True)

    @bot.tree.command(name="setliveid", description="Change the YouTube channel ID for live checking")
    async def set_live_id(interaction: discord.Interaction, new_id: str):
        """Allows whitelisted users to change the YouTube channel ID stored in YT-id.txt"""

        if not permission.is_whitelisted(interaction.user):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        set_channel_id(new_id)
        await interaction.response.send_message(f"✅ YouTube Channel ID has been updated to `{new_id}`.", ephemeral=True)
