import discord
from discord.ext import commands
from bot.utils.json_handler import save_json
from bot.config import BASE_POINTS, CLAIM_POINTS, CLAIM_COOLDOWN_PERIOD, LOAN_INTEREST_RATE

def setup(bot, user_points, POINTS_FILE):
    @bot.command(name='points')
    async def points(ctx):
        user = str(ctx.author)
        points = user_points.get(user, BASE_POINTS)
        await ctx.send(f'{user}, you have {points} points.')

    @bot.command(name='loan')
    async def loan(ctx, borrower: discord.Member, amount: int):
        lender = str(ctx.author)
        borrower = str(borrower)
        user_points.setdefault(lender, BASE_POINTS)
        user_points.setdefault(borrower, BASE_POINTS)

        if user_points[lender] < amount:
            await ctx.send('You do not have enough points to loan.')
            return

        user_points[lender] -= amount
        user_points[borrower] += amount
        loan_record = {'lender': lender, 'borrower': borrower, 'amount': amount, 'interest': amount * LOAN_INTEREST_RATE, 'repaid': False}
        loans.append(loan_record)

        save_json(POINTS_FILE, user_points)

        await ctx.send(f'{lender} has loaned {amount} points to {borrower} with {LOAN_INTEREST_RATE*100}% interest.')

    @bot.command(name='claim')
    @commands.cooldown(1, CLAIM_COOLDOWN_PERIOD, commands.BucketType.user)
    async def claim(ctx):
        user = str(ctx.author)
        user_points.setdefault(user, BASE_POINTS)
        if user_points[user] < CLAIM_POINTS:
            user_points[user] = CLAIM_POINTS
            save_json(POINTS_FILE, user_points)
            await ctx.send(f'{user}, your points have been reset to {CLAIM_POINTS}.')
        else:
            await ctx.send(f'{user}, you already have {user_points[user]} points, which is above the claim amount.')
    
    @bot.command(name='leaderboard')
    async def leaderboard(ctx):
        try:
            sorted_points = sorted(user_points.items(), key=lambda x: x[1], reverse=True)
            leaderboard_message = 'Leaderboard:\n'
            for user, points in sorted_points:
                leaderboard_message += f'{user}: {points} points\n'
            await ctx.send(leaderboard_message)
        except Exception as e:
            await ctx.send("An error occurred while retrieving the leaderboard.")
            print(f"Error in leaderboard command: {e}")
