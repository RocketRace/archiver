import discord

from asyncio     import sleep
from collections import Counter
from discord.ext import commands
from json        import load
from os          import listdir
from os.path     import isfile
from time        import time

# Sets up the cloner class
class Cloner(commands.Cog, name="Cloning:"):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def clone(self, ctx, ID, *, channel: commands.TextChannelConverter()):
        '''
        Takes an archived channel and copies its contents to another channel.
        Emulates an authentic channel using webhooks. Due to Discord ratelimiting, this may take several minutes.

        __Parameters__
        <ID> The ID of the archive to clone.
        <channel> A channel name, id or mention. The channel to clone the archive into. 
        '''
        async with ctx.typing():
            # Searches through archived channels for the provided archive
            sourcePath = None
            for guild in listdir("archives/guilds"):
                for sourceChannel in listdir(f"archives/guilds/{guild}"):
                    if isfile(f"archives/guilds/{guild}/{sourceChannel}/{ID}.json"):
                        sourcePath = f"archives/guilds/{guild}/{sourceChannel}"
            
            # If not found
            if sourcePath is None:
                return await ctx.send("Could not find an archive with that filename.")

            # Opens the channel archive
            archive = None
            with open(f"{sourcePath}/{ID}.json") as archiveFile:
                archive = load(archiveFile)

            # Messages in the archive
            messageCount = len(archive)
            # How many sets of 30 messages we are sending 
            # Since the channel message ratelimit bucket is 30 per minute, this is 
            # equal to how long the clone operation will take.
            batches = messageCount // 30 + 1
            
            # User feedback
            formatted = f"Cloning {messageCount} messages to {channel.mention}. " + \
                f"This will take roughly {batches} minutes."
            await ctx.send(formatted)
            # This message will be edited as we progress
            progressMessage = await ctx.send(f"Processing batch 1 of {batches}...")
            
            # Prepares the channel for cloning:
            
            # Opens the channel metadata file
            metadata = None
            with open(f"{sourcePath}/metadata_{ID}.json") as metadataFile:
                metadata = load(metadataFile)
            
            # Tweaks the channel name
            metadata["channel"]["name"] = metadata["channel"]["name"] + "-clone"
            
            # Updates the channel with the provided metadata
            await channel.edit(**metadata["channel"])

            # Up to 10 unique webhooks may exist in a channel at once. 
            # We will use all 10 slots to minimize webhook editing API calls.
            webhooks = await channel.webhooks()
            for webhook in webhooks:
                await webhook.delete()
            webhooks = {}
            webhookUsage = Counter()

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
            messagesProcessed = 0
            batchesProcessed = 0
            t = time()
            for message in archive:
                
                # Checks if the author already has a webhook representation
                authorID = message["author"]["id"]
                webhook = webhooks.get(authorID)
                if webhook is None:

                    # Determines the webhook name
                    name = messageTypes[message["type"]]
                    if name is False:
                        name = message["author"]["nick"]

                    # Gets the user avatar
                    avatarPath = message["author"]["avatar"]
                    avatarFile = open(f"archives/users/{avatarPath}", "rb").read()

                    # If there are already 10 webhooks, replace the first
                    if len(webhooks) >= 10:
                        # Gets the key of the least used webhook
                        leastUsed = min(webhookUsage.items(), key=lambda x: x[1])[0] 
                        # Pops the old webhook
                        webhookUsage.pop(leastUsed)
                        webhook = webhooks.pop(leastUsed)
                        # Edits that webhook, and updates the dicts
                        await webhook.edit(name=name, avatar=avatarFile)
                        webhooks[authorID] = webhook
                        
                    else:
                        # If there are less than 10 webhooks, create more
                        webhook = await channel.create_webhook(name=name, avatar=avatarFile)
                        webhooks[authorID] = webhook

                # Increment the counter for the current author
                webhookUsage[authorID] += 1
                
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
                output = await webhook.send(content=content, embeds=embeds, files=attachmentFiles, wait=True)

                # Adds the correct reactions to the message
                for emoji in message["reactions"]:
                    await output.add_reaction(emoji)

                # For our cooldown
                if messagesProcessed % 30 == 0:
                    t = time()

                # Increment the processed message counter
                messagesProcessed += 1

                # A batch is 30 messages
                batchesProcessed = messagesProcessed // 30

                # Hard-coded channel ratelimit because discord keeps kicking us
                if messagesProcessed % 30 == 0: 
                    # Seconds since the start of the batch
                    deltaTime = int(time() - t) 
                    # If we're not done yet
                    if batchesProcessed < batches:
                        # Update the user progress message
                        await progressMessage.edit(content=f"Processing batch {batchesProcessed + 1} of {batches}...")
                        # Fulfill the cooldown
                        await sleep(60 - deltaTime) # asyncio.sleep

            # User output message
            await ctx.send(f"{ctx.author.mention} Done. Created {messageCount} messages in {channel.mention}.")

# Imports the cog to the bot
def setup(bot):
    bot.add_cog(Cloner(bot))