import discord
from discord.ext import commands
from discord.ext.commands import errors
import aiohttp
import asyncio



TOKEN = 'hidden'

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)


@client.event
async def on_ready():
    print('Bot {0.user}'.format(client) + ' is now online')


@client.command()
async def guide(ctx):
    await ctx.send("/alert - pings a user")
    await ctx.send("/clear - deletes bots messages")
    await ctx.send("/clearthreads - deletes bots threads")
    await ctx.send("/setimage - use link to set image")


MAX_PINGS = 15  # Maximum number of pings allowed
THREAD_DURATION = 2  # Duration in hours before thread deletion


@client.command()
async def alert(ctx, user: discord.Member, count: int):
    if count <= 0:
        await ctx.send("Please provide a positive number of pings.")
        return

    if not user.mention:
        await ctx.send("bruh you forgot the @")
        return

    try:
        if isinstance(ctx.channel, discord.Thread):
            try:
                for _ in range(count):
                    await ctx.send(user.mention)
            except errors.MemberNotFound:
                await ctx.send("No user found, bozo")
        else:
            if count > MAX_PINGS:
                await ctx.send(
                    f"Only up to {MAX_PINGS} pings. Gets a bit glitchy after :pensive: \nThere is no limit in "
                    f"threads")
                return
            for i in range(count):
                await ctx.send(user.mention)

                if i + 1 == MAX_PINGS:
                    # Create a thread after reaching the maximum number of pings
                    await ctx.send(f"Creating a thread for {user.display_name}...")
                    thread = await ctx.channel.create_thread(name=f"Pings for {user.display_name}", private=False)
                    # Schedule thread deletion after a specified duration
                    await asyncio.sleep(THREAD_DURATION * 3600)  # Convert hours to seconds
                    await thread.delete()
    except errors.MemberNotFound:
        await ctx.send("")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, errors.MemberNotFound):
        await ctx.send("no user found bozo")


@client.command()
async def clear(ctx):
    def is_bot(m):
        return m.author == client.user

    deleted = await ctx.channel.purge(limit=None, check=is_bot)
    await ctx.send(f"Deleted {len(deleted)} message(s).", delete_after=5)

@client.command()
async def clearthreads(ctx):
    def is_bot_thread(t):
        return t.archived and t.owner == client.user

    deleted_threads = await ctx.channel.purge(limit=None, check=is_bot_thread, before=None, after=None)
    await ctx.send(f"Deleted {len(deleted_threads)} thread(s).", delete_after=5)

@client.command()
async def setimage(ctx, url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image = await response.read()
                    await client.user.edit(avatar=image)
                    await ctx.send("Bot image has been updated successfully.")
                else:
                    await ctx.send("Failed to retrieve image from URL.")
    except aiohttp.ClientError:
        await ctx.send("Failed to update bot image.")


client.run(TOKEN)
