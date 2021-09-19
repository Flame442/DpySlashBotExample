import discord
import asyncio
from enum import Enum


class SlashOptions(Enum):
    """Stores the option values for slash commands."""
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4 # any integer between -2^53 and 2^53
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7 # any channel type / category
    ROLE = 8
    MENTIONABLE = 9 # users and roles
    NUMBER = 10 # any float between -2^53 and 2^53


class SlashMessage():
    def __init__(self, bot, interaction):
        self.bot = bot
        self.interaction = interaction
    
    def edit(self, **kwargs):
        return self.interaction.edit_original_message(**kwargs)


class SlashContext():
    """Drop in `ctx` replacement for a slash interactions."""
    def __init__(self, interaction):
        self._interaction = interaction
        self.author = interaction.user
        self.message = interaction.message
        self.guild = interaction.guild
        self.channel = interaction.channel
        self.path = None # to be set by on_interaction
        self._defered = False # to be set by on_interaction
        self._lock = asyncio.Lock()
    
    def send(self, content=None, **kwargs):
        """Sends a message using the appropriate method in the given context."""
        if "content" in kwargs:
            content = kwargs["content"]
        # If we haven't responded to the interaction, this will send the message as an interaction response.
        # Otherwise, it will send it normally to the channel the command was sent in.
        async with self._lock:
            if self._interaction.response._responded:
                # If the command handler defered this message, we need to edit the message, not send a new one.
                if self._defered:
                    self._defered = False
                    await self._interaction.edit_original_message(content=content, **kwargs)
                    return SlashMessage(self.bot, self._interaction)
                # We already sent a response to the interaction, just send a new message to the channel.
                return await self.channel.send(content, **kwargs)
            # We need to respond to the interaction, send this message as that response.
            await self._interaction.response.send_message(content=content, **kwargs)
            return SlashMessage(self.bot, self._interaction)


class SlashMember():
    """A `discord.Member` equivalent that has only the data provided by slash commands."""
    def __init__(self, guild, id, username, discriminator, nick, permissions):
        self.guild = guild
        self.id = id
        self.name = username
        self.discriminator = discriminator
        self.nick = nick
        self.display_name = nick or username
        self.guild_permissions = permissions
        self.mention = f"<@{id}>"
    
    def __str__(self):
        return self.name + "#" + self.discriminator


class SlashCommand():
    """A command object for a slash command."""
    def __init__(self, func, path):
        self.path = path
        self.callback = func
        self.cog = None # to be set in add_cog


def command(path=None):
    """
    A decorator that can be added to async functions to make them slash commands.
    
        from core import slash
      
        @slash.command()
        async def mycommand(self, ctx):
            pass
        
        @slash.command()
        async def group_command(self, ctx):
            pass
        
        @slash.command(path=("ping",))
        async def pingcommand(self, ctx):
            pass
    
    The `path` parameter can be used to denote the command path to use,
    if not provided it defaults to
    `command_subcommand_subcommand` -> `("command", "subcommand", "subcommand")`
    """
    def wrapper(func):
        # Without this line, `path` is not properly defined. Thanks python.
        nonlocal path
        if path is None:
            path = tuple(func.__name__.split("_"))
        return SlashCommand(func, path)
    return wrapper

def prepare_args(interaction):
    """Resolves the raw argument data provided into objects."""
    path = [interaction.data["name"]]
    # There are no args or subcommands
    if "options" not in interaction.data:
        return [], tuple(path)
    return recursive_options(
        interaction.data["options"],
        {} if "resolved" not in interaction.data else interaction.data["resolved"],
        path,
        interaction.guild,
    )

def recursive_options(options: list, resolved: dict, path: list, guild):
    args = []
    for option in options:
        option_type = SlashOptions(option["type"])
        if option_type in (SlashOptions.SUB_COMMAND, SlashOptions.SUB_COMMAND_GROUP):
            path.append(option["name"])
            if "options" in option:
                return recursive_options(option["options"], resolved, path, guild)
        elif option_type == SlashOptions.STRING:
            args.append(option["value"].strip())
        elif option_type == SlashOptions.INTEGER:
            args.append(int(option["value"]))
        elif option_type == SlashOptions.BOOLEAN:
            args.append(bool(option["value"]))
        elif option_type == SlashOptions.USER:
            user_data = resolved["users"][option["value"]]
            mem_data = resolved["members"][option["value"]]
            mem = SlashMember(
                guild,
                int(user_data["id"]),
                user_data["username"],
                user_data["discriminator"],
                mem_data["nick"],
                discord.Permissions(int(mem_data["permissions"])),
            )
            args.append(mem)
        elif option_type == SlashOptions.CHANNEL:
            args.append(guild.get_channel(int(option["value"])))
        elif option_type == SlashOptions.ROLE:
            args.append(guild.get_role(int(option["value"])))
        elif option_type == SlashOptions.MENTIONABLE:
            raise NotImplementedError()
        elif option_type == SlashOptions.NUMBER:
            args.append(float(option["value"]))
    return args, tuple(path)
