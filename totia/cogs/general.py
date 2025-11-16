from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.name}!")

    @commands.command()
    async def cat(self, ctx):
        await ctx.send(f"cat is the name of a lazy person!! {ctx.author.name}")

async def setup(bot):
    await bot.add_cog(General(bot))
