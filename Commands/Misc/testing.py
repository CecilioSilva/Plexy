from discord.ext import commands
from Commands.settings import Settings
from Commands.logger import main_logger

settings = Settings()



class testing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(rate=1, per=settings.command_config.cooldowns.ping, type=commands.BucketType.member)
    @commands.command(aliases=settings.command_config.aliases.ping)
    @commands.guild_only()
    async def _ping(self, ctx):
        main_logger.command('ping', ctx)
        if settings.command_config.is_visible.ping:
            await ctx.send(f"pong ⏱ {round(self.bot.latency * 1000)}ms")




def setup(bot):
    bot.add_cog(testing(bot))
