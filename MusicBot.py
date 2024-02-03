import discord
from discord.ext import commands
from pytube import YouTube
import asyncio
import os
import datetime
from discord.voice_client import VoiceClient
# brandon if you are reading this you are a stinky human HAHHAHAHHAHAHAH

permissions_integer = 274948226688
permissions_numeric = int(permissions_integer)
permissions_obj = discord.Permissions(permissions=permissions_numeric)
intents_value = 274948226688  

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), permissions=permissions_obj)

voice_client = None

# Queue to store URLs
SongQueue = []

# Function to join a voice channel
async def join_voice_channel(channel_id):
    global voice_client
    try:
        channel = bot.get_channel(channel_id)
        if channel:
            voice_client = await channel.connect()
            print(f"Joined voice channel: {channel.name}")
        else:
            print("Voice channel not found.")
    except Exception as e:
        print(f"Error joining voice channel: {e}")

async def disconnect_from_voice_channel(ctx):
    global voice_client
    if voice_client is not None:
        await voice_client.disconnect()
        voice_client = None

# Function to play music
async def PlayMusic(ctx, url):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client:
            voice_client.stop()
            options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"  # Buffering options
            voice_client.play(discord.FFmpegPCMAudio(stream.url, before_options=options), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
            print(f"Now playing: {yt.title}")
        else:
            await join_voice_channel(ctx)
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"  # Buffering options
            voice_client.play(discord.FFmpegPCMAudio(stream.url, before_options=options), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
            print(f"Now playing: {yt.title}")
    except Exception as e:
        print(f"Error playing music: {e}")

async def play_next(ctx):
    global SongQueue
    if SongQueue:
        url = SongQueue.pop(0)
        await PlayMusic(ctx, url)

async def poll_voice_ws(voice_client):
    try:
        await voice_client.ws.poll_event()
    except asyncio.TimeoutError:
        if voice_client.is_playing():
            # Resume playing the song if the voice client was playing
            voice_client.resume()
            print("Resuming playback after reconnecting.")
        else:
            print("Voice connection was lost, but no song was playing.")

def connect_to_voice_channel(channel_id):
    global voice_client
    if voice_client is None:
        asyncio.run_coroutine_threadsafe(join_voice_channel(channel_id), bot.loop).result()

# All bot commands start here
@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    if channel:
        await channel.connect()
        print(f"Joined voice channel: {channel.name}")
    else:
        await ctx.send("You are not in a voice channel.")

@bot.command()
async def play(ctx, *, url: str):
    global SongQueue
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        # Add the URL to the queue
        SongQueue.append(url)
        yt = YouTube(url)
        await ctx.send(f"Added to queue: {yt.title}")
    else:
        await join_voice_channel(ctx.author.voice.channel.id)
        await PlayMusic(ctx, url)

@bot.command()
async def queue(ctx):
    if SongQueue:
        queue_message = "\n".join([f"{index+1}. {url}" for index, url in enumerate(SongQueue)])
        await ctx.send(f"Current Queue:\n{queue_message}")
    else:
        await ctx.send("The queue is empty.")

@bot.command()
async def clear(ctx):
    global SongQueue
    SongQueue.clear()
    await ctx.send("Queue cleared.")

@bot.command()
async def skip(ctx):
    global voice_client
    if voice_client is not None and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Skipping the current song.")
    else:
        await ctx.send("No song is currently playing.")

@bot.command()
async def stop(ctx):
    global voice_client
    if voice_client is not None and voice_client.is_playing():
        voice_client.stop()
        print("Music stopped.")
    else:
        print("No music is playing.")

@bot.command()
async def disconnect(ctx):
    try:
        await disconnect_from_voice_channel(ctx)
    except Exception as e:
        print(f"Error occurred during disconnection: {e}")

@bot.command()
async def Stink(ctx):
    StinkMessage = "Carson Stinks!  EW!!"
    await ctx.send(StinkMessage)


bot.run('')