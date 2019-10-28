import discord
import logging
import traceback

from datetime    import datetime
from discord.ext import commands
from json        import load
from sys         import stderr

# Sets up the bot
prefixes = None
token = None
with open("config.json") as configFile:
    config = load(configFile)
    prefixes = config["prefixes"]
    token = config["token"]

helpCommand=commands.MinimalHelpCommand(no_category="Other:")
bot = commands.Bot(command_prefix=prefixes, help_command=helpCommand)

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
    logger.warning(errorTitle)

    # Prints the error message as well
    traceback.print_exception(type(error), error, error.__traceback__, file=stderr)

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
modules = ("cogs.scraper", "cogs.cloner", "cogs.compressor", "cogs.utils", "cogs.batch")
if __name__ == "__main__":
    for module in modules:
        bot.load_extension(module)

# Starts the event loop
bot.run(token, reconnect=True, bot=True)