import discord
import re
import core

from utils import AvimetryBot


class Highlight(core.Cog):
    def __init__(self, bot: AvimetryBot):
        self.bot = bot

    @core.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if not message.guild:
            return
        if message.author.bot:
            return
        words = "bot|asd|lol|stupid"
        match = re.findall(rf"({words}\s*)", message.content, flags=re.IGNORECASE)
        if match:
            match_embed = discord.Embed(
                title="Highlight detected",
                description=f"In {message.channel.mention}, you were highlighted with the word(s) `{', '.join(match)}`"
            )
            match_embed.add_field(name="Message content:", value=message.content)
            await message.channel.send(embed=match_embed)
        return


def setup(bot: AvimetryBot):
    bot.add_cog(Highlight(bot))
