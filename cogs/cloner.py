import discord

from collections import OrderedDict
from datetime    import datetime
from discord.ext import commands
from json        import load
from os          import listdir
from os.path     import isfile

# Sets up the cloner class
class Cloner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Takes an archived channel by id and copies its contents to an existing channel.
    @commands.is_owner()
    @commands.command()
    async def clone(self, ctx, path, *, channel: commands.TextChannelConverter()):
        # Searches through archived channels for the provided archive
        sourcePath = None
        for guild in listdir("archives/guilds"):
            for sourceChannel in listdir(f"archives/guilds/{guild}"):
                if isfile(f"archives/guilds/{guild}/{sourceChannel}/{path}"):
                    sourcePath = f"archives/guilds/{guild}/{sourceChannel}"
        
        # If not found
        if sourcePath is None:
            return await ctx.send("Could not find an archive with that filename.")

        # User feedback
        await ctx.send("Working... This may take a few minutes.")
        await ctx.trigger_typing()

        # Opens the channel archive
        archive = None
        with open(f"{sourcePath}/{path}") as archiveFile:
            archive = load(archiveFile)
        
        # Prepares the channel for cloning:
        # Wipes the channel
        await channel.purge(limit=100) # Only purges 100 messages, since we likely don't need more.
        
        # Opens the channel metadata file
        metadata = None
        with open(f"{sourcePath}/metadata_{path}") as metadataFile:
            metadata = load(metadataFile)
        
        # Updates the channel with the metadata
        await channel.edit(**metadata)

        # Up to 10 unique webhooks may exist in a channel at once. 
        # We will use all 10 slots to minimize API calls.
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            await webhook.delete()
        webhooks = OrderedDict() # To maintain order

        # Determines what the webhook name should be for messages of a given type.
        # False => Use the provided user display name.
        messageTypes = {
            "call"                       : False,
            "channel_icon_change"        : False,
            "channel_name_change"        : False,
            "default"                    : False,
            "new_member"                 : "Join Message",
            "pins_add"                   : "Pinned Message",
            "premium_guild_subscription" : "Server Boost",
            "premium_guild_tier_1"       : "Server Boost",
            "premium_guild_tier_2"       : "Server Boost",
            "premium_guild_tier_3"       : "Server Boost",
            "recepent_add"               : False,
            "recepient_remove"           : False
        }

        # Clones each message in the archive
        counter = 0
        for message in archive:
            
            # Checks if the author already has a webhook representation
            authorID = message["author"]["id"]
            webhook = webhooks.get(authorID)
            if webhook is None:

                # If there are already 10 webhooks, replace the first
                if len(webhooks) == 10:
                    webhooks.popitem(last=False) # Pops the first entry

                # Determines the webhook name
                name = messageTypes[message["type"]]
                if name is False:
                    name = message["author"]["nick"]
                
                # Gets the user avatar
                avatarPath = message["author"]["avatar"]
                avatarFile = open(f"archives/users/{avatarPath}", "rb").read()

                # If the webhook doesn't exist, create one
                webhook = await channel.create_webhook(name=name, avatar=avatarFile)
                webhooks[authorID] = webhook
            
            # Gets message embeds
            embedDicts = message["embeds"]
            # Clones all rich embeds
            embeds = [discord.Embed.from_dict(e) for e in embedDicts if e["type"] == "rich"]

            # Gets message attachments
            attachmentPaths = message["attachments"]
            attachmentFiles = [discord.File(f"{sourcePath}/data/{fp}") for fp in attachmentPaths]

            # Gets message content
            content = message["content"]

            # Sends the message to the channel
            await webhook.send(content=content, embeds=embeds, files=attachmentFiles)
            counter += 1
        
        await ctx.send(f"{ctx.author.mention} Done. Created {counter} messages in {channel.mention}.")


                







# Imports the cog to the bot
def setup(bot):
    bot.add_cog(Cloner(bot))