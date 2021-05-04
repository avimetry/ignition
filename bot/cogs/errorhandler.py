import discord
import datetime
import traceback
import sys
import prettify_exceptions
import humanize
from config import webhooks
from utils.errors import Blacklisted
from utils.context import AvimetryContext
from discord.ext import commands
from difflib import get_close_matches


class ErrorHandler(commands.Cog):
    def __init__(self, avi):
        self.avi = avi
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 300, commands.BucketType.member)
        self.error_webhook = discord.Webhook.from_url(
            webhooks["error_log"],
            adapter=discord.AsyncWebhookAdapter(self.avi.session)
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: AvimetryContext, error):
        pre = ctx.clean_prefix
        error = getattr(error, "original", error)

        if hasattr(ctx.command, 'on_error'):
            return

        if isinstance(error, Blacklisted):
            blacklisted = discord.Embed(
                title="You are blacklisted",
                description=(
                    f"Blacklist reason: `{error.reason}`\n"
                    "If you think this message is an error, "
                    "Please join the [support](https://discord.gg/KaqqPhfwS4) server to appeal."
                ),
                color=discord.Color.red(),
            )
            bucket = self.cd_mapping.get_bucket(ctx.message)
            retry_after = bucket.update_rate_limit()
            if not retry_after:
                await ctx.send(embed=blacklisted, delete_after=15)

        elif isinstance(error, commands.CommandNotFound):
            if ctx.author.id in ctx.cache.blacklist:
                return
            not_found_embed = discord.Embed(
                title="Invalid Command", color=discord.Color.red()
            )
            not_found = ctx.invoked_with
            match = "\n".join(
                get_close_matches(not_found, [i.name for i in ctx.bot.commands])
            )
            if not match:
                return
            not_found_embed.description = f'"{not_found}" was not found. Did you mean...\n`{match}`'
            not_found_embed.set_footer(
                text=f"Not what you meant? Use {pre}help to see the whole list of commands."
            )
            await ctx.send(embed=not_found_embed)

        elif isinstance(error, commands.CommandOnCooldown):
            cd = discord.Embed(
                title="Slow down",
                description=f"This command has a cooldown o. Try again in {humanize.naturaldelta(error.retry_after)}.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=cd)

        elif isinstance(error, commands.BotMissingPermissions):
            mp = error.missing_perms
            missing_perms = (
                " ".join(str(elem) for elem in mp)
                .replace("_", " ")
                .replace("guild", "server")
                .title()
            )

            bnp = discord.Embed(
                title="Missing Permissions",
                description=f"I need the following permissions to run this command:\n`{missing_perms}`",
                color=discord.Color.red(),
            )
            await ctx.send(embed=bnp)

        elif isinstance(error, commands.MissingPermissions):
            mp = error.missing_perms
            missing_perms = (
                " ".join(str(elem) for elem in mp)
                .replace("_", " ")
                .replace("guild", "server")
                .title()
            )

            np = discord.Embed(
                title="Missing Permissions",
                description=f"You need the following permissions to run this command:\n`{missing_perms}`",
                color=discord.Color.red(),
            )
            await ctx.send(embed=np)

        elif isinstance(error, commands.NotOwner):
            no = discord.Embed(
                title="Missing Permissions",
                description="You need to be bot owner to run this command.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=no)

        elif isinstance(error, commands.MissingRequiredArgument):
            try:
                ctx.command.reset_cooldown(ctx)
            except Exception:
                pass
            a = discord.Embed(
                title="Missing Arguments",
                description=(
                    f"You need to put the `{error.param.name}` parameter to run this command.\n"
                    f"Send help for `{ctx.invoked_with}`?"
                ),
                color=discord.Color.red(),
            )
            conf = await ctx.confirm(embed=a)
            if conf:
                await ctx.send_help(ctx.command)
            else:
                return

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(
                "This command has been disabled because it is:\nNot done yet, API error or New API key needed")

        elif isinstance(error, commands.BadArgument):
            try:
                ctx.reset_cooldown(ctx)
            except Exception:
                pass
            ba = discord.Embed(
                title="Bad Argument",
                description=str(error),
                color=discord.Color.red()
            )
            await ctx.send(embed=ba)

        elif isinstance(error, commands.TooManyArguments):
            try:
                ctx.reset_cooldown(ctx)
            except Exception:
                pass
            many_arguments = discord.Embed(
                title="Too many arguments",
                description=str(error),
                color=discord.Color.red()
            )
            await ctx.send(embed=many_arguments)

        elif isinstance(error, commands.NoPrivateMessage):
            return

        elif isinstance(error, commands.MaxConcurrencyReached):
            max_uses = discord.Embed(
                title="Slow Down",
                description=(
                    f"This command can only be used {error.number} "
                    f"{'time' if error.number == 1 else 'times'} per {error.per.name}."),
                color=discord.Color.red()
            )
            await ctx.send(embed=max_uses)
        else:
            ctx.command.reset_cooldown(ctx)
            prettify_exceptions.DefaultFormatter().theme["_ansi_enabled"] = False
            long_exception = "".join(
                prettify_exceptions.DefaultFormatter().format_exception(
                    type(error), error, error.__traceback__
                )
            )
            print("------")
            print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )
            print("------")
            ee = discord.Embed(
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            short_exception = "".join(
                traceback.format_exception_only(type(error), error)
            )
            myst_exception = await self.avi.myst.post(
                long_exception, syntax="python"
            )
            ee.title = "Unknown Error"
            ee.description = (
                "Uh oh, An uncaught error has occured. This normally shouldn't happen. "
                "The error was sent to the [support server](https://discord.gg/KaqqPhfwS4)."
                f"\n\n[Error]({myst_exception}):\n```py\n{short_exception}```"
            )
            try:
                await ctx.send(embed=ee)
                embed = discord.Embed(
                    title="Uncaught Error",
                    description=f"```py\n {short_exception}```",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Error Info",
                    value=(
                        f"Command: {ctx.command.name}\n"
                        f"Invoker: {ctx.author}\n"
                        f"Full Error: {myst_exception}"
                    )
                )
                await self.error_webhook.send(embed=embed, username="Error")
            except Exception:
                return


def setup(avi):
    avi.add_cog(ErrorHandler(avi))
