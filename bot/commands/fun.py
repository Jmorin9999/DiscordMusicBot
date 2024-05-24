import discord
from discord.ext import commands

def setup(bot):
    @bot.command(name='Stink')
    async def stink(ctx):
        stink_message = "Carson Stinks!  EW!!"
        await ctx.send(stink_message)
    
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
            await ctx.send(f"An error occurred while generating the word cloud: {str(e)}")
    
    # Other fun commands can be added here
