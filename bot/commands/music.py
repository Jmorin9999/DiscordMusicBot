import discord
from discord.ext import commands
from pytube import YouTube
import asyncio
from .utils.json_handler import load_json, save_json

SongQueue = []

def setup(bot):
    @bot.command(name='play')
    async def play(ctx, *, url: str):
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            SongQueue.append(url)
            yt = YouTube(url)
            await ctx.send(f"Added to queue: {yt.title}")
        else:
            await join_voice_channel(ctx.author.voice.channel.id)
            await play_music(ctx, url)

    async def play_music(ctx, url):
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client:
            voice_client.stop()
            options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            voice_client.play(discord.FFmpegPCMAudio(stream.url, before_options=options), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

    async def join_voice_channel(channel_id):
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.connect()

    async def play_next(ctx):
        if SongQueue:
            url = SongQueue.pop(0)
            await play_music(ctx, url)

    @bot.command(name='queue')
    async def queue(ctx):
        if SongQueue:
            queue_message = "\n".join([f"{index+1}. {url}" for index, url in enumerate(SongQueue)])
            await ctx.send(f"Current Queue:\n{queue_message}")
        else:
            await ctx.send("The queue is empty.")
    
    # Other music commands can be added here
