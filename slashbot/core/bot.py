import discord
from discord.ext import commands
from slashbot.core import slash
import asyncio


class SlashBot(commands.AutoShardedBot):
    def __init__(self):
        print("Starting...")
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="ff-",
            case_insensitive=False,
            guild_subscriptions=True,
            max_messages=500,
            intents=intents,
            heartbeat_timeout=120,
            guild_ready_timeout=10,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
        )
        self.token = "your_token_here"
        self.slash_commands = {}

    async def on_ready(self):
        print("Ready!")

    async def start(self):
        self.load_extension("slashbot.cogs.dev")
        await super().start(self.token)

    def add_cog(self, cog, *, override=False):
        super().add_cog(cog, override=override)
        for item in cog.__dir__():
            item = getattr(cog, item, None)
            if isinstance(item, slash.SlashCommand):
                item.cog = cog
                self.slash_commands[item.path] = item
        
    def remove_cog(self, name):
        removed_cog = super().remove_cog(name)
        if removed_cog is None:
            return None
        for item in removed_cog.__dir__():
            item = getattr(removed_cog, item, None)
            if isinstance(item, slash.SlashCommand) and item.path in self.slash_commands:
                del self.slash_commands[item.path]
        return removed_cog
    
    async def on_interaction(self, interaction):
        # Filter out non-slash command interactions
        if interaction.type != discord.InteractionType.application_command:
            return
        # Only accept interactions that occurred in a guild
        if not interaction.guild:
            return
        
        ctx = slash.SlashContext(interaction)
        args, path = slash.prepare_args(interaction)
        ctx.path = path
        if path in self.slash_commands:
            command = self.slash_commands[path]
            task = asyncio.create_task(command.callback(command.cog, ctx, *args))
            # If 2s pass and there is no message sent yet, defer so the interaction doesn't fail
            await asyncio.sleep(2)
            async with ctx._lock:
                if not ctx._interaction.response._responded:
                    await ctx._interaction.response.defer()
            try:
                await task
            except Exception as e:
                # If we defered but the command errored, resolve it so it doesn't think forever
                if ctx._defered:
                    await ctx.send("The command encountered an error. Try again in a moment.")
                raise e
        else:
            await ctx.send("That command is not available right now. Try again later.")
