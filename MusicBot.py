import discord
from discord.ext import commands
from pytube import YouTube
import asyncio
import os
import random
import datetime
import json
from discord.voice_client import VoiceClient
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
# brandon if you are reading this you are a stinky human HAHHAHAHHAHAHAH

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = 'YOUR_BOT_TOKEN'
POINTS_FILE = 'user_points.json'
BET_HISTORY_FILE = 'bet_history.json'
LOANS_FILE = 'loans.json'
BASE_POINTS = 500
CLAIM_POINTS = BASE_POINTS // 2
COOLDOWN_PERIOD = 3600  # Cooldown period in seconds (1 hour)
CLAIM_COOLDOWN_PERIOD = 604800  # Cooldown period for claim command in seconds (1 week)
LOAN_INTEREST_RATE = 0.1  # 10% interest on loans

permissions_integer = 274948226688
permissions_numeric = int(permissions_integer)
permissions_obj = discord.Permissions(permissions=permissions_numeric)
intents_value = 274948226688  

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), permissions=permissions_obj)

voice_client = None

# Queue to store URLs
SongQueue = []
# In-memory database for bets, loans, and locked games
bets = []
loans = []
locked_games = [] 
# Dictionary to store active roll games by channel
roll_games = {}

def load_json(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                print(f"Data loaded from {filename}.")
                return data
        else:
            print(f"File {filename} not found. Creating new file.")
            with open(filename, 'w') as f:
                json.dump({}, f)
            return {}
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}

def save_json(filename, data):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"Data saved to {filename}.")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

user_points = load_json(POINTS_FILE)
bet_history = load_json(BET_HISTORY_FILE)
loans = load_json(LOANS_FILE)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is now running!')

@bot.command(name='wordcloud')
async def wordcloud(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    user = str(member)

    try:
        all_messages = []
        async for message in ctx.channel.history(limit=10000):
            if message.author == member:
                all_messages.append(message.content)

        if not all_messages:
            await ctx.send(f"No messages found for {member.display_name}.")
            return

        text = " ".join(all_messages)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        file = discord.File(buf, filename='wordcloud.png')

        await ctx.send(file=file)
        buf.close()

    except Exception as e:
        await ctx.send("An error occurred while generating the word cloud.")
        print(f"Error in wordcloud command: {e}")

@bot.command(name='points')
async def points(ctx):
    try:
        user = str(ctx.author)
        points = user_points.get(user, BASE_POINTS)  # Default to BASE_POINTS if user is not in the system
        await ctx.send(f'{user}, you have {points} points.')
    except Exception as e:
        await ctx.send("An error occurred while retrieving your points.")
        print(f"Error in points command: {e}")

@bot.command(name='bet')
async def bet(ctx, amount: int, game: str, bet_type: str):
    try:
        user = str(ctx.author)
        user_points.setdefault(user, BASE_POINTS)  # Ensure user has an entry in the points dictionary

        if game in locked_games:
            await ctx.send(f'Bets are locked for the game {game}.')
            return

        if user_points[user] < amount:
            await ctx.send(f'You do not have enough points to place this bet.')
            return

        if bet_type.lower() not in ['win', 'lose']:
            await ctx.send(f'Invalid bet type. Please use "win" or "lose".')
            return

        # Deduct points and record the bet
        user_points[user] -= amount
        bet_record = {'user': user, 'amount': amount, 'game': game, 'type': bet_type.lower(), 'outcome': None, 'points_gained': 0}
        bets.append(bet_record)
        
        if user not in bet_history:
            bet_history[user] = []
        bet_history[user].append(bet_record)

        save_json(POINTS_FILE, user_points)
        save_json(BET_HISTORY_FILE, bet_history)

        await ctx.send(f'{user} has placed a bet of {amount} points on {game} to {bet_type}.')
    except Exception as e:
        await ctx.send("An error occurred while placing your bet.")
        print(f"Error in bet command: {e}")

@bot.command(name='loan')
async def loan(ctx, borrower: discord.Member, amount: int):
    try:
        lender = str(ctx.author)
        borrower = str(borrower)
        user_points.setdefault(lender, BASE_POINTS)  # Ensure lender has an entry in the points dictionary
        user_points.setdefault(borrower, BASE_POINTS)  # Ensure borrower has an entry in the points dictionary

        if user_points[lender] < amount:
            await ctx.send(f'{lender}, you do not have enough points to loan.')
            return

        # Deduct points from the lender and loan to the borrower
        user_points[lender] -= amount
        user_points[borrower] += amount
        loan_record = {'lender': lender, 'borrower': borrower, 'amount': amount, 'interest': amount * LOAN_INTEREST_RATE, 'repaid': False}
        loans.append(loan_record)

        save_json(POINTS_FILE, user_points)
        save_json(LOANS_FILE, loans)

        await ctx.send(f'{lender} has loaned {amount} points to {borrower} with {LOAN_INTEREST_RATE*100}% interest.')
    except Exception as e:
        await ctx.send("An error occurred while processing the loan.")
        print(f"Error in loan command: {e}")

@bot.command(name='resolve')
async def resolve(ctx, game: str, outcome: str):
    try:
        global bets
        total_bet_points = sum(bet['amount'] for bet in bets if bet['game'] == game)
        if outcome.lower() not in ['win', 'lose']:
            await ctx.send(f'Invalid outcome. Please use "win" or "lose".')
            return

        winners = [bet for bet in bets if bet['game'] == game and bet['type'] == outcome.lower()]
        losers = [bet for bet in bets if bet['game'] == game and bet['type'] != outcome.lower()]

        if not winners:
            await ctx.send(f'No winners for the game {game}.')
            return

        # Calculate odds
        total_winner_bet_points = sum(bet['amount'] for bet in winners)
        total_loser_bet_points = sum(bet['amount'] for bet in losers)
        odds = (total_loser_bet_points / total_winner_bet_points) if total_winner_bet_points > 0 else 1

        for winner_bet in winners:
            payout = int(winner_bet['amount'] * odds) + winner_bet['amount']
            user = winner_bet['user']
            
            # Apply loan garnishments
            user_points[user] += payout
            for loan in loans:
                if loan['borrower'] == user and not loan['repaid']:
                    garnish_amount = loan['amount'] + loan['interest']
                    if user_points[user] >= garnish_amount:
                        user_points[user] -= garnish_amount
                        user_points[loan['lender']] += garnish_amount
                        loan['repaid'] = True
                    else:
                        user_points[loan['lender']] += user_points[user]
                        loan['amount'] -= user_points[user] / (1 + LOAN_INTEREST_RATE)
                        user_points[user] = 0

            for record in bet_history[user]:
                if record['game'] == game and record['type'] == outcome.lower():
                    record['outcome'] = 'win'
                    record['points_gained'] = payout

        for loser_bet in losers:
            user = loser_bet['user']
            for record in bet_history[user]:
                if record['game'] == game and record['type'] != outcome.lower():
                    record['outcome'] = 'lose'
                    record['points_gained'] = -loser_bet['amount']

        # Remove resolved bets
        bets = [bet for bet in bets if bet['game'] != game]
        save_json(POINTS_FILE, user_points)
        save_json(BET_HISTORY_FILE, bet_history)
        save_json(LOANS_FILE, loans)

        await ctx.send(f'Game {game} resolved. Winners received payouts based on odds of {odds:.2f}.')
    except Exception as e:
        await ctx.send("An error occurred while resolving the game.")
        print(f"Error in resolve command: {e}")

@bot.command(name='lock_bets')
async def lock_bets(ctx, game: str):
    try:
        if game not in locked_games:
            locked_games.append(game)
            await ctx.send(f'Bets for the game {game} are now locked.')
        else:
            await ctx.send(f'Bets for the game {game} are already locked.')
    except Exception as e:
        await ctx.send("An error occurred while locking the bets.")
        print(f"Error in lock_bets command: {e}")

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

@bot.command(name='claim')
@commands.cooldown(1, CLAIM_COOLDOWN_PERIOD, commands.BucketType.user)
async def claim(ctx):
    try:
        user = str(ctx.author)
        user_points.setdefault(user, BASE_POINTS)
        if user_points[user] < CLAIM_POINTS:
            user_points[user] = CLAIM_POINTS
            save_json(POINTS_FILE, user_points)
            await ctx.send(f'{user}, your points have been reset to {CLAIM_POINTS}.')
        else:
            await ctx.send(f'{user}, you already have {user_points[user]} points, which is above the claim amount.')
    except CommandOnCooldown as e:
        await ctx.send(f'This command is on cooldown. Try again in {e.retry_after:.2f} seconds.')
    except Exception as e:
        await ctx.send("An error occurred while claiming points.")
        print(f"Error in claim command: {e}")

@bot.command(name='bet_history')
async def bet_history_command(ctx):
    try:
        user = str(ctx.author)
        if user in bet_history:
            history_message = f'{user}\'s bet history:\n'
            for bet in bet_history[user]:
                outcome = bet['outcome'] if bet['outcome'] else "pending"
                history_message += f"Game: {bet['game']}, Bet: {bet['amount']} points, Type: {bet['type']}, Outcome: {outcome}, Points Gained/Lost: {bet['points_gained']}\n"
            await ctx.send(history_message)
        else:
            await ctx.send(f'{user}, you have no bet history.')
    except Exception as e:
        await ctx.send("An error occurred while retrieving bet history.")
        print(f"Error in bet_history command: {e}")

@bot.command(name='current_bets')
async def current_bets(ctx):
    try:
        if bets:
            current_bets_message = "Current bets:\n"
            for bet in bets:
                current_bets_message += f"User: {bet['user']}, Game: {bet['game']}, Amount: {bet['amount']} points, Type: {bet['type']}\n"
            await ctx.send(current_bets_message)
        else:
            await ctx.send('There are no current bets.')
    except Exception as e:
        await ctx.send("An error occurred while retrieving current bets.")
        print(f"Error in current_bets command: {e}")

@bot.command(name='cancel_bet')
async def cancel_bet(ctx, game: str):
    try:
        user = str(ctx.author)
        user_bets = [bet for bet in bets if bet['user'] == user and bet['game'] == game]
        if user_bets:
            for bet in user_bets:
                user_points[user] += bet['amount']
                bets.remove(bet)
                bet_history[user].remove(bet)
            save_json(POINTS_FILE, user_points)
            save_json(BET_HISTORY_FILE, bet_history)
            await ctx.send(f'{user}, your bets on {game} have been cancelled and points refunded.')
        else:
            await ctx.send(f'{user}, you have no bets on {game} to cancel.')
    except Exception as e:
        await ctx.send("An error occurred while cancelling bets.")
        print(f"Error in cancel_bet command: {e}")

@bot.command(name='bet_help')
async def bet_help(ctx):
    try:
        help_message = (
            "Betting Bot Commands:\n"
            "!points - Check your points.\n"
            "!bet <amount> <game> <win/lose> - Place a bet on a game.\n"
            "!loan <@user> <amount> - Loan points to another user with interest.\n"
            "!resolve <game> <win/lose> - Resolve bets for a game (admin only).\n"
            "!lock_bets <game> - Lock bets for a game (admin only).\n"
            "!leaderboard - Show the leaderboard.\n"
            "!claim - Claim points if you have less than the claim amount.\n"
            "!bet_history - Show your bet history.\n"
            "!current_bets - Show all current bets.\n"
            "!cancel_bet <game> - Cancel your bet on a game and refund points.\n"
        )
        await ctx.send(help_message)
    except Exception as e:
        await ctx.send("An error occurred while displaying help.")
        print(f"Error in bet_help command: {e}")
        
@bot.command(name='leaderboard')
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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f'This command is on cooldown. Try again in {error.retry_after:.2f} seconds.')
    else:
        await ctx.send(f"An error occurred: {str(error)}")

# Ensure JSON files exist at startup
for file in [POINTS_FILE, BET_HISTORY_FILE, LOANS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

# Save user points and bet history regularly
@bot.event
async def on_disconnect():
    save_json(POINTS_FILE, user_points)
    save_json(BET_HISTORY_FILE, bet_history)
    save_json(LOANS_FILE, loans)

bot.run(TOKEN)