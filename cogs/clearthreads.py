import discord
from discord.ext import commands
from discord import app_commands


class clearthreads(commands.Cog):
    def __init__(self, client: commands.bot):
        self.client = client

    @app_commands.command(name="clearthreads", description="Clears threads")
    async def clearthreads(self, interaction: discord.Interaction):
        """Clear Threads"""

        def is_bot_thread(t):
            return t.archived and t.owner == interaction.guild.me

        deleted_threads = 0
        for thread in interaction.channel.threads:
            if is_bot_thread(thread):
                await thread.delete()
                deleted_threads += 1

        await interaction.response.send_message(f"Deleted {deleted_threads} thread(s).", ephemeral=True, delete_after=5)


async def setup(client: commands.bot) -> None:
    await client.add_cog(clearthreads(client))
