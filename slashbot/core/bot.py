import discord
from discord.ext import commands
from slashbot.core import slash
import asyncio
import logging


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
        self.logger = logging.getLogger("slashbot")

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
                for alias in item.aliases:
                    self.slash_commands[alias] = item
        
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
            await interaction.response.send_message(content="Commands cannot be used in DMs.")
            return
        
        ctx = slash.SlashContext(self, interaction)
        args, path = slash.prepare_args(interaction)
        ctx.path = path
        if path not in self.slash_commands:
            await interaction.response.send_message(content="That command is not available right now. Try again later.", ephemeral=True)
            return
        
        command = self.slash_commands[path]
        await ctx._interaction.response.defer()
        try:
            await command.callback(command.cog, ctx, *args)
        except Exception as e:
            await ctx.send("`The command encountered an error. Try again in a moment.`")
            self.logger.exception(f"Error in command {ctx.path}")
