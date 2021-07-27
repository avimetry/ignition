"""
Fun commands for users
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
import random
import asyncio
import akinator
import typing
import datetime

from utils import core
from aiogtts import aiogTTS
from io import BytesIO
from discord.ext import commands
from akinator.async_aki import Akinator
from utils import AvimetryBot, AvimetryContext, Timer


class Fun(commands.Cog):
    """
    Fun commands for you and friends.
    """
    def __init__(self, bot: AvimetryBot):
        self.bot = bot
        self.load_time = datetime.datetime.now()
        self._cd = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.user)

    async def do_mock(self, string: str):
        return "".join(random.choice([mock.upper, mock.lower])() for mock in string)

    @core.command(
        aliases=["8ball", "8b"],
        brief="Ask the 8ball something",
    )
    @commands.cooldown(5, 15, commands.BucketType.member)
    async def eightball(self, ctx: AvimetryContext, *, question):
        responses = [
            "As I see it, yes.", "Ask again later.",
            "Better not tell you now.", "Cannot predict now.",
            "Concentrate and ask again.", "Don’t count on it.",
            "It is certain.", "It is decidedly so.",
            "Most likely.", "My reply is no.",
            "My sources say no.", "Outlook not so good.",
            "Outlook good.", "Reply hazy, try again.",
            "Signs point to yes.", "Very doubtful.",
            "Without a doubt.", "Yes.",
            "Yes – definitely.", "You may rely on it.",
        ]
        if ctx.author.id in self.bot.owner_ids and question.lower().endswith(
            "\u200b"
        ):
            responses = [
                "It is certain.", "Without a doubt.",
                "You may rely on it.", "Yes definitely.",
                "It is decidedly so.", "As I see it, yes.",
                "Most likely.", "Yes.",
                "Outlook good.", "Signs point to yes.",
            ]
        ballembed = discord.Embed(title=":8ball: Magic 8 Ball")
        ballembed.add_field(name="Question:", value=f"{question}", inline=False)
        ballembed.add_field(
            name="Answer:", value=f"{random.choice(responses)}", inline=False
        )
        await ctx.send(embed=ballembed)

    @core.command(brief="Pick a random number from 1 to 100", usage="[amount]")
    async def random(self, ctx: AvimetryContext, amount: int = 100):
        x = random.randint(1, amount)
        e = discord.Embed()
        e.add_field(name="Random Number", value=f"The number is {x}")
        await ctx.send(embed=e)

    @core.command(
        aliases=["murder"], brief="Kill some people. Make sure you don't get caught!")
    @commands.cooldown(2, 30, commands.BucketType.member)
    async def kill(self, ctx: AvimetryContext, member: discord.Member):
        if member == self.bot.user or member.bot:
            await ctx.send("Nope.")
        elif member == ctx.author:
            await ctx.send("You tried to shoot yourself in the head, but you couldn't because I won't let you :)")
        else:
            author = ctx.author.mention
            member = member.mention
            kill_response = [
                f"{author} killed {member}.",
                f"{author} murdered {member} with a machine gun.",
                f"{author} accidentally shot themselves in the face while trying to load the gun.",
                f"{author} died while summoning a demon to kill {member}",
                f"{member} summoned a demon to kill {author}.",
                f"{author} was caught by the police because they posted his plans to kill {member}",
                f"{author} hired a hitman to kill {member}.",
                f"{author} shot {member}. While reloading the gun, {author} shot themselves on the head.",
                f"{author} kidnapped {member} and chopped their head off with a guillotine",
                f"{author} sniped {member} at the store.",
                f"{author} tried to poison {member} but {author} put the poison in their drink.",
                f"{author} died whilst fighting {member}.",
                f"{member} was stoned to death by {author}.",
                f"{member} was almost killed by {author} but {member} took the gun and shot {author}",
            ]
            await ctx.send(f"{random.choice(kill_response)}")

    @core.command(brief="Makes me say a message")
    @commands.cooldown(1, 120, commands.BucketType.member)
    async def say(self, ctx: AvimetryContext, *, message):
        await ctx.no_reply(message)

    @core.command(brief="Makes me say a message but I delete your message")
    @commands.cooldown(1, 120, commands.BucketType.member)
    @core.has_permissions(manage_messages=True)
    async def dsay(self, ctx: AvimetryContext, *, message):
        await ctx.message.delete()
        await ctx.no_reply(message)

    @core.command(
        brief="Copies someone so it looks like a person actually sent the message."
    )
    @core.bot_has_permissions(manage_webhooks=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def copy(self, ctx: AvimetryContext, member: typing.Union[discord.User, discord.Member], *, text):
        if member == self.bot.user:
            say = self.bot.get_command("say")
            return await say(ctx, message=text)
        webhooks = await ctx.channel.webhooks()
        avimetry_webhook = discord.utils.get(webhooks, name="Avimetry")
        if not avimetry_webhook:
            avimetry_webhook = await ctx.channel.create_webhook(
                name="Avimetry", reason="For Avimetry copy command.",
                avatar=await self.bot.user.avatar_url.read())
        await avimetry_webhook.send(
            text, username=member.display_name,
            avatar_url=member.avatar_url_as(format="png"),
            allowed_mentions=discord.AllowedMentions.none())

    @core.command(
        aliases=["fp", "facep", "fpalm"]
    )
    async def facepalm(self, ctx: AvimetryContext, member: discord.Member = None):
        if member is None:
            return await ctx.send(f"{ctx.author.mention} hit their head")
        return await ctx.send(f"{ctx.author.mention} hit their head because {member.mention} was being stupid.")

    @core.command(brief="Remove the skin off of people that you don't like.")
    async def skin(self, ctx: AvimetryContext, member: discord.Member):
        await ctx.message.delete()
        if member == ctx.author:
            c = discord.Embed(description="You can't skin yourself, stupid")
            await ctx.send(embed=c)
        else:
            e = discord.Embed(description=f"{member.mention} was skinned.")
            await ctx.send(embed=e)

    @core.command(aliases=["sd"], brief="Self destruct? Who put that there?")
    async def selfdestruct(self, ctx: AvimetryContext):
        a = discord.Embed(
            description=f"{ctx.author.mention} self destructed due to overloaded fuel canisters")
        await ctx.send(embed=a)

    @core.command(brief="Dropkick someone")
    async def dropkick(self, ctx: AvimetryContext, *, mention: discord.Member):
        if mention == ctx.author:
            embed = discord.Embed(description=f"{ctx.author.mention} tried dropkicking themselves.")
        else:
            embed = discord.Embed(
                description=f"{ctx.author.mention} dropkicked {mention.mention}, killing them.")
        await ctx.send(embed=embed)

    @core.command(
        brief=(
            "Get the cookie! (If you mention a user, I will listen to you and the member that you mentioned.)"),
        aliases=["\U0001F36A", "vookir", "kookie"]
        )
    @commands.cooldown(5, 10, commands.BucketType.member)
    @commands.max_concurrency(2, commands.BucketType.channel)
    async def cookie(self, ctx: AvimetryContext, member: typing.Optional[discord.Member] = None):
        if member == ctx.author:
            return await ctx.send("You can't play against yourself.")
        cookie_embed = discord.Embed(
            title="Get the cookie!",
            description="Get ready to grab the cookie!")
        cd_cookie = await ctx.send(embed=cookie_embed)
        await cd_cookie.edit(embed=cookie_embed)
        await asyncio.sleep(random.randint(1, 12))
        cookie_embed.title = "GO!"
        cookie_embed.description = "GET THE COOKIE NOW!"
        await cd_cookie.edit(embed=cookie_embed)
        await cd_cookie.add_reaction("\U0001F36A")

        if member:
            def check(reaction, user):
                return(
                    reaction.message.id == cd_cookie.id and
                    str(reaction.emoji) == "\U0001F36A" and
                    user in [ctx.author, member]
                )
        else:
            def check(reaction, user):
                return (
                    reaction.message.id == cd_cookie.id and
                    str(reaction.emoji) in "\U0001F36A" and
                    user != self.bot.user
                )

        try:
            with Timer() as reaction_time:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=10
                )
        except asyncio.TimeoutError:
            cookie_embed.title = "Game over!"
            cookie_embed.description = "Nobody got the cookie :("
            await cd_cookie.edit(embed=cookie_embed)
            await cd_cookie.remove_reaction("\U0001F36A", ctx.me)
        else:
            if str(reaction.emoji) == "\U0001F36A":
                thing = reaction_time.total_time * 1000
                total_second = f"**{thing:.2f}ms**"
                if thing > 1000:
                    gettime = thing / 1000
                    total_second = f"**{gettime:.2f}s**"
                cookie_embed.title = "Nice!"
                cookie_embed.description = f"{user.mention} got the cookie in **{total_second}**"
                await cd_cookie.remove_reaction("\U0001F36A", ctx.me)
                return await cd_cookie.edit(embed=cookie_embed)

    async def remove(self, message: discord.Message, emoji, user, perm: bool):
        if not perm:
            return
        await message.remove_reaction(emoji, user)

    async def clear(self, message: discord.Message, perm: bool):
        if not perm:
            return
        await message.clear_reactions()

    @core.command(
        name="akinator",
        aliases=["aki", "avinator"],
        brief="Play a game of akinator.")
    @commands.cooldown(1, 60, commands.BucketType.member)
    @commands.max_concurrency(1, commands.BucketType.channel)
    @core.bot_has_permissions(add_reactions=True)
    async def fun_akinator(self, ctx: AvimetryContext, mode="en"):
        ended = False
        bot_perm = ctx.me.permissions_in(ctx.channel)
        perms = True if bot_perm.manage_messages is True else False
        aki_dict = {
            "<:greentick:777096731438874634>": "yes",
            "<:redtick:777096756865269760>": "no",
            "\U0001f937": "idk",
            "\U0001f914": "probably",
            "\U0001f614": "probably not",
            "<:Back:815854941083664454>": "back",
            "<:Stop:815859174667452426>": "stop"
        }
        aki_react = list(aki_dict)
        aki_client = Akinator()
        akinator_embed = discord.Embed(
            title="Akinator",
            description="Starting Game..."
        )
        async with ctx.channel.typing():
            initial_messsage = await ctx.send(embed=akinator_embed)
            for reaction in aki_react:
                await initial_messsage.add_reaction(reaction)
            game = await aki_client.start_game(mode)

        while aki_client.progression <= 80:
            akinator_embed.description = game
            await initial_messsage.edit(embed=akinator_embed)

            def check(reaction, user):
                return (
                    reaction.message.id == initial_messsage.id and
                    str(reaction.emoji) in aki_react and
                    user == ctx.author and
                    user != self.bot.user
                )

            done, pending = await asyncio.wait([
                self.bot.wait_for("reaction_remove", check=check, timeout=20),
                self.bot.wait_for("reaction_add", check=check, timeout=20)
            ], return_when=asyncio.FIRST_COMPLETED)

            try:
                reaction, user = done.pop().result()

            except asyncio.TimeoutError:
                await self.clear(initial_messsage, perms)
                akinator_embed.description = (
                    "Akinator session closed because you took too long to answer."
                )
                ended = True

                await initial_messsage.edit(embed=akinator_embed)
                break
            else:
                ans = aki_dict[str(reaction.emoji)]
                if ans == "stop":
                    ended = True
                    akinator_embed.description = "Akinator session stopped."
                    await initial_messsage.edit(embed=akinator_embed)
                    await self.clear(initial_messsage, perms)
                    break
                elif ans == "back":
                    try:
                        game = await aki_client.back()
                    except akinator.CantGoBackAnyFurther:
                        pass
                else:
                    answer = ans

            finally:
                for future in done:
                    future.exception()
                for future in pending:
                    future.cancel()

            await self.remove(initial_messsage, reaction.emoji, user, perms)
            game = await aki_client.answer(answer)
        try:
            await initial_messsage.clear_reactions()
        except discord.Forbidden:
            if ended:
                return
            await initial_messsage.delete()
            initial_messsage = await ctx.send("...")
        if ended:
            return
        await aki_client.win()

        akinator_embed.description = (
            f"I think it is {aki_client.first_guess['name']} ({aki_client.first_guess['description']})! Was I correct?"
        )
        akinator_embed.set_image(url=f"{aki_client.first_guess['absolute_picture_path']}")
        await initial_messsage.edit(embed=akinator_embed)
        reactions = ["<:greentick:777096731438874634>", "<:redtick:777096756865269760>"]
        for reaction in reactions:
            await initial_messsage.add_reaction(reaction)

        def yes_no_check(reaction, user):
            return (
                reaction.message.id == initial_messsage.id and
                str(reaction.emoji) in ["<:greentick:777096731438874634>", "<:redtick:777096756865269760>"] and
                user != self.bot.user and
                user == ctx.author
            )
        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", check=yes_no_check, timeout=60
            )
        except asyncio.TimeoutError:
            await self.clear(initial_messsage, perms)
        else:
            await self.clear(initial_messsage, perms)
            if str(reaction.emoji) == "<:greentick:777096731438874634>":
                akinator_embed.description = (
                    f"{akinator_embed.description}\n\n------\n\nYay!"
                )
            if str(reaction.emoji) == "<:redtick:777096756865269760>":
                akinator_embed.description = (
                    f"{akinator_embed.description}\n\n------\n\nAww, maybe next time."
                )
            await initial_messsage.edit(embed=akinator_embed)

    @core.command(
        brief="Check if a person is compatible with another person."
    )
    async def ship(self, ctx: AvimetryContext, person1: discord.Member, person2: discord.Member):
        if 750135653638865017 in (person1.id, person2.id):
            return await ctx.send(f"{person1.mention} and {person2.mention} are 0% compatible with each other")
        if person1 == person2:
            return await ctx.send("That's not how that works")
        percent = random.randint(0, 100)
        await ctx.send(f"{person1.mention} and {person2.mention} are {percent}% compatible with each other")

    @core.command(
        brief="Get the PP size of someone"
    )
    async def ppsize(self, ctx: AvimetryContext, member: discord.Member = None):
        member = member or ctx.author
        pp_embed = discord.Embed(
            title=f"{member.name}'s pp size",
            description=f"8{'=' * random.randint(0, 12)}D"
        )
        await ctx.send(embed=pp_embed)

    @core.command(
        name="10s",
        brief="Test your reaction time!",
    )
    @core.bot_has_permissions(add_reactions=True)
    async def _10s(self, ctx: AvimetryContext):
        embed_10s = discord.Embed(
            title="10 seconds",
            description="Click the cookie in 10 seconds"
        )
        react_message = await ctx.send(embed=embed_10s)
        await react_message.add_reaction("\U0001F36A")

        def check_10s(reaction, user):
            return (
                reaction.message.id == react_message.id and str(reaction.emoji) in "\U0001F36A" and user == ctx.author
            )

        try:
            with Timer() as timer:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=check_10s, timeout=20
                )
        except asyncio.TimeoutError:
            pass
        else:
            if str(reaction.emoji) == "\U0001F36A":
                final = timer.total_time
                if final < 5.0:
                    embed_10s.description = "Wait 10 seconds to get the cookie."
                    return await react_message.edit(embed=embed_10s)
                embed_10s.description = (
                    f"You got the cookie in {final:.2f} seconds with {(final-10)*1000:.2f}ms reaction time\n"
                )
                if final < 9.99:
                    embed_10s.description = f"You got the cookie in {final:.2f} seconds"
                await react_message.edit(embed=embed_10s)

    @core.command(
        brief="Gets a random post from a subreddit"
    )
    @commands.cooldown(1, 15, commands.BucketType.member)
    async def reddit(self, ctx: AvimetryContext, subreddit):
        if subreddit.startswith("r/"):
            subreddit = subreddit.replace("r/", "")
        async with self.bot.session.get(f"https://www.reddit.com/r/{subreddit}.json") as content:
            if content.status == 404:
                return await ctx.send("This subreddit does not exist. Please check your spelling and try again.")
            if content.status != 200:
                return await ctx.send("There has been a problem at Reddit. Please try again later.")
            stuff = await content.json()
        get_data = stuff["data"]["children"]
        if not get_data:
            return await ctx.send("No posts found in this subreddit.")
        try:
            data = random.choice(get_data)["data"]
        except Exception:
            return await ctx.send("No posts found.")
        desc = data["selftext"] if data["selftext"] is not None else ""
        if len(desc) > 2048:
            desc = f'{data["selftext"][:2045]}...'
        embed = discord.Embed(
            title=data["title"],
            url=f"https://reddit.com{data['permalink']}",
            description=desc
        )
        url = data["url"]
        embed.set_image(url=url)
        embed.add_field(
            name="Post Info:",
            value=(
                f"<:upvote:818730949662867456> {data['ups']} "
                f"<:downvote:818730935829659665> {data['downs']}\n"
                f"Upvote ratio: {data['upvote_ratio']}\n"
            )
        )
        if data["over_18"]:
            if ctx.channel.is_nsfw():
                return await ctx.send(embed=embed)
            else:
                return await ctx.send("NSFW posts can't be send in non-nsfw channels.")
        return await ctx.send(embed=embed)

    @core.command(
        brief="Gets a meme from r/memes | r/meme subreddits."
    )
    @commands.cooldown(1, 15, commands.BucketType.member)
    async def meme(self, ctx: AvimetryContext):
        reddit = self.bot.get_command("reddit")
        subreddits = ["memes", "meme"]
        await reddit(ctx, subreddit=random.choice(subreddits))

    @core.command(
        brief="See how fast you can react with the correct emoji."
    )
    @commands.cooldown(1, 10, commands.BucketType.channel)
    @core.bot_has_permissions(add_reactions=True)
    async def reaction(self, ctx: AvimetryContext):
        emoji = ["🍪", "🎉", "🧋", "🍒", "🍑"]
        random_emoji = random.choice(emoji)
        random.shuffle(emoji)
        embed = discord.Embed(
            title="Reaction time",
            description="After 1-15 seconds I will reveal the emoji."
        )
        first = await ctx.send(embed=embed)
        for react in emoji:
            await first.add_reaction(react)
        await asyncio.sleep(2.5)
        embed.description = "Get ready!"
        await first.edit(embed=embed)
        await asyncio.sleep(random.randint(1, 15))
        embed.description = f"GET THE {random_emoji} EMOJI!"
        await first.edit(embed=embed)

        def check(reaction, user):
            return(
                reaction.message.id == first.id and str(reaction.emoji) == random_emoji and user != self.bot.user)

        try:
            with Timer() as timer:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=15)
        except asyncio.TimeoutError:
            embed.description = "Timeout"
            await first.edit(embed=embed)
        else:
            if str(reaction.emoji) == random_emoji:
                gettime = timer.total_time * 1000
                total_second = f"**{gettime:.2f}ms**"
                if gettime > 1000:
                    gettime = gettime / 1000
                    total_second = f"**{gettime:.2f}s**"
                embed.description = f"{user.mention} got the {random_emoji} in {total_second}"
                return await first.edit(embed=embed)

    @core.command(
        name="guessthatlogo",
        aliases=["gtl"],
        brief="Try to guess the name of a logo. (Powered by Dagpi)"
    )
    @commands.cooldown(2, 10, commands.BucketType.member)
    async def dag_guess_that_logo(self, ctx: AvimetryContext):
        async with ctx.channel.typing():
            logo = await self.bot.dagpi.logo()
        embed = discord.Embed(
            title="Which logo is this?",
            description=f"{logo.clue}"
        )
        embed.set_image(url=logo.question)
        message = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author

        try:
            wait = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            embed.title = f"{self.bot.emoji_dictionary['red_tick']} | Time's Up!"
            embed.description = f"You took too long. The correct answer is {logo.brand}"
            try:
                embed.set_image(url=logo.answer)
            except discord.HTTPException:
                pass
            await message.edit(embed=embed)
        else:
            if wait.content.lower() == logo.brand.lower():
                embed.title = "🎉 Good Job 🎉"
                embed.description = f"The answer was {logo.brand}"
                try:
                    embed.set_image(url=logo.answer)
                except discord.HTTPException:
                    pass
                return await message.edit(embed=embed)
            embed.title = f"{self.bot.emoji_dictionary['red_tick']} | Wrong"
            embed.description = f"Your answer was {wait.content}.\nThe correct answer is actually {logo.brand}"
            try:
                embed.set_image(url=logo.answer)
            except discord.HTTPException:
                pass
            await message.edit(embed=embed)

    @core.command(
        name="roast",
        brief="Roasts a person. (Powered by Dagpi)")
    async def dag_roast(self, ctx: AvimetryContext, member: discord.Member):
        roast = await self.bot.dagpi.roast()
        await ctx.send(f"{member.mention}, {roast}")

    @core.command(
        name="funfact",
        brief="Gets a random fun fact. (Powered by Dagpi)")
    async def dag_fact(self, ctx: AvimetryContext):
        fact = await self.bot.dagpi.fact()
        await ctx.send(fact)

    @core.command(
        brief="Checks if a person is gay"
    )
    async def gay(self, ctx: AvimetryContext, member: discord.Member = None):
        if member is None:
            member = ctx.author
        conf = await ctx.confirm(f"Is {member.mention} gay?")
        if conf:
            return await ctx.send(f"{member.mention} is gay.")
        return await ctx.send(f"{member.mention} is not gay.")

    @core.command(
        brief="Check how gay a person is"
    )
    async def gayrate(self, ctx: AvimetryContext, member: discord.Member = None):
        if member is None:
            member = ctx.author
        if await self.bot.is_owner(member):
            return await ctx.send(f"{member.mention} is **{random.randint(0, 10)}%** gay :rainbow:")
        return await ctx.send(f"{member.mention} is **{random.randint(10, 100)}%** gay :rainbow:")

    @core.command()
    async def height(self, ctx: AvimetryContext):
        await ctx.send("How tall are you? (Ex: 1'4\")")

        def check(message: discord.Message):
            return message.author == ctx.author and message.channel == ctx.channel
        try:
            height = await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("You didn't respond in time!")
        else:
            embed = discord.Embed(
                title="Height",
                description=f"You are {height.content}!"
            )
            embed.set_footer(text="No need to thank me.")
            await ctx.send(embed=embed)

    @core.command()
    async def clap(self, ctx: AvimetryContext, *, words):
        input = words.split(" ")
        output = f"👏 {' 👏 '.join(input)} 👏"
        await ctx.send(output)

    @core.command()
    async def recursion(self, ctx: AvimetryContext):
        embed = discord.Embed(
            title="Invalid Command",
            description='"recursion" was not found. Did you mean...\n`recursion`'
        )
        embed.set_footer(text=f'Use {ctx.prefix}help to see the whole list of commands.')
        await ctx.send(embed=embed)

    @core.command()
    async def tts(self, ctx: AvimetryContext, *, text):
        async with ctx.channel.typing():
            aiogtts = aiogTTS()
            buffer = BytesIO()
            await aiogtts.write_to_fp(text, buffer, lang='en')
            buffer.seek(0)
            file = discord.File(buffer, f"{ctx.author.name}-tts.mp3")
        await ctx.send(file=file)

    @core.command(user_permissions='manage_messages')
    async def aaa(self, ctx: AvimetryContext):
        await ctx.send('a')


def setup(bot):
    bot.add_cog(Fun(bot))
