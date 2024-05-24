import discord
from discord.ext import commands
import asyncio
from bot.config import BASE_POINTS, CLAIM_POINTS, CLAIM_COOLDOWN_PERIOD, LOAN_INTEREST_RATE
from bot.utils.json_handler import save_json

# Global variables
roll_games = {}  # Dictionary to store roll game data
roll_timers = {}  # Dictionary to store roll game timers (to cancel if needed)

def setup(bot, BASE_POINTS, user_points, POINTS_FILE):
    @bot.command(name='roll')
    async def roll(ctx, amount: int):
        try:
            user = str(ctx.author)
            user_points.setdefault(user, BASE_POINTS)

            if amount <= 0:
                await ctx.send('Please enter a valid amount to gamble.')
                return

            if user_points[user] < amount:
                await ctx.send(f'You do not have enough points to gamble {amount} points.')
                return

            channel_id = ctx.channel.id
            if channel_id not in roll_games:
                roll_games[channel_id] = []
                roll_timers[channel_id] = asyncio.create_task(start_roll_game_after_delay(ctx, channel_id))

            roll_games[channel_id].append({'user': user, 'amount': amount})
            await ctx.send(f'{user} has joined the roll game with {amount} points. The game will start in 30 seconds.')

        except Exception as e:
            await ctx.send("An error occurred while joining the roll game.")
            print(f"Error in roll command: {e}")

    async def start_roll_game_after_delay(ctx, channel_id):
        await asyncio.sleep(30)
        if len(roll_games[channel_id]) < 2:
            await ctx.send('Not enough players to start the roll game. At least 2 players are required.')
            roll_games[channel_id] = []
            return

        rolls = []
        for player in roll_games[channel_id]:
            roll_result = random.randint(1, 100)
            rolls.append({'user': player['user'], 'amount': player['amount'], 'roll': roll_result})

        rolls = sorted(rolls, key=lambda x: x['roll'])
        lowest_roll = rolls[0]
        lost_amount = lowest_roll['amount']

        user_rolls_message = "Roll results:\n"
        for roll in rolls:
            user_rolls_message += f"{roll['user']}: {roll['roll']}\n"

        user_points[lowest_roll['user']] -= lost_amount

        remaining_players = rolls[1:]
        for winner in remaining_players:
            user_points[winner['user']] += lost_amount // len(remaining_players)

        await ctx.send(f"{user_rolls_message}\n{lowest_roll['user']} rolled the lowest ({lowest_roll['roll']}) and lost {lost_amount} points. The points were distributed among the other players.")

        # Clear the roll game data for this channel
        roll_games[channel_id] = []
        save_json(POINTS_FILE, user_points)