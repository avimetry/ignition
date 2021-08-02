"""
Command to get help for the bot.
Copyright (C) 2021 avizum

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import discord
import humanize
import datetime

from discord.ext import commands
from difflib import get_close_matches
from utils import AvimetryBot


class AvimetryHelp(commands.HelpCommand):
    async def get_bot_perms(self, command):
        permissions = getattr(command, 'bot_permissions', ["send_messages"])
        return ", ".join(permissions).replace("_", " ").replace("guild", "server").title()

    async def get_user_perms(self, command):
        permissions = getattr(command, 'user_permissions', ["send_messages"])
        return ", ".join(permissions).replace("_", " ").replace("guild", "server").title()

    async def can_run(self, command, ctx):
        try:
            await command.can_run(ctx)
            emoji = ctx.bot.emoji_dictionary["green_tick"]
        except commands.CommandError:
            emoji = ctx.bot.emoji_dictionary["red_tick"]
        return emoji

    def get_cooldown(self, command):
        try:
            rate = command._buckets._cooldown.rate
            cd_type = command._buckets._cooldown.type.name
            per = humanize.precisedelta(command._buckets._cooldown.per)
            time = "time"
            if rate > 1:
                time = "times"
            return f"{per} every {rate} {time} per {cd_type}"
        except Exception:
            return None

    def ending_note(self):
        return f"Use {self.clean_prefix}{self.invoked_with} [command|module] for help on a command or module."

    def command_signature(self):
        return (
            "```<> is a required argument\n"
            "[] is an optional argument\n"
            "[...] accepts multiple arguments```"
        )

    async def send_error_message(self, error):
        embed = discord.Embed(
            title="Help Error", description=error, color=discord.Color.red()
        )
        embed.set_footer(text=self.ending_note())
        await self.get_destination().send(embed=embed)

    def get_destination(self):
        return self.context

    async def send_bot_help(self, mapping):
        bot = self.context.bot
        total = len(bot.commands)
        usable = 0
        for command in bot.commands:
            try:
                await command.can_run(self.context)
                usable += 1
            except commands.CommandError:
                continue
        if await bot.is_owner(self.context.author):
            usable = total
        usable = f"Total Commands: {total} | Usable by you here: {usable}"
        info = [
            f"[Support Server]({self.context.bot.support})",
            f"[Invite]({self.context.bot.invite})",
            "[Vote](https://top.gg/bot/756257170521063444/vote)"
        ]
        embed = discord.Embed(
            title=f"{self.context.bot.user.name} Help",
            description=(
                f"{self.command_signature()}Do not use these when using commands.\n"
                f"{usable}\n"
                f"{' | '.join(info)}\n"
            )
        )
        modules_list = []
        for cog, command in mapping.items():
            name = "No Category" if cog is None else cog.qualified_name
            filtered = await self.filter_commands(command, sort=True)
            if filtered:
                modules_list.append(name)
            joiner = "\n"
        embed.add_field(
            name="Modules",
            value=f"{joiner.join(modules_list)}", inline=False
        )
        embed.set_footer(text=self.ending_note(), icon_url=str(self.context.author.avatar_url))
        embed.set_thumbnail(url=str(self.context.bot.user.avatar_url))
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"{cog.qualified_name.title()} module",
            description=cog.description or "Module description is not provided",
        )
        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        command_list = []
        for command in filtered:
            try:
                getattr(command, 'commands')
                command_list.append(f"{command.name}\u200b*")
            except AttributeError:
                command_list.append(command.name)
        if not command_list:
            return
        split_list = [command_list[item:item+4] for item in range(0, len(command_list), 4)]
        value = [", ".join(lists) for lists in split_list]
        embed.add_field(
            name=f"Commands in {cog.qualified_name.title()}",
            value=",\n".join(value) or "No commands.",
            inline=False,
        )
        embed.set_thumbnail(url=str(self.context.bot.user.avatar_url))
        embed.set_footer(text=self.ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=f"Command Group: {group.qualified_name.title()}",
            description=f"{group.short_doc}" or "Description was not provided")
        embed.add_field(
            name="Base command usage",
            value=f"`{self.clean_prefix}{group.qualified_name} {group.signature}`")
        if group.aliases:
            embed.add_field(
                name="Command Aliases",
                value=", ".join(group.aliases),
                inline=False)
        embed.add_field(
            name="Required Permissions",
            value=(
                f"Can Use: {await self.can_run(group, self.context)}\n"
                f"Bot Permissions: `{await self.get_bot_perms(group)}`\n"
                f"User Permissions: `{await self.get_user_perms(group)}`"
            ),
            inline=False)
        cooldown = self.get_cooldown(group)
        if cooldown:
            embed.add_field(
                name="Cooldown",
                value=cooldown)
        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            group_commands = []
            for command in filtered:
                try:
                    getattr(command, 'commands')
                    group_commands.append(f"{command.name}\u200b*")
                except AttributeError:
                    group_commands.append(command.name)
            split_list = [group_commands[i:i+4]for i in range(0, len(group_commands), 4)]
            value = [", ".join(lists) for lists in split_list]
            embed.add_field(
                name=f"Subcommands for {group.qualified_name}",
                value=",\n".join(value) or None,
                inline=False)
        embed.set_thumbnail(url=str(self.context.bot.user.avatar_url))
        embed.set_footer(text=self.ending_note())
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"Command: {command.qualified_name}")

        embed.add_field(
            name="Command Usage",
            value=f"`{self.clean_prefix}{command.qualified_name} {command.signature}`")
        if command.aliases:
            embed.add_field(
                name="Command Aliases",
                value=", ".join(command.aliases),
                inline=False)
        embed.add_field(
            name="Description",
            value=command.short_doc or "No help was provided.",
            inline=False)
        embed.add_field(
            name="Required Permissions",
            value=(
                f"Can Use: {await self.can_run(command, self.context)}\n"
                f"Bot Permissions: `{await self.get_bot_perms(command)}`\n"
                f"User Permissions: `{await self.get_user_perms(command)}`"),
            inline=False)
        cooldown = self.get_cooldown(command)
        if cooldown:
            embed.add_field(
                name="Cooldown",
                value=cooldown)
        embed.set_thumbnail(url=str(self.context.bot.user.avatar_url))
        embed.set_footer(text=self.ending_note())
        await self.get_destination().send(embed=embed)

    async def command_not_found(self, string):
        all_commands = []
        for cmd in self.context.bot.commands:
            try:
                await cmd.can_run(self.context)
                all_commands.append(cmd.name)
                if cmd.aliases:
                    all_commands.extend(cmd.aliases)
            except commands.CommandError:
                continue
        match = "\n".join(get_close_matches(string, all_commands))
        if match:
            return f'"{string}" is not a command or module. Did you mean...\n`{match}`'
        return f'"{string}" is not a command or module. I couln\'t find any similar commands.'

    async def subcommand_not_found(self, command, string):
        return f'"{string}" is not a subcommand of "{command}".'


class HelpCommand(commands.Cog):
    def __init__(self, bot: AvimetryBot):
        self.default = bot.help_command
        self.bot = bot
        self.load_time = datetime.datetime.now()
        self.bot.help_command = AvimetryHelp(
            verify_checks=False,
            show_hidden=False,
            command_attrs=dict(
                hidden=True,
                aliases=["halp", "helps", "hlp", "hlep", "hep"],
                brief="Why do you need help with the help command?",
                usage="[command|module]",
            )
        )

    def cog_unload(self):
        self.bot.help_command = self.default


def setup(bot):
    bot.add_cog(HelpCommand(bot))
