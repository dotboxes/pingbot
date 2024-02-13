from keep_alive import keep_alive
keep_alive()
from typing import Literal, Optional, Union
import discord
import aiohttp
import asyncio
import os


from discord import Embed
from discord.ext import commands
from discord.ext.commands import errors
from discord.ext.commands import Greedy, Context


TOKEN = os.environ.get('TOKEN')
async def guild_fetch():
    guild_id = 123
    guild = await client.fetch_guild(guild_id)
    print(guild.name)

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)


@client.event
async def on_ready():
    print('Bot {0.user}'.format(client) + ' is now online')


@client.tree.command()
async def guide(interaction: discord.Interaction):
    """Guide"""  # Description when viewing / commands
    try:
        await interaction.response.send_message("/ping - pings a user \n/clear - deletes bots messages\n/clearthreads - "
                                            "deletes bots threads\n"
                                            "/setimage - use link to set image")
    except (TypeError, discord.errors.NotFound):
        pass #ignores notFound error


@client.command()
async def alert(ctx, target: Union[discord.Role, discord.Member], count: int):
    if count <= 0:
        await ctx.send("Please provide a positive number of pings.")
        return

    if isinstance(target, discord.Role):
        mention_string = target.mention

        try:
            for _ in range(count):
                await ctx.send(mention_string)
        except discord.errors.NotFound:
            await ctx.send("No role found.")
    elif isinstance(target, discord.Member):
        if not target.mention:
            await ctx.send("Please mention the user.")
            return

        if isinstance(ctx.channel, discord.Thread):
            try:
                for _ in range(count):
                    await ctx.send(target.mention)
            except discord.errors.NotFound:
                await ctx.send("No user found.")
        else:
            MAX_PINGS = 15  # Maximum number of pings allowed
            THREAD_DURATION = 2  # Duration in hours before thread deletion

            if count > MAX_PINGS:
                await ctx.send(f"Only up to {MAX_PINGS} pings are allowed. It may get glitchy after that.")
                return

            for i in range(count):
                await ctx.send(target.mention)

                if i + 1 == MAX_PINGS:
                    await ctx.send(f"Creating a thread for {target.display_name}...")
                    thread = await ctx.channel.create_thread(name=f"Pings for {target.display_name}", private=False)
                    await asyncio.sleep(THREAD_DURATION * 3600)  # Convert hours to seconds
                    await thread.delete()
    else:
        await ctx.send("Invalid target. Please mention a user or specify a role.")


MAX_PINGS = 15  # Maximum number of pings allowed
THREAD_DURATION = 2  # Duration in hours before thread deletion

@client.event
async def on_command_error(interaction: discord.Interaction, error):
    if isinstance(error, errors.MemberNotFound):
        await interaction.response.send_message.send("no user found bozo")


@client.tree.command()
async def clear(interaction: discord.Interaction, count: int = None):
    """Clears Messages"""
    if count is None or count < 1:
        nmb = "you want to clear negative messages?"
        nmb_cb = f"```python\n{nmb}\n```"
        await interaction.response.send_message(nmb_cb, ephemeral=True, delete_after=3.5, )
        return

    def is_bot_message(message):
        return message.author.id == client.user.id and message != interaction.message

    await interaction.response.defer()

    deleted = await interaction.channel.purge(limit=count + 1, check=is_bot_message)

    code = f"Deleted {len(deleted) - 1} message(s)."
    code_block = f"```python\n{code}\n```"
    await interaction.channel.send(code_block, delete_after=2.5)
  

@client.tree.command()
async def clearthreads(ctx: discord.Interaction):
    """Clear Threads"""

    def is_bot_thread(t):
        return t.archived and t.owner == ctx.guild.me

    deleted_threads = 0
    for thread in ctx.channel.threads:
        if is_bot_thread(thread):
            await thread.delete()
            deleted_threads += 1

    await ctx.response.send_message(f"Deleted {deleted_threads} thread(s).", ephemeral=True, delete_after=5)


@client.tree.command()
async def setimage(interaction: discord.Interaction, url: str):
    """Use a link to change the image. Make sure your focus is in the center of the image since you can't adjust it."""
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


bot_owner_id = client.owner_id


@client.command(aliases=['embedsay'])
async def say(ctx, title: str, description: str, *, color: discord.Color = discord.Color(0xFFFFFF)):
    embed = discord.Embed(title=title, description=description, color=color)
    await ctx.message.delete()
    await ctx.send(embed=embed)


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

