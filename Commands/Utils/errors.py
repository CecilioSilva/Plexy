from discord.ext import commands
from Commands.logger import main_logger
import traceback



class ErrorHandler(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            message = f"This command is on cool-down. Please try again after {round(error.retry_after, 1)} seconds."
        elif isinstance(error, commands.MissingPermissions):
            message = "You are missing the required permissions to run this command!"
        elif isinstance(error, commands.MissingRequiredArgument):
            message = f"Missing a required argument: {error.param}"
        elif isinstance(error, commands.ConversionError):
            message = str(error)
        elif isinstance(error, commands.CommandNotFound):
            message = f"Command: `{ctx.message.content}` does not exist!"
        else:
            message = "Oh no! Something went wrong while running the command!"

        main_logger.error(error)
        traceback.print_exception(type(error), error, error.__traceback__)

        await ctx.send(message, delete_after=5)
        await ctx.message.delete(delay=5)


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
