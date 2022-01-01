# DpySlashBotExample
An example of using discordpy 2.0.0a to create a bot that supports slash commands. This is not a fully complete bot, just an example of a kind of structure and syntax that can be used to keep discord.ext.commands-like syntax while still supporting slash commands. This approach comes with many limitations, but it is relatively easy to integrate into an existing bot.

## Requirements
- Python 3.8
- discordpy 2.0.0a
- A discord bot that has been added to a server

## Instructions
1. Download and extract the repo.
2. Edit `slashbot/core/bot` and replace `"your_token_here"` with your bot's token. Change the text command prefix if you would like to now.
3. Run the bot with `python -m slashbot`.
4. Once "Ready" appears in console, you should be able to use the text commands to interact with the bot. Run `ff-load example` to load the example cog.
5. Run `ff-setup` to register the slash commands in your server.
6. Assuming the example cog is loaded, and you have registered the slash commands, you should now be able to run `/command ` and `/group command`.

## Explanation
This bot overrides the `add_cog`, `remove_cog`, and `on_interaction` methods of `commands.AutoShardedBot` in order to integrate slash commands in a non-intrusive way. When a cog is loaded, slash commands are searched for similar to how text commands are searched for, and are added to a dictionary stored in the bot class. When a cog is unloaded, any slash commands are removed from this dictionary. When a command interaction happens, the bot searches for a registered slash command with the same "path". If one is found, the function is executed, with arguments prepared from the raw data given by the interaction. If one is not found, a simple error message is sent.

`slashbot/core/slash.py` does most of the heavy lifting. `SlashContext` is intended to be a drop in replacement for the context normally returned by a command. It does not contain *everything* that context normally does, partially because I chose not to add everything, and partially because everything is not able to be obtained. The `send` method is defined to use the followup webhook as long as that is still valid, then it swaps to using `channel.send()`. Note that this method could cause errors if the bot does not have `send_message` permissions in the channel. `prepare_args` and `recursive_options` are internal functions which take in an interaction and output that interaction's path and formatted arguments. Slash commands cannot have more than 1 optional arg as this system does not currently differentiate args outside of the order they are received from the API, however it is possible to modify this method to support that. If your bot has the members intent, it may be a good idea to replace the `SlashMember` mock class with a call to `guild.get_member`.

`slashbot/core/example.py` is an example slash cog. It appears very similar to a normal cog, with a few key differences. `@commands.command()` is replaced with `@slash.command()`, using the decorator provided by `slashbot/core/slash.py`. This prepares slash commands to be found by the bot when the cog is loaded. Slash command function names follow a syntax of command_subcommand, however the optional `path=("command", subcommand)` argument can be provided to the decorator to override the default name handling. Currently existing checks cannot be used with slash commands, although it may be possible to modify the `SlashCommand` class to support them. Cog methods such as `cog_check`, `before_invoke`, etc will not be run on slash commands.

## Registering Commands
This code **will not** register slash commands dynamically, though it is possible to modify `add_cog` to do so. If you want to register a command (other than the example commands), you will need to do so semi-manually. A slash command payload must be created, see [the discord api docs](https://discord.com/developers/docs/interactions/application-commands) for an explanation on how to create one. Once you have a payload, you can run the following code to register a command:
```py
payload = {
    "name": "command",
    "type": 1,
    "description": "An example command payload.",
}
# For a guild-specific command
await bot.http.upsert_guild_command(bot.user.id, guild.id, payload)
# For a global command
await bot.http.upsert_global_command(bot.user.id, payload)
```

## Integration into your bot
Be sure to respect the license of this code if you integrate any or all of it into your bot. If you want to integrate a similar system into your bot, you will probably need to do the following things:
1. Add the `add_cog`, `remove_cog`, and `on_interaction` overrides to your bot class.
2. Add `slash.py` to your bot.
3. Replace all instances of `@commands.command()` with `@slash.command()`.
4. Manually register all of the commands you require.
5. Deal with any and all issues that arise as a result of incompatibilities with this system.

## Support/Contact
I will not be providing support for this code, nor any attempts to integrate this code into your bot. This repo is purely for demonstration of one system that can be used to create a bot which supports slash commands using only discordpy 2.0.0a.
