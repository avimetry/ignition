import discord
from discord.ext import commands
import aiozaneapi
import aiohttp
from io import BytesIO
import io
from PIL import Image

class manipulation(commands.Cog):
    def __init__(self, avimetry):
        self.avimetry=avimetry

    async def member_convert(self, ctx, url):
        try:
            member_url=await commands.MemberConverter().convert(ctx, url)
            url=member_url.avatar_url_as(format="png")
            return url
        except Exception:
            url=url
            return url

    @commands.command(usage="[url or member]", brief="Returns a gif of your image being scaled")
    async def magic(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            magic=await self.avimetry.zaneapi.magic(str(url))
            return await ctx.send(file=discord.File(io.BytesIO(magic.read()), filename="magic.gif"))

    @commands.command(usage="[url or member]", brief="Returns a gif of your image being bent into a floor")
    async def floor(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            floor=await self.avimetry.zaneapi.floor(str(url))
            return await ctx.send(file=discord.File(io.BytesIO(floor.read()), filename="floor.gif"))

    @commands.command(usage="[url or member]", brief="Returns your image deepfried")
    async def deepfry(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            deepfry=await self.avimetry.zaneapi.deepfry(str(url))
            return await ctx.send(file=discord.File(BytesIO(deepfry.read()), filename="deepfry.png"))

    @commands.command(usage="[url or member]", brief="Returns your image with black and white dots")
    async def dots(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            dots=await self.avimetry.zaneapi.dots(str(url))
            return await ctx.send(file=discord.File(BytesIO(dots.read()), filename="dots.png"))

    @commands.command(usage="[url or member]", brief="Returns your image heavilly compressed and with low quality, just like jpeg")
    async def jpeg(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            jpeg=await self.avimetry.zaneapi.jpeg(str(url))
            return await ctx.send(file=discord.File(BytesIO(jpeg.read()), filename="jpeg.png"))

    @commands.command(usage="[url or member]", brief="Returns a gif of all the pixels spreading out")
    async def spread(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            spread=await self.avimetry.zaneapi.spread(str(url))
            return await ctx.send(file=discord.File(BytesIO(spread.read()), filename="spread.gif"))

    @commands.command(usage="[url or member]", brief="Returns your image on a cube")
    async def cube(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            cube=await self.avimetry.zaneapi.cube(str(url))
            return await ctx.send(file=discord.File(io.BytesIO(cube.read()), filename="cube.png"))

    @commands.command(usage="[url or member]", brief="Returns the pixels on your image")
    async def sort(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            sort=await self.avimetry.zaneapi.sort(str(url))
            return await ctx.send(file=discord.File(BytesIO(sort.read()), filename="sort.png"))

    @commands.command(usage="[url or member]", brief="Returns up to 8 colors from your image")
    async def palette(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            palette=await self.avimetry.zaneapi.palette(str(url))
            return await ctx.send(file=discord.File(BytesIO(palette.read()), filename="palette.png"))

    @commands.command(usage="[url or member]", brief="Returns an inverted version of your image")
    async def invert(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            invert=await self.avimetry.zaneapi.invert(str(url))
            return await ctx.send(file=discord.File(BytesIO(invert.read()), filename="invert.png"))

    @commands.command(usage="[url or member]", brief="Returns a poserized version of your image")
    async def posterize(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            posterize=await self.avimetry.zaneapi.posterize(str(url))
            return await ctx.send(file=discord.File(BytesIO(posterize.read()), filename="posterize.png"))

    @commands.command(usage="[url or member]", brief="Returns your image as grayscale")
    async def grayscale(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            grayscale=await self.avimetry.zaneapi.grayscale(str(url))
            return await ctx.send(file=discord.File(BytesIO(grayscale.read()), filename="grayscale.png"))

    @commands.command(usage="[url or member]", brief="Returns an your image scaled down then scaled back up")
    async def pixelate(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            pixelate=await self.avimetry.zaneapi.pixelate(str(url))
            return await ctx.send(file=discord.File(BytesIO(pixelate.read()), filename="pixelate.png"))

    @commands.command(usage="[url or member]", brief="Returns a gif of your image being swirled")
    async def swirl(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            swirl=await self.avimetry.zaneapi.swirl(str(url))
            return await ctx.send(file=discord.File(BytesIO(swirl.read()), filename="swirl.gif"))

    @commands.command(usage="[url or member]", brief="Returns your image with a sobel filter")
    async def sobel(self, ctx, url=None):
        if url==None:
            url=ctx.author.avatar_url_as(format="png")
        else:
            url=await self.member_convert(ctx, url)
        async with ctx.channel.typing():
            sobel=await self.avimetry.zaneapi.sobel(str(url))
            return await ctx.send(file=discord.File(BytesIO(sobel.read()), filename="sobel.png"))
            
def setup(avimetry):
    avimetry.add_cog(manipulation(avimetry))