import discord
from discord.ext import commands
from bot.config import BASE_POINTS, CLAIM_POINTS, CLAIM_COOLDOWN_PERIOD, LOAN_INTEREST_RATE
from bot.utils.json_handler import save_json

# In-memory database for bets, loans, and locked games
bets = []
locked_games = [] 

def setup(bot, BASE_POINTS, CLAIM_POINTS, CLAIM_COOLDOWN_PERIOD, LOAN_INTEREST_RATE, user_points, bet_history, loans, POINTS_FILE, BET_HISTORY_FILE, LOANS_FILE):
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
