import discord

from discord.ext import commands
from itertools   import islice, takewhile, repeat
from json        import load
from os          import listdir

# Sets up the utility class
class Utils(commands.Cog, name="Utilities:"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def invite(self, ctx):
        '''
        Generates an invite link for the bot.
        '''
        # Read, write and manage messages
        # Manage channels, webhooks
        # Add files, embeds, reactions
        permissions = discord.Permissions(537128048)
        link = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
        await ctx.send(f"<{link}>")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def logout(self, ctx):
        '''
        Logs the bot out and cancels any ongoing commands.
        '''
        await self.bot.logout()

    @commands.command(name="list")
    @commands.is_owner()
    async def _list(self, ctx):
        '''
        Lists existing channel archives.
        '''
        # Stores archive entries
        archives = ["Stored archives:"] # Prefix
      
        # Each guild directory
        guilds = listdir("archives/guilds")
        for guildID in guilds:
            
            # Gets the guild object from its ID
            guild = self.bot.get_guild(int(guildID))
            guildName = guildID + " (ID)" if guild is None else guild.name
            
            # Each channel directory
            channels = listdir(f"archives/guilds/{guildID}")
            for channelID in channels:
            
                # Gets the channel object from its ID
                channel = guild.get_channel(int(channelID))
                channelName = channelID + " (ID)" if channel is None else channel.name
            
                # Each file, given it's not metadata and is not the data directory
                files = listdir(f"archives/guilds/{guildID}/{channelID}") 
                for fp in files:
                    
                    # Fills the file structure
                    if not fp.startswith("metadata_") and not fp == "data":
                        # Strips the '.json' suffix
                        archiveName = fp[:-5]

                        # Opens the archive metadata
                        metadata = None
                        with open(f"archives/guilds/{guildID}/{channelID}/metadata_{fp}") as metadataFile:
                            metadata = load(metadataFile)
                        
                        # Gets relevant metadata
                        size = metadata["size"]
                        timestamp = metadata["timestamp"]

                        # Appends an archive entry
                        formatted = "".join([
                            f"Guild: `{guildName}`, ",
                            f"Channel: `{channelName}`, ", 
                            f"Archive ID: `{archiveName}`, ",
                            f"Archived: `{timestamp}`, ",
                            f"Size: `{size}` messages"
                        ])
                        archives.append(formatted)
        
        # Cleans up the prefix from <@id> to @name
        cleanPrefix = ctx.prefix
        cleanPrefix = f"@{self.bot.user.name} " if ctx.prefix == self.bot.user.mention + " " else cleanPrefix

        # Appends a message after the last entry
        suffix = f"To clone an archive to a channel, run `{cleanPrefix}clone [archive ID] [target channel]`."
        archives.append(suffix) 

        # Join the entries together in groups of 10
        def splitEvery(n, iterable):
            iterator = iter(iterable)
            return takewhile(bool, (list(islice(iterator, n)) for _ in repeat(None)))
        archivePartitions = splitEvery(10, archives)

        # Sends each group
        for partition in archivePartitions:
            formatted = "\n".join(partition)
            await ctx.send(formatted)



# Imports the cog to the bot
def setup(bot):
    bot.add_cog(Utils(bot))