import discord
from discord import app_commands
import permission

# Register commands
def setup(bot):
    @bot.tree.command(name="rexyadd", description="Add a role to the whitelist (Admins only)")
    async def rexyadd(interaction: discord.Interaction, role: discord.Role):
        """Adds a role to the whitelist (Admin-only command)."""

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only **admins** can use this command.", ephemeral=True)
            return

        whitelisted_roles = permission.load_whitelisted_roles()
        
        if str(role.id) in whitelisted_roles:
            await interaction.response.send_message(f"✅ Role **{role.name}** is already whitelisted.", ephemeral=True)
            return

        whitelisted_roles.add(str(role.id))
        permission.save_whitelisted_roles(whitelisted_roles)
        
        await interaction.response.send_message(f"✅ Role **{role.name}** has been added to the whitelist.", ephemeral=True)

    @bot.tree.command(name="rexyremove", description="Remove a role from the whitelist (Admins only)")
    async def rexyremove(interaction: discord.Interaction, role: discord.Role):
        """Removes a role from the whitelist (Admin-only command)."""

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only **admins** can use this command.", ephemeral=True)
            return

        whitelisted_roles = permission.load_whitelisted_roles()
        
        if str(role.id) not in whitelisted_roles:
            await interaction.response.send_message(f"❌ Role **{role.name}** is not in the whitelist.", ephemeral=True)
            return

        whitelisted_roles.remove(str(role.id))
        permission.save_whitelisted_roles(whitelisted_roles)
        
        await interaction.response.send_message(f"✅ Role **{role.name}** has been removed from the whitelist.", ephemeral=True)
