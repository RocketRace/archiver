import asyncio
import discord

from discord.ext import commands
from os          import listdir
from os.path     import isfile

# Sets up the batch utility class
class Batch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.is_owner()
    async def batch(self, ctx):
        '''
        Base command for batch operations.
        '''
    
    @batch.command()
    @commands.is_owner()
    async def archive(self, ctx, limit: int, channels: commands.Greedy[commands.TextChannelConverter()]):
        '''
        Archives multiple channels onto disk.
        '''
        # Creates a coroutine for each channel archival process
        coroutines = []
        for channel in channels:
            coroutine = self.bot.get_cog("Archiving:").store(ctx, channel, limit)
            coroutines.append(coroutine)
            
        IDs = await asyncio.gather(*coroutines)
        
        await ctx.send(f"{ctx.author.mention} Done. Created archives:\n{IDs}")

    @batch.command()
    @commands.is_owner()
    async def clone(self, ctx, category: commands.CategoryChannelConverter(), *IDs):
        '''
        Clones multiple archives into a channel category.
        '''

        # Prepares the channels 
        channels = []
        for ID in IDs:
            channel = await category.create_text_channel(ID)
            channels.append(channel)

        # Creates a coroutine for each cloning process
        coroutines = []
        for ID,channel in zip(IDs, channels):
            # Searches through archived channels for the provided archive
            sourcePath = None
            for guild in listdir("archives/guilds"):
                for sourceChannel in listdir(f"archives/guilds/{guild}"):
                    if isfile(f"archives/guilds/{guild}/{sourceChannel}/{ID}.json"):
                        sourcePath = f"archives/guilds/{guild}/{sourceChannel}"
            
            # Schedules to fill the new channels
            coroutines.append(self.bot.get_cog("Cloning:").fill(ctx, sourcePath, ID, channel))
        
        output = await asyncio.gather(*coroutines)
        
        await ctx.send(f"{ctx.author.mention} Done. Created messages:\n{output}")

            

        



        
    

# Imports the cog to the bot
def setup(bot):
    bot.add_cog(Batch(bot))