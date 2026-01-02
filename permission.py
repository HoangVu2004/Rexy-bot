import os
import discord

WHITELIST_FILE = "whitelisted_roles.txt"

# Load whitelisted roles from file
def load_whitelisted_roles():
    if not os.path.exists(WHITELIST_FILE):
        return set()
    
    with open(WHITELIST_FILE, "r") as file:
        return set(line.strip() for line in file.readlines())

# Save whitelisted roles to file
def save_whitelisted_roles(roles):
    with open(WHITELIST_FILE, "w") as file:
        file.writelines(f"{role}\n" for role in roles)

# Check if user has a whitelisted role
def is_whitelisted(member: discord.Member):
    whitelisted_roles = load_whitelisted_roles()
    admin_override = member.guild_permissions.administrator  # Allow admins to bypass whitelist

    if admin_override:
        return True
    
    return any(str(role.id) in whitelisted_roles for role in member.roles)
