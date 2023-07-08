from typing import Literal, Optional
import discord
from discord.ext import commands
from discord.ext.commands import errors
from discord.ext.commands import Greedy, Context
from discord import Interaction
from discord import app_commands
import aiohttp
import asyncio

TOKEN = 'hidden'

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)


@client.event
async def on_ready():
    print('Bot {0.user}'.format(client) + ' is now online')


@client.tree.command()
async def guide(interaction: discord.Interaction):
    """Guide"""  # Description when viewing / commands
    await interaction.response.send_message("/ping - pings a user \n/clear - deletes bots messages\n/clearthreads - "
                                            "deletes bots threads\n"
                                            "/setimage - use link to set image")


@client.tree.command()
async def ping(interaction: discord.Interaction, user: discord.Member, count: int):
    """PING MATTHEW!!!"""
    if count <= 0:
        await interaction.response.send_message("Please provide a positive number of pings.")
        return

    if not user.mention:
        await interaction.response.send_message("bruh you forgot the @")
        return

    try:
        if isinstance(interaction.response.send_message.channel, discord.Thread):
            try:
                for _ in range(count):
                    await interaction.response.send_message.send(user.mention)
            except errors.MemberNotFound:
                await interaction.response.send_message.send("No user found, bozo")
        else:
            if count > MAX_PINGS:
                await interaction.response.send_message.send(
                    f"Only up to {MAX_PINGS} pings. Gets a bit glitchy after :pensive: \nThere is no limit in "
                    f"threads")
                return
            for i in range(count):
                await interaction.response.send_message.send(user.mention)

                if i + 1 == MAX_PINGS:
                    # Create a thread after reaching the maximum number of pings
                    await interaction.response.send_message.send(f"Creating a thread for {user.display_name}...")
                    thread = await interaction.response.send_message.channel.create_thread(
                        name=f"Pings for {user.display_name}", private=False)
                    # Schedule thread deletion after a specified duration
                    await asyncio.sleep(THREAD_DURATION * 3600)  # Convert hours to seconds
                    await thread.delete()
    except errors.MemberNotFound:
        await interaction.response.send_message.send("")


MAX_PINGS = 15  # Maximum number of pings allowed
THREAD_DURATION = 2  # Duration in hours before thread deletion


@client.event
async def on_command_error(interaction: discord.Interaction, error):
    if isinstance(error, errors.MemberNotFound):
        await interaction.response.send_message.send("no user found bozo")


@client.tree.command()
async def clear(interaction: discord.Interaction):
    """Clears Messages"""

    def is_bot(m):
        return m.author == client.user

    deleted = await interaction.response.send_message.channel.purge(limit=None, check=is_bot)
    await interaction.response.send_message.send(f"Deleted {len(deleted)} message(s).", delete_after=5)


@client.tree.command()
async def clearthreads(interaction: discord.Interaction):
    """Clear Threads"""

    def is_bot_thread(t):
        return t.archived and t.owner == client.user

    deleted_threads = await interaction.response.send_message.channel.purge(limit=None, check=is_bot_thread,
                                                                            before=None, after=None)
    await interaction.response.send_message.send(f"Deleted {len(deleted_threads)} thread(s).", delete_after=5)


@client.tree.command()
async def setimage(interaction: discord.Interaction, url: str):
    """Use a link to change the image. Make sure your focus is in the center of the image since you can't adjust it."""  #
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image = await response.read()
                    await client.user.edit(avatar=image)
                    await interaction.response.send_message.send("Bot image has been updated successfully.")
                else:
                    await interaction.response.send_message.send("Failed to retrieve image from URL.")
    except aiohttp.ClientError:
        await interaction.response.send_message.send("Failed to update bot image.")


guild = discord.Object(id='hidden')
# Sync Code


@client.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
        ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


client.run(TOKEN)
