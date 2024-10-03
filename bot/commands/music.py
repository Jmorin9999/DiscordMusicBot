import discord
from discord.ext import commands
from pytubefix import YouTube
from pytubefix.cli import on_progress
import asyncio
from bot.utils.json_handler import load_json, save_json

SongQueue = []

def setup(bot):
# The play command, which uses join_voice_channel
    @bot.command(name='play')
    async def play(ctx, *, url: str):
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command.")
            return

        if voice_client and voice_client.is_playing():
            SongQueue.append(url)
            yt = YouTube(url)
            await ctx.send(f"Added to queue: {yt.title}")
        else:
            # Join the voice channel if not already connected
            await join_voice_channel(ctx)
            await play_music(ctx, url)

    async def play_music(ctx, url):
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            if not stream:
                await ctx.send("Could not retrieve audio stream from YouTube.")
                return
            
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            if voice_client:
                # Stop any currently playing audio
                voice_client.stop()
                
                # FFmpeg options for reconnecting streams
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                
                # Play the audio using FFmpegPCMAudio
                voice_client.play(discord.FFmpegPCMAudio(stream.url, **ffmpeg_options),
                                  after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
                
                await ctx.send(f"Now playing: {yt.title}")
        
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    async def join_voice_channel(ctx):
        channel = ctx.author.voice.channel  # Get the channel the user is currently in
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        if voice_client and voice_client.is_connected():
            # If already connected, move to the channel if different
            if voice_client.channel != channel:
                await voice_client.move_to(channel)
        else:
            # Not connected, so connect to the channel
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
