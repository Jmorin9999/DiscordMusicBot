import discord, asyncio, os, requests, json
from discord.ext import commands, tasks
from pytube import YouTube
from datetime import datetime, timedelta
 
class MusicBot(commands.Bot):
    def __init__(self, command_prefix, intents, token):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.token = token
        self.voice_client = None
        self.song_queue = []
        self.client = discord.Client(intents=intents)
        self.add_commands()
        self.BettingDataFile = "PointsFile.json"
        self.BettingData = self.LoadBettingData()

    def LoadBettingData(self):
        if not os.path.exists(self.BettingDataFile):
            with open(self.BettingDataFile, "w") as file:
                json.dump({"Players": {}, "CurrentBets": {}, "BettingLocked": False}, file)
        else:
            with open(self.BettingDataFile, "r") as file:
                return json.load(file)

    def SaveData(self,data):
        with open(self.BettingDataFile, "w") as file:
            json.dump(data, file, indent=4)

    def add_commands(self):
        @self.command()
        async def join(ctx):
            await self.join_voice_channel(ctx)

        @self.command()
        async def play(ctx, *, url: str):
            await self.add_to_queue_or_play(ctx, url)

        @self.command()
        async def queue(ctx):
            await self.show_queue(ctx)

        @self.command()
        async def clear(ctx):
            await self.clear_queue(ctx)

        @self.command()
        async def skip(ctx):
            await self.skip_song(ctx)

        @self.command()
        async def stop(ctx):
            await self.stop_music(ctx)

        @self.command()
        async def disconnect(ctx):
            await self.disconnect_voice(ctx)

        @self.command()
        async def stink(ctx):
            channelId = 1319490837868056597
            channel = bot.get_channel(channelId)
            if channel:
                await channel.send("Carson = stinky boi")
            else:
                await ctx.send("Channel not found!")

        @self.command()
        async def fent(ctx):
            channelId = 1319490837868056597
            channel = bot.get_channel(channelId)
            if channel:
                await channel.send("Fent reactors: online")
            else:
                await ctx.send("Channel not found!")

        @self.command()
        async def Commands(ctx):
            channelId = 1319490837868056597
            channel = bot.get_channel(channelId)
            if channel:
                FormattedMessage = "**Commands!!!**\n"
                FormattedMessage += (
                    f"**!!Commands** - Shows all the commands\n"
                    f"**!!StartDate** - Shows start of the leaderboard week\n"
                    f"**!!ResetDate** - Shows date that the leaderboard will be reset\n"
                    f"**!!KDR** - Shows all of the kdas for everyone\n"
                    f"**!!KPPG** - Shows the kill participation of everyone\n"
                    f"**!!Leaderboard** - Shows the leaderboard\n"
                    f"**!!StatCheck Name** - Shows that persons's stats\n"

                )
                await channel.send(FormattedMessage)
            else:
                await ctx.send("Channel not found!")

        @self.command()
        async def StartDate(ctx):
            channelId = 1319490837868056597
            channel = bot.get_channel(channelId)
            file = "/opt/league_bot/WeeklyStats.json"
            if channel:
                try:
                    with open(file, "r") as file:
                        FileData = json.load(file)

                        data = FileData["StartDate"]

                        await channel.send(f"Leaderboard stats started on:  {data}")
                except (FileNotFoundError, ValueError):
                    print("No file found")
            else:
                print("Channel not found!")

        @self.command()
        async def ResetDate(ctx):
            channelId = 1319490837868056597
            channel = bot.get_channel(channelId)
            file = "/opt/league_bot/WeeklyStats.json"
            if channel:
                try:
                    with open(file, "r") as file:
                        FileData = json.load(file)

                        data = FileData["ResetDate"]

                        await channel.send(f"Leaderboard stats reset on:  {data}")
                except (FileNotFoundError, ValueError):
                    print("No file found")
            else:
                print("Channel not found!")

        @self.command()
        async def Test(ctx):
            channelId = 1242124701837557931  # Betting channel ID
            channel = bot.get_channel(channelId)
            if channel:
                await channel.send(f"{ctx.author} used this command")
                print(ctx.author)  
            else:
                print("Something went wrong.")

        @self.command()
        async def BettingEnroll(ctx):
            channelId = 1242124701837557931  # Betting channel ID
            channel = bot.get_channel(channelId)

        @self.command()
        async def StatCheck(ctx, *,name: str):
            channelId = 1319490837868056597
            channel = bot.get_channel(channelId)
            file = "/opt/league_bot/WeeklyStats.json"  
            if channel:
                try:
                    with open(file, "r") as file:
                        FileData = json.load(file)
                        data = FileData["players"].get(name)

                        FormattedMessage = f"**{name}'s Stats**\n"

                        FormattedMessage +=(
                            f"- Games Played: **{data['games_played']}**\n"
                            f"- Kills: **{data['kills']}**\n"
                            f"- Assists: **{data['assists']}**\n"
                            f"- Deaths: **{data['deaths']}**\n"
                            f"- Total Damage Dealt to Champions: **{data['totalDamageDealtToChampions']:,}**\n"
                            f"- Enemy Missing Pings: **{data['enemyMissingPings']}**\n"
                            f"- Wards Placed: **{data['wardsPlaced']}**\n"
                            f"- Total Time Spent Dead: **{data['totalTimeSpentDead']:,}** seconds\n"
                            f"- Total Minions Killed: **{data['totalMinionsKilled']:,}** minions\n"
                            f"- Games Ended In Surrenders: **{data['gamesEndedInSurrender']}**\n"
                            f"- Average Kill Participation Per Game: **{data['AverageKillParticipationPerGame']}%**\n"
                            f"- Wins: **{data['wins']}**\n"
                            f"- Losses: **{data['losses']}**\n"
                            f"- Double Kills: **{data['doubleKills']}**\n"
                            f"- Triple Kills: **{data['tripleKills']}**\n"
                            f"- Quadra Kills: **{data['quadraKills']}**\n"
                            f"- KDR: **{data['KDA']}**\n"
                            f"- WLR: **{data['WLR']}**\n"
                            f"- I inted **{data['TimesInted']}** times!\n")

                        await channel.send(FormattedMessage)

                except (FileNotFoundError, ValueError):
                    print("No file found")
            else:
                print("Channel not found!")


        @self.command()
        async def KDR(ctx):
            channelId = 1319490837868056597
            channel = bot.get_channel(channelId)
            file = "/opt/league_bot/WeeklyStats.json"
            if channel:
                try:
                    with open(file, "r") as file:
                        FileData = json.load(file)

                        data = FileData["players"]
                        FormattedMessage = "**Current League KDRs - NO ARAMS**\n"

                        for player, stats in data.items():

                            FormattedMessage += f"- {player} -- **{stats['KDA']}**\n"

                        await channel.send(FormattedMessage)

                except (FileNotFoundError, ValueError):
                    print("No file found")
            else:
                print("Channel not found!")

        @self.command()
        async def KPPG(ctx):
            channelId = 1319490837868056597
            channel = bot.get_channel(channelId)
            file = "/opt/league_bot/WeeklyStats.json"
            if channel:
                try:
                    with open(file, "r") as file:
                        FileData = json.load(file)

                        data = FileData["players"]
                        FormattedMessage = "**Current Kill Participation Per Games - NO ARAMS**\n"

                        for player, stats in data.items():

                            FormattedMessage += f"- {player} -- **{stats['AverageKillParticipationPerGame']} %**\n"

                        await channel.send(FormattedMessage)

                except (FileNotFoundError, ValueError):
                    print("No file found")
            else:
                print("Channel not found!")

        @self.command()
        async def Leaderboard(ctx):
            ChannelID = 1319490837868056597  # Channel ID for the league leaderboard
            channel = bot.get_channel(ChannelID)
            file = "/opt/league_bot/WeeklyStats.json"
            Today = datetime.combine(datetime.today(), datetime.min.time())

            if channel:
                try:
                    with open(file, "r") as file:
                        FileData = json.load(file)
                        ResetDate = FileData["ResetDate"]
                        data = FileData["players"]

                        MostKills = {"player": None, "value": 0}
                        MostDeaths = {"player": None, "value": 0}
                        MostAssists = {"player": None, "value": 0}
                        MostDamage = {"player": None, "value": 0}
                        MostTimeSpentDead = {"player": None, "value": 0}
                        MostMinionsKilled = {"player": None, "value": 0}
                        MostWins = {"player": None, "value": 0}
                        MostLosses = {"player": None, "value": 0}
                        MostDoubleKills = {"player": None, "value": 0}
                        MostTripleKills = {"player": None, "value": 0}
                        MostQuadraKills = {"player": None, "value": 0}
                        HighestKDR = {"player": None, "value": 0}
                        HighestKPPG = {"player": None, "value": 0}

                        TiedHighestKDR = []
                        TiedHighestKPPG = []
                        TiedMostKills = []
                        TiedMostDeaths = []
                        TiedMostAssists = []
                        TiedMostDamage = []
                        TiedMostTimeSpentDead = []
                        TiedMostMinionsKilled = []
                        TiedMostWins = []
                        TiedMostLosses = []
                        TiedMostDoubleKills = []
                        TiedMostTripleKills = []
                        TiedMostQuadraKills = []

                        FormattedMessage = "**League Normal(Draft) Leaders - NO ARAMS**\n"
                        """
                        FormattedMessage += (
                            f"**{player}**\n"
                            f"- Games Played: {stats['games_played']}\n"
                            f"- Kills: {stats['kills']}\n"
                            f"- Assists: {stats['assists']}\n"
                            f"- Deaths: {stats['deaths']}\n"
                            f"- KDA: {stats['kills'] / stats['deaths']}\n"
                            f"- Total Damage Dealt to Champions: {stats['totalDamageDealtToChampions']}\n"
                            f"- Enemy Missing Pings: {stats['enemyMissingPings']}\n"
                            f"- Wards Placed: {stats['wardsPlace    d']}\n"
                            f"- Total Time Spent Dead: {stats['totalTimeSpentDead']} seconds\n"
                            f"- Games Ended In Surrenders: {stats['gamesEndedInSurrender']}\n\n"
                        )
                        """
                        for player, stats in data.items():

                            if stats["kills"] > MostKills["value"]:
                                MostKills = {"player": player, "value": stats["kills"]}
                                TiedMostKills = [player]
                            elif stats["kills"] == MostKills["value"]:
                                if player not in TiedMostKills:
                                    TiedMostKills.append(player)

                            if stats["deaths"] > MostDeaths["value"]:
                                MostDeaths = {"player": player, "value": stats["deaths"]}
                                TiedMostDeaths = [player]
                            elif stats["deaths"] == MostDeaths["value"]:
                                if player not in TiedMostDeaths:
                                    TiedMostDeaths.append(player)


                            if stats["assists"] > MostAssists["value"]:
                                MostAssists = {"player": player, "value": stats["assists"]}
                                TiedMostAssists = [player]
                            elif stats["assists"] == MostAssists["value"]:
                                if player not in TiedMostAssists:
                                    TiedMostAssists.append(player)


                            if stats["totalDamageDealtToChampions"] > MostDamage["value"]:
                                MostDamage = {"player": player, "value": stats["totalDamageDealtToChampions"]}
                                TiedMostDamage = [player]
                            elif stats["totalDamageDealtToChampions"] == MostDamage["value"]:
                                if player not in TiedMostDamage:
                                    TiedMostDamage.append(player)


                            if stats["totalTimeSpentDead"] > MostTimeSpentDead["value"]:
                                MostTimeSpentDead = {"player": player, "value": stats["totalTimeSpentDead"]}
                                TiedMostTimeSpentDead = [player]
                            elif stats["totalTimeSpentDead"] == MostTimeSpentDead["value"]:
                                if player not in TiedMostTimeSpentDead:
                                    TiedMostTimeSpentDead.append(player)

                            if stats["totalMinionsKilled"] > MostMinionsKilled["value"]:
                                MostMinionsKilled = {"player": player, "value": stats["totalMinionsKilled"]}
                                TiedMostMinionsKilled = [player]
                            elif stats["totalMinionsKilled"] == MostMinionsKilled["value"]:
                                if player not in TiedMostMinionsKilled:
                                    TiedMostMinionsKilled.append(player)

                            if stats["wins"] > MostWins["value"]:
                                MostWins = {"player": player, "value": stats["wins"]}
                                TiedMostWins = [player]  # Reset with the new top player
                            elif stats["wins"] == MostWins["value"]:
                                if player not in TiedMostWins:
                                    TiedMostWins.append(player)

                            if stats["losses"] > MostLosses["value"]:
                                MostLosses = {"player": player, "value": stats["losses"]}
                                TiedMostLosses = [player]  # Reset with the new top player
                            elif stats["losses"] == MostLosses["value"]:
                                if player not in TiedMostLosses:
                                    TiedMostLosses.append(player)

                            if stats["doubleKills"] > MostDoubleKills["value"]:
                                MostDoubleKills = {"player": player, "value": stats["doubleKills"]}
                                TiedMostDoubleKills = [player]  # Reset with the new top player
                            elif stats["doubleKills"] == MostDoubleKills["value"]:
                                if player not in TiedMostDoubleKills:
                                    TiedMostDoubleKills.append(player)

                            if stats["tripleKills"] > MostTripleKills["value"]:
                                MostTripleKills = {"player": player, "value": stats["tripleKills"]}
                                TiedMostTripleKills = [player]  # Reset with the new top player
                            elif stats["tripleKills"] == MostTripleKills["value"]:
                                if player not in TiedMostTripleKills:
                                    TiedMostTripleKills.append(player)

                            if stats["quadraKills"] > MostQuadraKills["value"]:
                                MostQuadraKills = {"player": player, "value": stats["quadraKills"]}
                                TiedMostQuadraKills = [player]  # Reset with the new top player
                            elif stats["quadraKills"] == MostQuadraKills["value"]:
                                if player not in TiedMostQuadraKills:
                                    TiedMostQuadraKills.append(player)    

                            if stats["KDA"] > HighestKDR["value"]:
                                HighestKDR = {"player": player, "value": stats["KDA"]}
                                TiedHighestKDR = [player]  # Reset with the new top player
                            elif stats["KDA"] == HighestKDR["value"]:
                                if player not in TiedHighestKDR:
                                    TiedHighestKDR.append(player)      

                            if stats["AverageKillParticipationPerGame"] > HighestKPPG["value"]:
                                HighestKPPG = {"player": player, "value": stats["AverageKillParticipationPerGame"]}
                                TiedHighestKPPG = [player]  # Reset with the new top player
                            elif stats["AverageKillParticipationPerGame"] == HighestKPPG["value"]:
                                if player not in TiedHighestKPPG:
                                    TiedHighestKPPG.append(player)

                        if len(TiedMostKills) <= 1:
                            FormattedMessage += f"- Most Kills this week: **{MostKills['player']}** with **{MostKills['value']}** kills \n"
                        else:
                            KillsTiedPlayers = ", ".join(TiedMostKills)
                            FormattedMessage += f"- Most Kills tied between: **{KillsTiedPlayers}** with **{MostKills['value']}** kills \n"


                        if len(TiedMostDeaths) <= 1:
                            FormattedMessage += f"- Most Deaths this week: **{MostDeaths['player']}** with **{MostDeaths['value']}** deaths\n"
                        else:
                            DeathsTiedPlayers = ", ".join(TiedMostDeaths)
                            FormattedMessage += f"- Most Deaths tied between: **{DeathsTiedPlayers}** with **{MostDeaths['value']}** deaths \n"


                        if len(TiedMostAssists) <= 1:
                            FormattedMessage += f"- Most Assists this week: **{MostAssists['player']}** with **{MostAssists['value']}** assists\n"
                        else:
                            AssistsTiedPlayers = ", ".join(TiedMostAssists)
                            FormattedMessage += f"- Most Assists tied between: **{AssistsTiedPlayers}** with **{MostDeaths['value']}** assists \n"


                        if len(TiedMostDamage) <= 1:
                            FormattedMessage += f"- Most Damage this week: **{MostDamage['player']}** with **{MostDamage['value']:,}** damage\n"
                        else:
                            DamageTiedPlayers = ", ".join(TiedMostDamage)
                            FormattedMessage += f"- Most Damage tied between: **{DamageTiedPlayers}** with **{MostDamage['value']:,}** damage \n"


                        if len(TiedMostTimeSpentDead) <= 1:
                            FormattedMessage += f"- Most Time Spent Dead this week: **{MostTimeSpentDead['player']}** with **{MostTimeSpentDead['value']:,}** seconds spent dead\n"
                        else:
                            TimeSpentDeadTiedPlayers = ", ".join(TiedMostTimeSpentDead)
                            FormattedMessage += f"- Most Time Spent Dead tied between: **{TimeSpentDeadTiedPlayers}** with **{MostTimeSpentDead['value']:,}** seconds spent dead \n"


                        if len(TiedMostMinionsKilled) <= 1:
                            FormattedMessage += f"- Most Minions Killed this week: **{MostMinionsKilled['player']}** with **{MostMinionsKilled['value']:,}** minions killed.\n"
                        else:
                            MinionsTiedPlayers = ", ".join(TiedMostMinionsKilled)
                            FormattedMessage += f"- Most Minions Killed tied between: **{MinionsTiedPlayers}** with **{MostMinionsKilled['value']:,}** minions killed.\n"

                        if len(TiedMostDoubleKills) <= 1:
                            FormattedMessage += f"- Most Double Kills this week: **{MostDoubleKills['player']}** with **{MostDoubleKills['value']}** double kills.\n"
                        else:
                            DoubleKillTiedPlayers = ", ".join(TiedMostDoubleKills)
                            FormattedMessage += f"- Most Double Kills tied between: **{DoubleKillTiedPlayers}** with **{MostDoubleKills['value']}** double kills.\n"


                        if len(TiedMostTripleKills) <= 1:
                            FormattedMessage += f"- Most Triple Kills this week: **{MostTripleKills['player']}** with **{MostTripleKills['value']}** triple kills.\n"
                        else:
                            TripleKillTiedPlayers = ", ".join(TiedMostTripleKills)
                            FormattedMessage += f"- Most Triple Kills tied between: **{TripleKillTiedPlayers}** with **{MostTripleKills['value']}** triple kills.\n"


                        if len(TiedMostQuadraKills) <= 1:
                            FormattedMessage += f"- Most Quadra Kills this week: **{MostQuadraKills['player']}** with **{MostQuadraKills['value']}** quadra kills.\n"
                        else:
                            QuadraKillsTiedPlayers = ", ".join(TiedMostQuadraKills)
                            FormattedMessage += f"- Most Quadra Kills tied between: **{QuadraKillsTiedPlayers}** with **{MostTripleKills['value']}** quadra kills.\n"



                        if len(TiedMostWins) <= 1 :
                            FormattedMessage += f"- Most Wins: **{MostWins['player']}** with **{MostWins['value']}** wins.\n"
                        else:
                            WinsTiedPlayers = ", ".join(TiedMostWins)
                            FormattedMessage += f"- Most Wins tied between: **{WinsTiedPlayers}** with **{MostWins['value']}** wins.\n"


                        if len(TiedMostLosses) <= 1:
                            FormattedMessage += f"- Most Losses: **{MostLosses['player']}** with **{MostLosses['value']}** losses.\n"
                        else:
                            LossesTiedPlayers = ", ".join(TiedMostLosses)
                            FormattedMessage += f"- Most Losses tied between: **{LossesTiedPlayers}** with **{MostLosses['value']}** losses.\n"

                        if len(TiedHighestKDR) <= 1:
                            FormattedMessage += f"- Highest KDR: **{HighestKDR['player']}** with **{HighestKDR['value']}**\n"
                        else:
                            KDRTiedPlayers = ", ".join(TiedHighestKDR)
                            FormattedMessage += f"- Highest KDR tied between: **{KDRTiedPlayers}** with **{HighestKDR['value']}**\n"     

                        if len(TiedHighestKPPG) <= 1:
                            FormattedMessage += f"- Highest Kill Participation: **{HighestKPPG['player']}** with **{HighestKPPG['value']}**%\n"
                        else:
                            KPPGTiedHighestPlayers = ", ".join(TiedHighestKPPG)
                            FormattedMessage += f"- Highest Kill Participation tied between: **{KPPGTiedHighestPlayers}** with **{HighestKPPG['value']}**%\n"


                        await channel.send(FormattedMessage)
                except (FileNotFoundError, ValueError):
                    print("No file found")
            else:
                print("Channel not found!")


    async def join_voice_channel(self, ctx):
        channel = ctx.author.voice.channel
        if channel:
            self.voice_client = await channel.connect()
            print(f"Joined voice channel: {channel.name}")
        else:
            await ctx.send("You are not in a voice channel.")

    async def add_to_queue_or_play(self, ctx, url):
        if self.voice_client and self.voice_client.is_playing():
            self.song_queue.append(url)
            yt = YouTube(url)
            await ctx.send(f"Added to queue: {yt.title}")
        else:
            await self.join_voice_channel(ctx)
            await self.play_music(ctx, url)

    async def play_music(self, ctx, url):
        try:
            yt = YouTube(url)
            stream = yt.streams.filter(only_audio=True).first()
            options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            self.voice_client.stop()
            self.voice_client.play(
                discord.FFmpegPCMAudio(stream.url, before_options=options), 
                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.loop)
            )
            print(f"Now playing: {yt.title}")
        except Exception as e:
            print(f"Error playing music: {e}")

    async def play_next(self, ctx):
        if self.song_queue:
            next_url = self.song_queue.pop(0)
            await self.play_music(ctx, next_url)

    async def show_queue(self, ctx):
        if self.song_queue:
            queue_message = "\n".join([f"{index + 1}. {url}" for index, url in enumerate(self.song_queue)])
            await ctx.send(f"Current Queue:\n{queue_message}")
        else:
            await ctx.send("The queue is empty.")

    async def clear_queue(self, ctx):
        self.song_queue.clear()
        await ctx.send("Queue cleared.")

    async def skip_song(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            await ctx.send("Skipping the current song.")
        else:
            await ctx.send("No song is currently playing.")

    async def stop_music(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            print("Music stopped.")
        else:
            print("No music is playing.")

    async def disconnect_voice(self, ctx):
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            print("Disconnected from voice channel.")

    def run_bot(self):
        self.run(self.token)

if __name__ == "__main__":
    with open("/opt/token", "r") as f:
        TOKEN = f.read().strip()
    intents = discord.Intents.all()
    bot = MusicBot(command_prefix="!!", intents=intents, token=TOKEN)
    bot.run_bot()

#jacob if this doesnt work im gonna KILL MYSELF
#test123!
