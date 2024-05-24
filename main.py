import os
import logging
from discord.ext import commands
from dotenv import load_dotenv
from utils.json_handler import load_json, save_json
from commands import betting, music, user_management, fun

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup logging
logging.basicConfig(level=logging.INFO)

# Bot setup
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Load data files
POINTS_FILE = 'user_points.json'
BET_HISTORY_FILE = 'bet_history.json'
LOANS_FILE = 'loans.json'

user_points = load_json(POINTS_FILE)
bet_history = load_json(BET_HISTORY_FILE)
loans = load_json(LOANS_FILE)

# Register commands
betting.setup(bot, user_points, bet_history, loans, POINTS_FILE, BET_HISTORY_FILE, LOANS_FILE)
music.setup(bot)
user_management.setup(bot, user_points, POINTS_FILE)
fun.setup(bot)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is now running!')

@bot.event
async def on_disconnect():
    save_json(POINTS_FILE, user_points)
    save_json(BET_HISTORY_FILE, bet_history)
    save_json(LOANS_FILE, loans)

bot.run(TOKEN)
