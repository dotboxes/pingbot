import aiohttp
import discord
from discord.ext import commands
from discord import app_commands


class setimage(commands.Cog):
    def __init__(self, client: commands.bot):
        self.client = client

    @app_commands.command(name="setimage", description="Use a link to change the image.")
    async def setimage(self, interaction: discord.Interaction, url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image = await response.read()
                        bot_user = interaction.client.user
                        await bot_user.edit(avatar=image)
                        await interaction.response.send_message("Bot image has been updated successfully.")
                    else:
                        await interaction.response.send_message("Failed to retrieve image from URL.")
        except aiohttp.ClientError:
            await interaction.response.send_message("Failed to update bot image.")


async def setup(client: commands.bot) -> None:
    await client.add_cog(setimage(client))
