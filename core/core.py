"""
Custom command class for discord.ext.commands
Copyright (C) 2021 - 2022 avizum

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

from __future__ import annotations


import datetime
from typing import TYPE_CHECKING, TypeVar, Callable, Any, overload

import discord
from discord.ext import commands
from discord.utils import MISSING


if TYPE_CHECKING:
    from .avimetry import Bot


T = TypeVar("T")
GroupT = TypeVar("GroupT", bound="Group")
CommandT = TypeVar("CommandT", bound="Command")


def to_list(thing) -> list[str]:
    return [thing] if isinstance(thing, str) else list(thing)


default_cooldown = commands.Cooldown(3, 15)
def owner_cd(message: discord.Message):
    bot = message._state._get_client()
    assert isinstance(bot, Bot)
    return None if message.author.id in bot.owner_ids else default_cooldown


mapping = commands.DynamicCooldownMapping(owner_cd, commands.BucketType.user)
mapping._cooldown = default_cooldown


class Command(commands.Command):
    def __init__(self, func, **kwargs) -> None:
        self.member_permissions: list[str] = to_list(
            kwargs.get("member_permissions")
            or getattr(func, "member_permissions", ["none_needed"])
            or kwargs.get("extras", {}).get("member_permissions")
        )
        self.bot_permissions: list[str] = to_list(
            kwargs.get("bot_permissions")
            or getattr(func, "bot_permissions", ["none_needed"])
            or kwargs.get("extras", {}).get("bot_permissions")
        )
        super().__init__(func, **kwargs)
        if not self._buckets._cooldown:
            cd = commands.Cooldown(3, 15)
            self._buckets = commands.DynamicCooldownMapping(owner_cd, commands.BucketType.user)
            self._buckets._cooldown = cd

    def __repr__(self) -> str:
        return f"<core.Command name={self.qualified_name}>"


class Group(commands.Group, Command):
    def __init__(self, *args, **kwargs) -> None:
        self.invoke_without_command = kwargs.get("invoke_without_command", True)
        super().__init__(*args, **kwargs)

    def command(
        self,
        name: str = MISSING,
        hybrid: bool = False,
        **attrs: Any,
    ) -> Callable[..., Command | HybridCommand]:
        def decorator(func):
            attrs.setdefault("parent", self)
            result = command(name=name, hybrid=hybrid, **attrs)(func)
            self.add_command(result)
            return result

        return decorator

    def group(
        self,
        name: str = MISSING,
        hybrid: bool = False,
        **attrs: Any,
    ) -> Callable[..., Group | HybridGroup]:
        def decorator(func):
            attrs.setdefault("parent", self)
            result = group(name=name, hybrid=hybrid, **attrs)(func)
            self.add_command(result)
            return result

        return decorator


class HybridCommand(commands.HybridCommand, Command):
    pass


class HybridGroup(commands.HybridGroup, Group):
    pass


class Cog(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.load_time: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)

@overload
def command(
    name: str = MISSING,
    hybrid: bool = True,
    **kwargs: Any
) -> Callable[...,  HybridCommand]:
    ...

@overload
def command(
    name: str = MISSING,
    hybrid: bool = False,
    **kwargs: Any
) -> Callable[..., Command]:
    ...

def command(
    name: str = MISSING,
    hybrid: bool = False,
    **kwargs: Any
) -> Callable[..., Command | HybridCommand]:
    cls = HybridCommand if hybrid else Command

    def decorator(func):
        if isinstance(func, Command):
            raise TypeError("Callback is already a command.")
        return cls(func, name=name, **kwargs)

    return decorator


def group(
    name: str = MISSING,
    hybrid: bool = False,
    **kwargs: Any
) -> Callable[..., Group | HybridGroup]:
    cls = HybridGroup if hybrid else Group

    def decorator(func: Any) -> Group | HybridGroup:
        if isinstance(func, Group):
            raise TypeError("Callback is already a group.")
        return cls(func, name=name, **kwargs)

    return decorator


describe = discord.app_commands.describe
