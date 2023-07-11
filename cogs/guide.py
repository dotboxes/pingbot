import discord
from discord.ext import commands
from discord import app_commands


class guide(commands.Cog):
    def __init__(self, client: commands.bot):
        self.client = client

    @app_commands.command(name="guide", description="List of Commands")
    async def guide(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message(content=
                                                    "/ping - pings a user \n/clear - deletes bots "
                                                    "messages\n/clearthreads -"
                                                    "deletes bots threads\n"
                                                    "/setimage - use link to set image")
        except (TypeError, discord.errors.NotFound):
            pass  # ignores notFound error


async def setup(client: commands.bot) -> None:
    await client.add_cog(guide(client))
