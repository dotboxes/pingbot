from typing import Literal, Optional, Union
import discord
from discord.ext import commands
from colorama import Back, Fore, Style
import time
import os
import platform

import asyncio
from discord.ext.commands import errors
from discord.ext.commands import Greedy, Context
from keep_alive import keep_alive
keep_alive()

TOKEN = os.environ.get('token')
guild = discord.Object(id='hidden')


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=discord.Intents().all())

        self.cogslist = ["cogs.ping", "cogs.guide", "cogs.clear", "cogs.setimage", "cogs.clearthreads"]

    async def setup_hook(self):
        for ext in self.cogslist:
            await self.load_extension(ext)

    async def on_ready(self):
        prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S UTC",
                                                        time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(prfx + " Logged in as " + Fore.YELLOW + self.user.name)
        print(prfx + " Bot ID " + Fore.YELLOW + str(self.user.id))
        print(prfx + " Discord Version " + Fore.YELLOW + discord.__version__)
        print(prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()))
        synced = await self.tree.sync()
        print(prfx + " Slash CMDs Synced " + Fore.YELLOW + str(len(synced)) + " Commands")

client = Client()

client.run(TOKEN)


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
        await interaction.followup.send("no user found bozo")


@client.command()
async def clear_bot_messages(ctx, limit: int = 100):
    def is_bot_message(message):
        return message.author.bot

    deleted = await ctx.channel.purge(limit=limit + 1,
                                      check=is_bot_message)  # Add 1 to include the command message itself
    await ctx.send(f'Deleted {len(deleted)} bot message(s).')  # Subtract 1 to exclude the command message





bot_owner_id = client.owner_id


@client.command(aliases=['embedsay'])
@commands.is_owner()
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
