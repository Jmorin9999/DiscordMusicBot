import discord
from discord.ext import commands
from bot.utils.json_handler import save_json

def setup(bot, user_points, bet_history, loans, POINTS_FILE, BET_HISTORY_FILE, LOANS_FILE):
    @bot.command(name='bet')
    async def bet(ctx, amount: int, game: str, bet_type: str):
        user = str(ctx.author)
        user_points.setdefault(user, BASE_POINTS)

        if user_points[user] < amount:
            await ctx.send('You do not have enough points to place this bet.')
            return

        if bet_type.lower() not in ['win', 'lose']:
            await ctx.send('Invalid bet type. Please use "win" or "lose".')
            return

        user_points[user] -= amount
        bet_record = {'user': user, 'amount': amount, 'game': game, 'type': bet_type.lower(), 'outcome': None, 'points_gained': 0}
        bets.append(bet_record)

        if user not in bet_history:
            bet_history[user] = []
        bet_history[user].append(bet_record)

        save_json(POINTS_FILE, user_points)
        save_json(BET_HISTORY_FILE, bet_history)

        await ctx.send(f'{user} has placed a bet of {amount} points on {game} to {bet_type}.')

    # Other betting commands can be added here in a similar manner
