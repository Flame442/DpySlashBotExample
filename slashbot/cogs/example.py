import discord
from discord.ext import commands
from slashbot.core import slash


class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash.command()
    async def command(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        await ctx.send(f"Hi {member.mention}!")

    @slash.command()
    async def group_command(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        await ctx.send(f"{member.mention} loves group commands!")

def setup(bot):
    bot.add_cog(Example(bot))
