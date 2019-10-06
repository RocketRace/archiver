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
    @commands.command()
    async def archive(self, ctx, limit: int = 100, *, channel: commands.TextChannelConverter()):
        # Feedback for the user
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
            avatarFormat = "gif" if message.author.is_avatar_animated() else "webp"
            
            # Avatar identifier
            avatarName = f"{message.author.id}.{avatarFormat}"

            # Saves the author's current avatar to disk if it does not exist yet
            if not isfile(f"archives/users/{avatarName}"):
                await message.author.avatar_url.save(f"archives/users/{avatarName}")

            ### === EMBEDS ===

            # Copies the message embed data as-is
            embeds = [e.to_dict() for e in message.embeds]

            ### === MESSAGE ===

            #  Stores the message information necessary for a backup
            copy = {
                "attachments" : attachmentNames,
                "author"      : {
                    "avatar"  : avatarName,
                    "nick"    : message.author.display_name
                },
                "content"     : message.system_content,
                "created_at"  : message.created_at.isoformat(),
                "embeds"      : embeds,
                "type"        : message.type
            }
            
            # Stores the message
            history.append(copy)
        
        # Reverses the history (to oldest first)
        history.reverse()

        # Creates and saves the archive file
        with open(f"{path}/{timestamp}.json", "x") as archiveFile:
            dump(history, archiveFile, indent=2)

        await ctx.send("Done.")


# Imports the cog to the bot
def setup(bot):
    bot.add_cog(Scraper(bot))