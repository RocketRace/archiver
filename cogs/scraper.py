import discord

from datetime    import datetime
from discord.ext import commands
from json        import dump
from os          import makedirs
from os.path     import isfile

# Sets up the scraper class
class Scraper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Archives `limit` recent messages from the provided channel onto disk.
    @commands.is_owner()
    @commands.command()
    async def archive(self, ctx, limit: int = 100, *, channel: commands.TextChannelConverter()):
        # Feedback for the user
        userMessage = "Working..." if bool(limit) else "Working... This may take several minutes."
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
        timestamp = datetime.utcnow().isoformat()

        # The path to the archive folder
        path = f"archives/guilds/{guild.id}/{channel.id}"

        # Creates the folder to store any images, if it doesn't exist
        try:
            makedirs(f"{path}/data")
            makedirs("archives/users") # For avatars
        except OSError:
            pass

        # Stores the channel metadata
        metadata = {
            "name"           : channel.name,
            "nsfw"           : channel.is_nsfw(),
            "slowmode_delay" : channel.slowmode_delay,
            "topic"          : channel.topic
        }

        # Creates and saves the archive metadata file
        with open(f"{path}/metadata_{timestamp}.json", "x") as metadataFile:
            dump(metadata, metadataFile, indent=2)

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
            embeds = [e.to_dict() for e in message.embeds]

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
        await ctx.send(f"Scraped {len(history)} messages from {channel.mention}.")

        # Compresses the message history
        history = await self.bot.get_cog("Compressor").compress(ctx, history)

        # Creates and saves the archive file
        with open(f"{path}/{timestamp}.json", "x") as archiveFile:
            dump(history, archiveFile, indent=2)

        await ctx.send(f"{ctx.author.mention} Done. File stored in `{path}` as `{timestamp}.json`.")


# Imports the cog to the bot
def setup(bot):
    bot.add_cog(Scraper(bot))