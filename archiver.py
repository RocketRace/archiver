import discord
import logging

from datetime    import datetime
from discord.ext import commands
from json        import load

# Sets up the bot
prefixes = None
token = None
with open("config.json") as configFile:
    config = load(configFile)
    prefixes = config["prefixes"]
    token = config["token"]

bot = commands.Bot(command_prefix=prefixes, help_command=None)

# Sets up logging of verbosity INFO into a file named "log.txt"
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="log.txt", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# Sets up error logging
@bot.event
async def on_command_error(ctx, error):
    # Get the original error, if it exists
    error = getattr(error, "original", error)
    
    # Formats the error message
    errorTitle = f"An exception occurred while processing '{ctx.invoked_with}': "
    errorMessage = f"{type(error)}: {error}"

    # Logs the error
    logger = logging.getLogger("discord")
    logger.warning(errorTitle + errorMessage)

    # Ignore these errors when sending error messages to the user
    ignored = (commands.CommandNotFound,)
    if isinstance(error, ignored):
        return

    # Prepares the error message embed
    embed = discord.Embed(
        type        = "rich", 
        color       = 0xff0000,
        title       = errorTitle,
        description = errorMessage,
        timestamp   = datetime.utcnow()
    )

    # Propagates the error message to the user
    await ctx.send(" ", embed=embed)

# Loads the bot's modules
modules = ("cogs.scraper", "cogs.cloner")
if __name__ == "__main__":
    for module in modules:
        bot.load_extension(module)

# For convenience: Generates an invite link for the bot
@bot.command()
@commands.is_owner()
async def invite(ctx):
    link = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(537128048))
    await ctx.send(f"<{link}>")

@bot.command()
@commands.is_owner()
async def logout(ctx):
    await bot.logout()

# Starts the event loop
bot.run(token)