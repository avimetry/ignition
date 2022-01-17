"""
Subclassed Command context
Copyright (C) 2021 - present avizum

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

import asyncio
import discord
import datetime
import re
import typing

from .avimetry import AvimetryBot
from .gist import GistClient, GistFile
from .view import AvimetryView
from discord.ext import commands, menus
from datetime import timedelta

emoji_regex = "<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>"


class TrashView(AvimetryView):
    def __init__(self, *, member: discord.Member, timeout: int = 60, ctx):
        self.ctx = ctx
        super().__init__(member=member, timeout=timeout)

    async def stop(self):
        for button in self.children:
            button.disabled = True
        await self.message.edit(view=self)
        super().stop()

    async def on_timeout(self):
        await self.stop()

    @discord.ui.button(emoji="\U0001f5d1", style=discord.ButtonStyle.danger)
    async def trash(self, button, interaction):
        await self.message.delete()
        await self.ctx.message.add_reaction(self.ctx.bot.emoji_dictionary["green_tick"])


class ConfirmView(AvimetryView):
    def __init__(self, *, member: discord.Member, timeout=None):
        super().__init__(member=member, timeout=timeout)
        self.value = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, button, interaction):
        self.value = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, button, interaction):
        self.value = False
        self.stop()


class ConfirmResult:
    def __init__(self, message: discord.Message, result: bool):
        self.message = message
        self.result = result

    def __repr__(self):
        return f"<ConfirmResult result={self.result}>"


class AutoPageSource(menus.ListPageSource):
    def __init__(self, entry: typing.Union[str, list], lang=None, *, limit: int = 1000):
        if isinstance(entry, list):
            entries = entry
        elif isinstance(entry, str):
            if lang:
                entries = [
                    f"```{lang}\n{entry[i:i+limit]}```"
                    for i in range(0, len(entry), limit)
                ]
            else:
                entries = [entry[i : i + limit] for i in range(0, len(entry), limit)]
        elif isinstance(entry, commands.Paginator):
            entries = entry.pages
        super().__init__(entries, per_page=1)

    async def format_page(self, menu, page):
        return page


class AvimetryContext(commands.Context):
    def __init__(self, *, bot: AvimetryBot, **kwargs):
        super().__init__(bot=bot, **kwargs)
        self.tokens = []
        self.tokens.extend(self.bot.settings["bot_tokens"].values())
        self.tokens.extend(self.bot.settings["api_tokens"].values())
        self.tokens.extend(self.bot.settings["webhooks"].values())

    @property
    def cache(self):
        return self.bot.cache

    @property
    def pool(self):
        return self.bot.pool

    @property
    def clean_prefix(self):
        match = re.match(emoji_regex, self.prefix)
        if match:
            return re.sub(emoji_regex, match.group(2), self.prefix)

        return re.sub(
            f"<@!?{self.bot.user.id}>", f"@{self.me.display_name} ", self.prefix
        )

    @property
    def content(self):
        return self.message.content

    @property
    async def get_prefix(self):
        get_prefix = await self.cache.get_guild_settings(self.guild.id)
        if get_prefix:
            prefix = get_prefix["prefixes"]
        if not prefix:
            return "`a.`"
        return f"`{'` | `'.join(prefix)}`"

    @property
    def reference(self):
        ref = self.message.reference
        if isinstance(ref.resolved, discord.Message):
            return ref.resolved
        return None

    async def no_reply(self, *args, **kwargs):
        return await super().send(*args, **kwargs)

    async def post(self, content, syntax: str = "py", gist: bool = False):
        if gist:
            gist_client = GistClient(
                self.bot.settings["api_tokens"]["GitHub"], self.bot.session
            )
            gist_file = [GistFile(filename=f"output.{syntax}", content=content)]
            link = await gist_client.post(
                description=str(self.author), files=gist_file, public=True, raw=False
            )
        else:
            link = await self.bot.myst.post(content, syntax=syntax)
        embed = discord.Embed(
            description=f"Output for {self.command.qualified_name}: [Here]({link})"
        )
        await self.send(embed=embed)

    async def determine_color(self, member: discord.Member = None):
        member = member or self.author
        base = member.color
        data = self.cache.users.get(member.id)
        try:
            color = data.get("color")
            if not color:
                color = base
        except AttributeError:
            color = base
        if color == discord.Color(0):
            if await self.bot.is_owner(member):
                color = discord.Color(0x01B9C0)
            else:
                color = discord.Color(0x2F3136)
        return color

    async def paginate(
        self,
        entry: typing.Union[str, list[discord.Embed]],
        lang: str = None,
        *,
        limit: int = 1000,
        delete_message_after: bool = True,
        remove_view_after: bool = False,
        disable_view_after: bool = False,
    ):
        from .paginators import AvimetryPages

        menu = AvimetryPages(
            AutoPageSource(entry, lang, limit=limit),
            ctx=self,
            remove_view_after=remove_view_after,
            delete_message_after=delete_message_after,
            disable_view_after=disable_view_after,
        )
        await menu.start()

    async def send(
        self,
        content: str = None,
        *,
        tts: bool = None,
        embed: discord.Embed = None,
        embeds: list[discord.Embed] = None,
        file: discord.File = None,
        files: list[discord.File] = None,
        stickers: typing.Sequence[discord.GuildSticker | discord.StickerItem] = None,
        delete_after: float = None,
        nonce: str | int = None,
        allowed_mentions: discord.AllowedMentions = None,
        reference: discord.MessageReference = None,
        mention_author: bool = None,
        view: discord.ui.View = None,
        paginate: bool = None,
        post: bool = None,
        no_reply: bool = None,
        no_edit: bool = None,
        return_message: bool = None,
        ephemeral: bool = None,
    ) -> discord.Message:
        if content:
            con = str(content)
            for token in self.tokens:
                content = con.replace(token, "[configuration token omitted]")
            if len(content) >= 2000:
                if paginate:
                    return await self.paginate(content, remove_view_after=True)
                if post:
                    return await self.post(content, gist=True)
        if embed:
            if not embed.footer:
                embed.set_footer(
                    text=f"Requested by: {self.author}",
                    icon_url=self.author.display_avatar.url,
                )
                embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
            if not embed.color:
                embed.color = await self.determine_color()
        if self._typing_task is not None:
            self._typing_task.cancel()
            self._typing_task = None

        if self.interaction is None or (
            self.interaction.response.responded_at is not None
            and discord.utils.utcnow() - self.interaction.response.responded_at
            >= timedelta(minutes=15)
        ):
            if (
                self.message.id in self.bot.command_cache
                and self.message.edited_at
                and not no_edit
            ):
                message = await self.bot.command_cache[self.message.id].edit(
                    content,
                    embed=embed,
                    delete_after=delete_after,
                    allowed_mentions=allowed_mentions,
                    view=view,
                )
            else:
                try:
                    reference = None if no_reply else self.message
                    message = await super().send(
                        content,
                        tts=tts,
                        embed=embed,
                        embeds=embeds,
                        file=file,
                        files=files,
                        stickers=stickers,
                        delete_after=delete_after,
                        nonce=nonce,
                        allowed_mentions=allowed_mentions,
                        reference=reference,
                        mention_author=mention_author,
                        view=view,
                    )
                except Exception as e:
                    print(e)
                    message = await super().send(
                        content,
                        tts=tts,
                        embed=embed,
                        embeds=embeds,
                        file=file,
                        files=files,
                        stickers=stickers,
                        delete_after=delete_after,
                        nonce=nonce,
                        allowed_mentions=allowed_mentions,
                        reference=reference,
                        mention_author=mention_author,
                        view=view,
                    )
            self.bot.command_cache[self.message.id] = message
            return message

        if not (
            return_message
            or self.interaction.response.is_done()
            # or any(arg in kwargs for arg in ("file", "files", "allowed_mentions"))
        ):
            send = self.interaction.response.send_message
        else:
            # We have to defer in order to use the followup webhook
            if not self.interaction.response.is_done():
                await self.interaction.response.defer(ephemeral=ephemeral)

            send = self.interaction.followup.send

        return await send(
            content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            delete_after=delete_after,
            allowed_mentions=allowed_mentions,
            view=view,
        )  # type: ignore

    def codeblock(self, content: str, language: str = "py"):
        return f"```{language}\n{content}\n```"

    async def confirm(
        self,
        message=None,
        embed: discord.Embed = None,
        confirm_message=None,
        *,
        timeout=60,
        delete_after=False,
        no_reply=False,
        remove_view_after=True,
    ):
        if delete_after:
            remove_view_after = False
        view = ConfirmView(member=self.author, timeout=timeout)
        check_message = (
            confirm_message or 'Press "yes" to accept, or press "no" to deny.'
        )
        if no_reply is True:
            send = await self.no_reply(content=message, embed=embed, view=view)
        elif message:
            message = f"{message}\n\n{check_message}"
            send = await self.send(message, view=view)
        elif embed:
            embed.description = f"{embed.description}\n\n{check_message}"
            send = await self.send(embed=embed, view=view)
        view.message = send
        await view.wait()
        if delete_after:
            await send.delete()
        if remove_view_after:
            await view.message.edit(view=None)
        return ConfirmResult(send, view.value)

    async def prompt(
        self,
        message=None,
        embed: discord.Embed = None,
        *,
        timeout=60,
        delete_after=True,
        raw=False,
    ):
        if raw is True:
            send = await self.no_reply(content=message, embed=embed)
        elif message:
            message = f"{message}"
            send = await self.send(message)
        elif embed:
            embed.description = f"{embed.description}\n\n{message or ''}"
            send = await self.send(embed=embed)

        def check(message: discord.Message):
            return self.author == message.author and self.channel == message.channel

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            confirm = False
            pass
        else:
            return msg.content
        if delete_after:
            await send.delete()
        return confirm

    async def can_delete(self, *args, **kwargs):
        view = TrashView(member=self.author, ctx=self)
        view.message = await self.send(*args, **kwargs, view=view)


def setup(bot: AvimetryBot):
    bot.context = AvimetryContext


def teardown(bot: AvimetryBot):
    bot.context = commands.Context
