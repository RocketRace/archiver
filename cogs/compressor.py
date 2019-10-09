import discord

from discord.ext import commands

# Sets up the compressor utility class
class Compressor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Compresses a file provided to take up as few messages as possible.
    async def compress(self, ctx, archive):
        # Goes through the messages once 
        temporaryMessage = archive[0] # The first message
        compressedArchive = [] 
        for message in archive[1:]: # The other messages
            # If consecutive messages are by the same author
            if temporaryMessage["author"]["id"] == message["author"]["id"]:
                # We can't merge two messages if the first has attachments, embeds or reactions
                # This is false when all fields are empty lists: []
                canNotCombine = any([
                    temporaryMessage["attachments"],
                    temporaryMessage["embeds"],
                    temporaryMessage["reactions"]
                ])
                # We can't merge two messages if the total character count of the contents exceeds 2000
                mergedContent = temporaryMessage["content"] + "\n" + message["content"]
                messageTooLong = len(mergedContent) > 2000

                # In any of these cases, the temporary message is what we will clone.
                if canNotCombine or messageTooLong:
                    compressedArchive.append(temporaryMessage)
                    temporaryMessage = message
                
                # Otherwise, merge the messages
                else:
                    # Override embeds, attachments, reactions
                    temporaryMessage = message 
                    # Override content
                    temporaryMessage["content"] = mergedContent
            
            # If the author does not match, clone the temporary message as-is
            else:
                compressedArchive.append(temporaryMessage)
                temporaryMessage = message
        
        # The last message
        compressedArchive.append(temporaryMessage)
        
        # Return compression efficiency
        compressionRatio = 100 - round(100 * len(compressedArchive) / len(archive))
        formatted = f"Compressed archive from {len(archive)} to {len(compressedArchive)} messages" + \
                    f" ({compressionRatio}% compression rate)."

        await ctx.send(formatted)
        # Return our compressed archive
        return compressedArchive

# Imports the cog to the bot
def setup(bot):
    bot.add_cog(Compressor(bot))