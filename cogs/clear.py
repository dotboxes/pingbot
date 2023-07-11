import discord
from discord.ext import commands
from discord import app_commands


class clear(commands.Cog):
    def __init__(self, client: commands.bot):
        self.client = client

    @app_commands.command(name="guide", description="List of Commands")
    async def clear(self, interaction: discord.Interaction):
        """Clears Messages"""
        count = None;
        if count is None or count < 1:
            nmb = "you want to clear negative messages?"
            nmb_cb = f"```python\n{nmb}\n```"
            await interaction.response.send_message(nmb_cb, ephemeral=True, delete_after=3.5, )
            return

        def is_bot_message(message):
            from main import client
            return message.author.id == client.user.id and message != interaction.message

        await interaction.response.defer()

        deleted = await interaction.channel.purge(limit=count + 1, check=is_bot_message)

        code = f"Deleted {len(deleted) - 1} message(s)."
        code_block = f"```python\n{code}\n```"
        await interaction.channel.send(code_block, delete_after=2.5)


async def setup(client: commands.bot) -> None:
    await client.add_cog(clear(client))

