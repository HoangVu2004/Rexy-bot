# sync.py
import discord
import requests
import json
from discord import app_commands
import permission
import obsws_python as obs  # pip install obsws-python

YT_ID_FILE = "YT-id.txt"

# Read YouTube Channel ID
def get_channel_id():
    try:
        with open(YT_ID_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


# Fetch live or upcoming video ID
def get_chat_video_id(youtube_api_key):
    channel_id = get_channel_id()
    if not channel_id:
        return None

    # Check for live
    live_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=live&key={youtube_api_key}"
    live_response = requests.get(live_url)
    try:
        data = live_response.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0]["id"]["videoId"]
    except Exception as e:
        print(f"Error fetching live data: {e}")

    # Check for upcoming
    upcoming_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=upcoming&key={youtube_api_key}"
    upcoming_response = requests.get(upcoming_url)
    try:
        data = upcoming_response.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0]["id"]["videoId"]
    except Exception as e:
        print(f"Error fetching upcoming data: {e}")

    return None


# Connect to OBS and set browser sources
def update_obs_browser_sources(live_chat_url):
    try:
        client = obs.ReqClient(host='localhost', port=3456)  # No password

        sources = ["Chat-BIG", "Chat-SMALL"]
        scene_name = "Chat-config"

        for source in sources:
            client.set_input_settings(
                inputName=source,
                inputSettings={"url": live_chat_url},
                overlay=False
            )

        client.disconnect()
        return True
    except Exception as e:
        print(f"OBS WebSocket error: {e}")
        return False


# Register command
def setup(bot):
    @bot.tree.command(name="sync", description="Sync YouTube live chat to OBS browser sources (Chat-BIG & Chat-SMALL).")
    async def sync_slash(interaction: discord.Interaction):
        """Fetch live/upcoming chat and set OBS browser sources."""

        if not permission.is_whitelisted(interaction.user):
            return  # Ignore unauthorized users

        config = json.load(open("config.json"))
        video_id = get_chat_video_id(config["youtube_api_key"])

        if not video_id:
            await interaction.response.send_message("❌ No live or upcoming stream found.", ephemeral=True)
            return

        live_chat_url = f"https://www.youtube.com/live_chat?v={video_id}"
        success = update_obs_browser_sources(live_chat_url)

        if success:
            embed = discord.Embed(title="✅ Chat Synced to OBS", color=discord.Color.green())
            embed.description = f"Chat URL:\n```{live_chat_url}```\nApplied to:\n- Chat-BIG\n- Chat-SMALL"
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Failed to connect or update OBS sources.", ephemeral=True)
