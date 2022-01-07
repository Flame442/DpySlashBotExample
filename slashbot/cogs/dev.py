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

    @commands.command(name="setup")
    async def setup_command(self, ctx, confirm=False):
        if not confirm:
            await ctx.send(
                "Are you sure you want to register the example slash commands in this guild? "
                "Do not do this if they are already registered.\n"
                f"Run `{ctx.prefix}setup yes` to confirm."
            )
            return
        payload = {
            "name": "command",
            "type": 1,
            "description": "Example slash command",
            "options": [
                {
                    "name": "member",
                    "description": "A discord member",
                    "type": 6,
                    "required": False,
                },
            ]
        }
        await self.bot.http.upsert_guild_command(self.bot.user.id, ctx.guild.id, payload)
        payload = {
            "name": "group",
            "type": 1,
            "description": "Example slash group command",
            "options": [
                {
                    "name": "command",
                    "description": "Example slash group command",
                    "type": 1,
                    "options": [
                        {
                            "name": "member",
                            "description": "A discord member",
                            "type": 6,
                            "required": False,
                        },
                    ]
                },
            ]
        }
        await self.bot.http.upsert_guild_command(self.bot.user.id, ctx.guild.id, payload)

def setup(bot):
    bot.add_cog(Dev(bot))
