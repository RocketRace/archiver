import discord

from datetime    import datetime
from discord.ext import commands
from json        import dump
from os          import makedirs
from os.path     import isfile

# Sets up the scraper class
class Scraper(commands.Cog, name="Archiving:"):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def archive(self, ctx, channel: commands.TextChannelConverter(), limit: int = 100):
        '''
        Archives [limit] recent messages from the provided channel onto disk.
        '''
        async with ctx.typing():
            # Feedback for the user
            userMessage = f"Archiving {limit} messages from {channel.mention}..." \
                if bool(limit) else \
                f"Archiving all messages from {channel.mention}... This may take several minutes."
            await ctx.send(userMessage)
            await ctx.trigger_typing()

            # Limit of 0 -> no limit
            limit = limit if bool(limit) else None

            # Gets the guild information
            guild = None
            if ctx.guild:
                guild = ctx.guild
            else: # In a DM context
                guild = channel.guild
            
            # The current timestamp, to differentiate archives
            timestamp = datetime.utcnow().ctime()
            # A mostly unique name
            filename = hash(timestamp) % 1000000

            # The path to the archive folder
            path = f"archives/guilds/{guild.id}/{channel.id}"

            # Creates the folder to store any images, if it doesn't exist
            try:
                makedirs(f"{path}/data")
                makedirs("archives/users") # For avatars
            except OSError:
                pass

            # Goes through the channel history as specified by the limit.
            # By default, it goes through only the 100 most recent messages.
            history = []
            async for message in channel.history(limit=limit, oldest_first=False):

                ### === ATTACHMENTS ===

                # Attachment identifiers
                attachmentNames = [f"{a.id}_{a.filename}" for a in message.attachments]        

                # Saves the message attachments to disk
                for name, attachment in zip(attachmentNames, message.attachments):
                    await attachment.save(f"{path}/data/{name}")

                ### === AVATAR ===

                # Determines whether or not to save an animated avatar
                # Currently animated avatars are not supported.
                avatarFormat = "webp" 
                # avatarFormat = "gif" if message.author.is_avatar_animated() else "webp"
                
                # Avatar identifier
                avatarName = f"{message.author.id}.{avatarFormat}"

                # Saves the author's current avatar to disk if it does not exist yet
                if not isfile(f"archives/users/{avatarName}"):
                    await message.author.avatar_url_as(format=avatarFormat)\
                        .save(f"archives/users/{avatarName}")

                ### === EMBEDS ===

                # Copies the message embed data as-is
                embeds = [e.to_dict() for e in message.embeds if e.type == "rich"]

                ### === REACTIONS ===

                # Gets the message reactions
                allReactions = message.reactions
                unicodeReactions = [r.emoji for r in allReactions if not r.custom_emoji]

                ### === MESSAGE ===

                #  Stores the message information necessary for a backup
                copy = {
                    "attachments" : attachmentNames,
                    "author"      : {
                        "avatar"  : avatarName,
                        "id"      : message.author.id,
                        "nick"    : message.author.display_name
                    },
                    "content"     : message.system_content,
                    "created_at"  : message.created_at.isoformat(),
                    "embeds"      : embeds,
                    "reactions"   : unicodeReactions,
                    "type"        : message.type[0]
                }
                
                # Stores the message
                history.append(copy)
            
            # Reverses the history (to oldest first)
            history.reverse()

            # User feedback
            note = f" (Only found {len(history)})" if len(history) < limit else ""
            await ctx.send(f"Scraped {len(history)} messages from {channel.mention}{note}.")

            # Compresses the message history
            history = await self.bot.get_cog("Compressor").compress(ctx, history)

            # Stores the channel metadata
            metadata = {
                "channel" : {
                    "name"           : channel.name,
                    "nsfw"           : channel.is_nsfw(),
                    "slowmode_delay" : channel.slowmode_delay,
                    "topic"          : channel.topic
                },
                "size"      : len(history),
                "timestamp" : timestamp
            }

            # Creates and saves the archive metadata file
            with open(f"{path}/metadata_{filename}.json", "x") as metadataFile:
                dump(metadata, metadataFile, indent=2)

            # Creates and saves the archive file
            filename = hash(timestamp) % 1000000
            with open(f"{path}/{filename}.json", "x") as archiveFile:
                dump(history, archiveFile, indent=2)

        # Cleans up the prefix from <@id> to @name
        cleanPrefix = ctx.prefix
        cleanPrefix = f"@{self.bot.user.name} " if ctx.prefix == self.bot.user.mention + " " else cleanPrefix
        
        # Final user message
        formatted = f"{ctx.author.mention} Done. Archive saved with ID `{filename}`.\n" + \
            f"To clone this archive to another channel, run `{cleanPrefix}clone {filename} [channel]`.\n" + \
            f"To list other archived channels, run `{cleanPrefix}list`."
        await ctx.send(formatted)


# Imports the cog to the bot
def setup(bot):
    bot.add_cog(Scraper(bot))