import discord
from discord.ext import commands
from bot.utils.json_handler import save_json

def setup(bot, BASE_POINTS, user_points, bet_history, loans, POINTS_FILE, BET_HISTORY_FILE, LOANS_FILE):
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

    @bot.command(name='cancel_bet')
    async def cancel_bet(ctx, game: str):
        try:
            user = str(ctx.author)
            if game in bets and any(bet['user'] == user for bet in bets[game]):
                user_bets = [bet for bet in bets[game] if bet['user'] == user]
                for bet in user_bets:
                    user_points[user] += bet['amount']
                    bets[game].remove(bet)
                bet_history[user] = [bet for bet in bet_history[user] if bet['game'] != game]
                save_json(POINTS_FILE, user_points)
                save_json(BET_HISTORY_FILE, bet_history)
                await ctx.send(f'{user}, your bet in {game} has been canceled.')
            else:
                await ctx.send(f'{user}, you have no bet in {game} to cancel.')
        except Exception as e:
            await ctx.send("An error occurred while canceling your bet.")
            print(f"Error in cancel_bet command: {e}")
    
    @bot.command(name='bet_help')
    async def bet_help(ctx):
        help_message = (
            "Welcome to the betting commands!\n\n"
            "Commands available:\n"
            "!bet <game> <amount> <win/lose> - Place a bet on a game\n"
            "!cancel_bet <game> - Cancel your bet for a specific game and get your points back\n"
            "!bet_help - Display this help message\n"
            "!leaderboard - Display the current leaderboard\n"
            "!claim - Claim your daily points\n"
            "!roll <amount> - Join a roll game with the specified amount\n"
        )
        await ctx.send(help_message)
