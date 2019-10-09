import discord

from discord.ext import commands

# Sets up the utility class
class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def invite(self, ctx):
        '''
        Generates an invite link for the bot
        '''
        # Read, write and manage messages
        # Manage channels, webhooks
        # Add files, embeds, reactions
        permissions = discord.Permissions(537128048)
        link = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
        await ctx.send(f"<{link}>")

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        '''
        Logs the bot out
        '''
        await self.bot.logout()

    @commands.command(name="list")
    @commands.is_owner()
    async def _list(self, ctx):
        '''
        Lists existing channel archives.
        '''
        


# Imports the cog to the bot
def setup(bot):
    bot.add_cog(Utils(bot))