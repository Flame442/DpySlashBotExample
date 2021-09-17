import discord
from discord.ext import commands


class Dev(commands.Cog):
    """Dev non-slash commands for testing."""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def load(self, ctx, name):
        try:
            self.bot.load_extension(f"slashbot.cogs.{name}")
        except Exception as e:
            await ctx.send(f"Failed to load `{name}`.")
            raise e
        await ctx.send(f"Loaded `{name}`.")
    
    @commands.command()
    async def reload(self, ctx, name):
        try:
            self.bot.unload_extension(f"slashbot.cogs.{name}")
        except Exception:
            pass
        try:
            self.bot.load_extension(f"slashbot.cogs.{name}")
        except Exception as e:
            await ctx.send(f"Failed to reload `{name}`.")
            raise e
        await ctx.send(f"Reloaded `{name}`.")
    
    @commands.command()
    async def unload(self, ctx, name):
        try:
            self.bot.unload_extension(f"slashbot.cogs.{name}")
        except Exception as e:
            await ctx.send(f"Failed to unload `{name}`.")
            raise e
        await ctx.send(f"Unloaded `{name}`.")
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.command()
    async def console(self, ctx):
        [print('') for x in range(50)]
        print('\033[0;37;40m\nDone!')
        await ctx.send('Done.')


def setup(bot):
    bot.add_cog(Dev(bot))
