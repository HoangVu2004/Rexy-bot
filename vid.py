import discord
import requests
import json
from discord import app_commands
import permission

# File path for YouTube channel ID
YT_ID_FILE = "YT-id.txt"

# Read YouTube Channel ID
def get_channel_id():
    try:
        with open(YT_ID_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

# Get the most recent uploaded video (not live or upcoming)
def get_latest_video(youtube_api_key):
    channel_id = get_channel_id()
    if not channel_id:
        return None

    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&channelId={channel_id}"
        f"&order=date&type=video&maxResults=1&key={youtube_api_key}"
    )

    response = requests.get(url)

    try:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            video = data["items"][0]
            video_id = video["id"]["videoId"]
            title = video["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            return title, video_url
    except Exception as e:
        print(f"Error fetching latest video: {e}")

    return None

# Register command
def setup(bot):
    @bot.tree.command(name="vid", description="Get the latest uploaded YouTube video")
    async def vid_slash(interaction: discord.Interaction):
        """Fetches the latest uploaded video from the channel and sends the link."""

        if not permission.is_whitelisted(interaction.user):
            return  # Ignore silently

        config = json.load(open("config.json"))
        result = get_latest_video(config["youtube_api_key"])

        if result:
            title, video_url = result
            await interaction.response.send_message(f"📺 **Latest Upload:** {title}\n🔗 {video_url}")
        else:
            await interaction.response.send_message("⚠️ Couldn't find any recent uploads.", ephemeral=True)
