from discord.ext import commands
from Commands.Info.info import NotiEmbed
from Commands.plex import PlexConnection, Content, ContentEmbed
from Commands.settings import Settings
from Commands.logger import main_logger
from EZPaginator import Paginator
import random




settings = Settings()



class utils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_libraries_from_args(arg1: str, arg2: str = None, arg3: int = 1) -> tuple[list, int, str]:
        """Gets the libraries, amount, query from the command"""

        libraries_to_search = settings.command_config.args.get(arg1)

        query = arg2
        if not libraries_to_search:
            libraries_to_search = settings.plex_config.scanLibraries
            query = arg1

        if str(arg3).isnumeric():
            amount = max(1, min(int(arg3), settings.command_config.settings.max_embed_amount))
        else:
            amount = 1

        main_logger.debug(f"Libraries: {libraries_to_search}, Amount: {amount}, Query: {query}")
        return libraries_to_search, amount, query

    @staticmethod
    def random_embed(plex_con: PlexConnection, library: str, amount: int, _) -> list[ContentEmbed]:
        """Return list of random content from random library"""

        # clamps value to from 1 to max value
        amount = max(1, min(amount, settings.command_config.settings.max_random_amount))

        random_content_embeds = list()
        for _ in range(amount):
            all_in_library = plex_con.get_all_in_library(random.choice(library))
            random_content = random.choice(all_in_library)
            random_content_object = Content(plex_con, random_content)
            random_content_embeds.append(ContentEmbed(random_content_object))

        return random_content_embeds

    @staticmethod
    def search_library(plex_con: PlexConnection, params: tuple[list, int, str]):
        """Gets content by query from passed library"""
        found = list()
        libraries = params[0]
        amount = params[1]
        query = params[2]
        for library in libraries:
            try:
                results = plex_con.library.section(library).search(query)
                for result in results:
                    # if episode names need to be searched too
                    found.append(Content(plex_con, result))
            except Exception as e:
                main_logger.error(f"Exception in searching for content: {e}")

        return found[:amount]

    @staticmethod
    async def send_error_message(ctx, error: str):
        main_logger.error(f"{__name__} {error}")
        await ctx.send(f"An error has occurred 😖: {error}", delete_after=5)
        await ctx.message.delete(delay=5)

    @commands.command(aliases=Settings().command_config.aliases.search)
    @commands.has_permissions()
    async def _search(self, ctx, arg1=None, arg2=None, arg3=None):
        main_logger.command('search', ctx)
        if settings.command_config.is_visible.search:
            async with ctx.typing():
                try:
                    search_params = self.get_libraries_from_args(arg1, arg2, arg3)
                    plex_con = PlexConnection()
                except Exception as e:
                    await self.send_error_message(ctx, e)
                    return

            search_results = self.search_library(plex_con, search_params)

            search_embeds = [ContentEmbed(content) for content in search_results[:3]]

            if len(search_results) > 3:
                titles = [(cont.title, cont.library) for cont in search_results[3:]]
                title = f"Extras:"
                description = '\n'.join([f'• {val[0]} - {val[1]}' for val in titles])
                search_embeds.append(NotiEmbed(title=title, description=description, author=False))

            if len(search_embeds) > 0:
                for embed in search_embeds:
                    await ctx.send(embed=embed)
                    main_logger.info(f'Send: {repr(embed)}')
            else:
                await ctx.send(f"** Nothing Found For: `{' '.join([str(arg1),str(arg2),str(arg3)])}`**")

    @commands.command(aliases=settings.command_config.aliases.random)
    async def _random(self, ctx, arg1=None, arg2=None, arg3=None):
        main_logger.command('random', ctx)
        if settings.command_config.is_visible.random:
            try:
                arg_libs = self.get_libraries_from_args(arg1, arg2, arg3)
                plex_con = PlexConnection()
            except Exception as e:
                await self.send_error_message(ctx, e)
                return

            random_embeds = self.random_embed(plex_con, *arg_libs)
            for embed in random_embeds:
                if hasattr(embed, "get_pages"):
                    embed_list = embed.get_pages()
                    msg = await ctx.send(embed=embed_list[0])
                    await Paginator(bot=self.bot, message=msg, embeds=embed_list).start()
                else:
                    await ctx.send(embed=embed)
                main_logger.info(f'Send: {repr(embed)}')

    @commands.command(aliases=settings.command_config.aliases.request)
    async def _request(self, ctx, *, request=None):
        main_logger.command('request', ctx)
        if settings.command_config.is_visible.request:
            if not settings.secrets.plexAdminDiscordId:
                await self.send_error_message(ctx, "Plex Admin Discord Id")
            else:
                if request:
                    user = self.bot.get_user(settings.secrets.plexAdminDiscordId)
                    embed = NotiEmbed(title="📬**Request** send for:", description=f"`{request}`", thumbnail=settings.style_config.loadingImgLink)
                    await user.send(f'📬**Request** from **{ctx.author}**: {request}')
                else:
                    embed = NotiEmbed(title="No request send")

                await ctx.send(embed=embed, delete_after=10)
                await ctx.message.delete(delay=5)
                main_logger.info(f'Send: {repr(embed)}')

    @commands.command(aliases=settings.command_config.aliases.report)
    async def _report(self, ctx, *, report):
        main_logger.command('report', ctx)
        if settings.command_config.is_visible.report:
            if not settings.secrets.plexAdminDiscordId:
                await self.send_error_message(ctx, "Plex Admin Discord Id")
            else:
                if report:
                    await self.bot.get_user(settings.secrets.plexAdminDiscordId).send(f'🛑 **Report** from **{ctx.author}**: {report}')
                    embed = NotiEmbed(title="🛑 **Report** send for:", description=f"`{report}`", author=False)
                else:
                    embed = NotiEmbed(title="No report send", author=False)

                await ctx.send(embed=embed, delete_after=10)
                await ctx.message.delete(delay=5)
                main_logger.info(f'Send: {repr(embed)}')


def setup(bot):
    bot.add_cog(utils(bot))
