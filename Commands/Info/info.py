from discord.ext import commands
import discord
from collections import Counter
from Commands.logger import main_logger
from Commands.plex import PlexConnection, Content
import datetime
import json
from itertools import groupby
from Commands.settings import Settings
from os.path import exists

starting_time = datetime.datetime.now()
settings = Settings()


async def send_error_message(ctx, error):
    main_logger.error(f"{__name__} {error}")
    await ctx.send(f"An error has occurred 😖: {error}", delete_after=5)
    await ctx.message.delete(delay=5)


class SupportEmbed(discord.Embed):
    def __init__(self):
        super().__init__()
        self.title = "Support the developer"
        self.set_thumbnail(url="https://i.imgur.com/sxfp0vX.png")
        self.description = "[Buy me a Coffee](https://ko-fi.com/gamingismyfood)\n[Github Repo](https://github.com/CecilioSilva/Plexy)"
        self.color = 0xf207ff
        self.set_author(
            name="Made by: Gamingismyfood",
            url="https://github.com/CecilioSilva",
            icon_url="https://avatars.githubusercontent.com/u/61215183?v=4"
        )

    def __repr__(self):
        return f'<Support Embed: https://github.com/CecilioSilva>'


class NotiEmbed(discord.Embed):
    def __init__(self, title=discord.Embed.Empty, description=discord.Embed.Empty, color=None, author=True, thumbnail=None):
        super().__init__()
        self.title = title
        self.description = description
        self.color = settings.style_config.defaultEmbedColor if not color else color

        if author:
            self.set_author(name="Plexy", icon_url=settings.style_config.iconLink,
                            url="https://github.com/CecilioSilva/Plexy")
        if thumbnail:
            self.set_thumbnail(url=thumbnail)

    def __repr__(self):
        return f'<NotiEmbed: {self.title} >'


class InfoEmbed(discord.Embed):
    def __init__(self, plex_con, all_libs):
        super().__init__()

        self.title = "Info"
        self.description = "Plex Server Info"
        self.color = settings.style_config.helpEmbedColor
        self.all_libs = all_libs

        self.set_author(name="Plexy", icon_url=settings.style_config.iconLink,
                        url="https://github.com/CecilioSilva/Plexy")
        self.plex_con = plex_con

        if self.plex_con:
            self.add_field(
                name="Server:", value=f"{self.plex_con.title}:  🟢", inline=False)
            self.set_all_fields()
        else:
            self.add_field(name="Server:", value=f"Offline:  🔴", inline=False)

        self.set_footer(text=f'Version: 6.0',
                        icon_url=settings.style_config.iconLink)
        self.set_thumbnail(url=settings.style_config.infoThumbLink)
        self.add_field(
            name="Uptime:", value=datetime.datetime.now() - starting_time)

        main_logger.debug(f"{self} {self.description}")

    def set_all_fields(self):
        all_content = self.plex_con.library.all()

        types = [content.type for content in all_content]
        library_stats = [content.section().title for content in all_content]

        general_value = ""
        all_count = 0

        # Gets the content amount of different content types
        result = Counter(types)
        for key, value in result.items():
            all_count += value
            general_value += f"{key.capitalize()}: **{value}**\n"
        general_value += f"Total: **{all_count}**\n"
        self.add_field(name="General:", value=general_value, inline=False)

        # Gets the amount of content per library
        libraries_value = ""
        result = Counter(library_stats)

        libraries_to_scan = settings.plex_config.allLibraries if self.all_libs else settings.plex_config.scanLibraries

        for key, value in result.items():
            if key in libraries_to_scan:
                libraries_value += f"{key}: **{value}**\n"
        self.add_field(name="Libraries:", value=libraries_value, inline=False)

    def __repr__(self):
        return f'<Info Embed: uptime: {datetime.datetime.now() - starting_time}>'


class HelpEmbed(discord.Embed):
    def __init__(self, arg=None):
        super().__init__()
        self.title = "Help"
        self.description = f"Prefix: **`{' | '.join(list(settings.general_config.prefix))}`**"
        self.color = settings.style_config.helpEmbedColor

        self.set_author(
            name="Plexy", icon_url=settings.style_config.iconLink, url="https://github.com/CecilioSilva/Plexy")

        self.set_footer(
            text=f"Made by: Gamingismyfood", icon_url=settings.style_config.iconLink)

        # Specific help message
        if arg:
            self.title = discord.Embed.Empty
            self.description = discord.Embed.Empty

        if exists('configs/help_config.json'):
            # Reads help file
            with open('configs/help_config.json', 'r') as help_file:
                data = help_file.read()
            for i in json.loads(data):
                string = ''
                for j in i['content']:
                    # Added command with quotes and description to field
                    string += f"`{j}`: {i['content'][j]}\n"
                # Adds commands aliases to field
                string += f'*aliases*: ***{" | ".join([f"`{alias}`" for alias in i["aliases"]])}***\n'

                # If command is hidden don't show it in help except if the all help is asked
                if not arg:
                    self.add_field(
                        name=i['field'].capitalize(), value=string, inline=False)
                else:

                    # if help for certain command is asked
                    if getattr(settings.command_config.aliases, arg.lower(), False):
                        if i['field'] == arg.lower():
                            self.add_field(
                                name=i['field'].capitalize(), value=string, inline=False)
                            self.add_field(name="Description",
                                           value=i['description'], inline=False)
                            break
                    else:
                        self.add_field(
                            name=i['field'].capitalize(), value=string, inline=False)
        else:
            self.add_field(
                name='Error', value="No Help file found", inline=False)

    def __repr__(self):
        return f"<Help Embed {settings.general_config.prefix}>"


def summary_embed(plex_con):
    """Summary embed method"""
    new_content: list[Content] = plex_con.get_new_content()

    # Sorts all rows by title
    categories = [list(g)
                  for k, g in groupby(new_content, key=lambda x: x.type)]
    embeds = list()
    for content in categories:
        content.reverse()
        # Top newest additions
        titles = [(cont.title, cont.library)
                  for cont in content[:settings.command_config.settings.max_summary_amount]]

        title = f"Recently Added {content[0].library}:"
        description = '\n'.join(
            [f'• {val[0]} - {val[1]}' for val in titles])
        embeds.append(NotiEmbed(
            title=title,
            description=description,
            author=False,
            color=settings.style_config.newContentEmbedColor
        ))
    return embeds


class info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(rate=1, per=30, type=commands.BucketType.member)
    @commands.command(aliases=settings.command_config.aliases.info)
    async def _info_command(self, ctx, arg1=None):
        main_logger.command('info', ctx)
        if settings.command_config.is_visible.info:
            try:
                plex_con = PlexConnection()
            except Exception as e:
                await send_error_message(ctx, e)
                plex_con = False

            async with ctx.typing():
                info_embed = InfoEmbed(plex_con, all_libs=arg1 == "-a")

            await ctx.send(embed=info_embed)
            main_logger.info(f'Send: {repr(info_embed)}')

    @commands.command(name="help")
    async def _help(self, ctx, arg=None):
        main_logger.command('help', ctx)
        if not arg:
            await ctx.author.send(embed=HelpEmbed())
            embed = NotiEmbed(title=f"Send help message to:",
                              description=f"{ctx.author.name}#{ctx.author.discriminator}")
            main_logger.info(f'Send private: {repr(embed)}')
            ctx.send(embed=embed, delete_after=10)
            return
        elif arg == "-c":
            embed = HelpEmbed()
        else:
            embed = HelpEmbed(arg=arg)

        await ctx.send(embed=embed)
        main_logger.info(f'Send: {repr(embed)}')

    @commands.command(aliases=settings.command_config.aliases.summary)
    async def _summary(self, ctx):
        main_logger.command('summary', ctx)
        try:
            plex_con = PlexConnection()
        except Exception as e:
            await send_error_message(ctx, e)
            return

        if settings.command_config.is_visible.summary:
            await ctx.send("**Newest additions to the Plex server:**")
            async with ctx.typing():
                summary_embeds = summary_embed(plex_con)

            for embed in summary_embeds:
                await ctx.send(embed=embed)
                main_logger.info(f'Send: {repr(embed)}')

    @commands.cooldown(rate=1, per=30, type=commands.BucketType.member)
    @commands.command(aliases=settings.command_config.aliases.libraries)
    async def _libraries(self, ctx, arg=None):
        main_logger.command('libraries', ctx)
        if settings.command_config.is_visible.libraries:

            try:
                plex_con = PlexConnection()
            except Exception as e:
                await send_error_message(ctx, e)
                return

            libraries = plex_con.library.sections()
            if arg == "-a":
                desc = "\n".join(
                    [f"• **{lib.title}** - `{lib.totalSize}`" for lib in libraries])
            else:
                scan_libs = settings.plex_config.scanLibraries
                desc = "\n".join(
                    [f"• **{lib.title}** - `{lib.totalSize}`" for lib in libraries if lib.title in scan_libs])

            embed = NotiEmbed(title=f"Libraries:", description=desc)
            await ctx.send(embed=embed)
            main_logger.info(f'Send: {repr(embed)}')

    @commands.command(aliases=['support', 'sup', 'hero', 'dev'])
    async def _support(self, ctx):
        main_logger.command('support', ctx)
        embed = SupportEmbed()
        await ctx.send(embed=embed)
        main_logger.info(f'Send: {repr(embed)}')


def setup(bot):
    bot.add_cog(info(bot))
