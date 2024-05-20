import discord
from discord.ext import commands
from pytube import YouTube
import asyncio
import os
import datetime
import json
from discord.voice_client import VoiceClient
# brandon if you are reading this you are a stinky human HAHHAHAHHAHAHAH

POINTS_FILE = 'user_points.json'

permissions_integer = 274948226688
permissions_numeric = int(permissions_integer)
permissions_obj = discord.Permissions(permissions=permissions_numeric)
intents_value = 274948226688  

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), permissions=permissions_obj)

voice_client = None

# Queue to store URLs
SongQueue = []
# Store all bets here
Bets = []

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

#load points from POINTS_FILE   
def load_points():
    if os.path.exists(POINTS_FILE):
        try:
            with open(POINTS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {POINTS_FILE} contains invalid JSON.")
            return {}
        except Exception as e:
            print(f"Error reading {POINTS_FILE}: {e}")
            return {}
    return {}

#saves points to POINTS_FILE
def save_points(points):
    try:
        with open(POINTS_FILE, 'w') as f:
            json.dump(points, f)
    except Exception as e:
        print(f"Error saving to {POINTS_FILE}: {e}")   

user_points = load_points()       

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
async def points(ctx):
    try:
        user = str(ctx.author)
        points = user_points.get(user, 100)  # Default to 100 points if user is not in the system
        await ctx.send(f'{user}, you have {points} points.')
    except Exception as e:
        await ctx.send("An error occurred while retrieving your points.")
        print(f"Error in points command: {e}") 
        
@bot.command()
async def bet(ctx, amount: int, game: str, bet_type: str):
    try:
        user = str(ctx.author)
        user_points.setdefault(user, 100)  # Ensure user has an entry in the points dictionary

        if user_points[user] < amount:
            await ctx.send(f'{user}, you do not have enough points to place this bet.')
            return

        if bet_type.lower() not in ['win', 'lose']:
            await ctx.send(f'{user}, invalid bet type. Please use "win" or "lose".')
            return

        # Deduct points and record the bet
        user_points[user] -= amount
        bets.append({'user': user, 'amount': amount, 'game': game, 'type': bet_type.lower()})
        save_points(user_points)
        await ctx.send(f'{user} has placed a bet of {amount} points on {game} to {bet_type}.')
    except Exception as e:
        await ctx.send("An error occurred while placing your bet.")
        print(f"Error in bet command: {e}")

@bot.command()
async def resolve(ctx, game: str, outcome: str):
    try:
        global bets
        total_bet_points = sum(bet['amount'] for bet in bets if bet['game'] == game)
        if outcome.lower() not in ['win', 'lose']:
            await ctx.send(f'Invalid outcome. Please use "win" or "lose".')
            return

        winners = [bet for bet in bets if bet['game'] == game and bet['type'] == outcome.lower()]

        if not winners:
            await ctx.send(f'No winners for the game {game}.')
            return

        points_per_winner = total_bet_points // len(winners)
        
        for winner_bet in winners:
            user_points[winner_bet['user']] += points_per_winner + winner_bet['amount']

        # Remove resolved bets
        bets = [bet for bet in bets if bet['game'] != game]
        save_points(user_points)

        await ctx.send(f'Game {game} resolved. Each winner receives {points_per_winner} points.')
        leaderboard()
    except Exception as e:
        await ctx.send("An error occurred while resolving the game.")
        print(f"Error in resolve command: {e}")
        
@bot.command()
async def leaderboard(ctx):
    try:
        sorted_users = sorted(user_points.items(), key=lambda item: item[1], reverse=True)
        leaderboard_message = "Leaderboard:\n"
        for user, points in sorted_users:
            leaderboard_message += f'{user}: {points} points\n'
        await ctx.send(leaderboard_message)
    except Exception as e:
        await ctx.send("An error occurred while generating the leaderboard.")
        print(f"Error in leaderboard command: {e}")

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    #jacob if you read this u are a N F R :D
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