from discord.embeds import Embed
from plexapi.server import PlexServer
from Commands.settings import Settings
import discord
from Commands.logger import main_logger
import urllib.parse


class PlexConnection(PlexServer):

    def __init__(self):
        self.__bot_settings = Settings()
        self.__base_url = self.__bot_settings.secrets.plexBaseUrl
        self.__plex_token = self.__bot_settings.secrets.plexToken
        self.__content_url = self.__bot_settings.secrets.contentUrl
        self.__scan_libraries = self.__bot_settings.plex_config.scanLibraries

        
        if not self.__base_url:
            raise Exception("plexBaseUrl")
        elif not self.__plex_token:
            raise Exception("plexToken")
        elif not self.__content_url:
            raise Exception("contentUrl")
        else:
            try:
                super().__init__(self.__base_url, self.__plex_token)
                self.title = self.friendlyName
                self.server_name = self.friendlyName
            except Exception as e:
                main_logger.error(f"Failed plex api connection")
                raise e


    def get_new_content(self) -> list:
        new_content = list()
        main_logger.info('Getting new Content')
        try:
            for library in self.__scan_libraries:

                recently_added = [Content(self, content) for content in self.library.section(library).recentlyAdded(maxresults=40)]

                # Sorts the list of recently_added items by name and index (Example Show01e02)
                recently_added.sort(key=lambda sort_func: str(sort_func.title) + str(sort_func.index))
                seen = set()
                # Adds library list of new content to overall new content list
                # Checks if multiple of a show got added (Aka season) and filters them out
                # so there wont be 10 messages if you add 10 new episodes of a show

                new_content.extend([content for content in recently_added if content.title not in seen and not seen.add(content.title)])
            return new_content
        except Exception as e:
            main_logger.error(f"Exception in getting new content: {e}")
            return new_content

    def get_all_in_library(self, lib):
        main_logger.debug(f"Got all from: {lib}")
        return self.library.section(lib).all()




class Content:
    def __init__(self, plex_connection: PlexConnection, content, send: bool = False) -> None:
        self.content = content
        self.plex_connection = plex_connection
        self.type = self.content.type
        self.library = self.content.librarySectionTitle
        self.key = self.content.key
        self.send = 1 if send else 0
        self.settings = Settings()
        self.image_link = Embed.Empty

        if self.content.type == "episode":
            self.index = self.content.seasonEpisode
            self.title = self.content.grandparentTitle


            if self.content.parentThumb and not self.settings.general_config.safe_mode:
                self.image_link = f"{self.settings.secrets.plexBaseUrl}{self.content.parentThumb}?X-Plex-Token={self.settings.secrets.plexToken}"
        else:
            self.index = self.content.type.capitalize()
            self.title = self.content.title

            if not self.settings.general_config.safe_mode:
                self.image_link = self.content.thumbUrl

        self.content_link = self._get_content_link()
        main_logger.debug(f"Content -> {self.__repr__()}")

    def _get_content_link(self) -> str:
        return f"{self.settings.secrets.contentUrl}details?key={self.content.key}&context=library%3Acontent.library"



    def __repr__(self):
        return f"<Content:{self.title}-{self.index}>"


class ContentEmbed(discord.Embed):
    def __init__(self, content):
        super().__init__()
        self.settings = Settings()

        self.title = content.title
        self.description = content.content.summary if content.content.summary else discord.Embed.Empty
        self.color = self.settings.style_config.newContentEmbedColor
        self.content = content

        if self.settings.general_config.safe_mode:
            self.url = f"https://app.plex.tv/desktop/#!/search?query={urllib.parse.quote(content.title)}"
        else:
            self.url = self.content.content_link

        self.set_author(name="Plexy", icon_url=self.settings.style_config.iconLink, url=self.url)
        self.set_thumbnail(url=self.content.image_link)
        self.set_fields()
        main_logger.debug(self.__repr__())

    def set_fields(self):
        self.add_field(name="Type", value=self.content.library.capitalize(), inline=True)

        if self.content.type == "show":
            self.add_field(name="Episodes", value=str(
                len(self.content.content.episodes())), inline=True)

    def first_page(self):
        self.description = discord.Embed.Empty
        self.set_thumbnail(url=discord.Embed.Empty)
        self.set_image(url=self.content.image_link)
        self.set_footer(text="Next page for summary", icon_url=discord.Embed.Empty)
        return self

    def second_page(self):
        self.description = self.content.content.summary
        self.set_thumbnail(url=self.content.image_link)
        self.set_footer(text=discord.Embed.Empty, icon_url=discord.Embed.Empty)
        return self

    def get_pages(self):
        pages = [self.first_page(), ContentEmbed(self.content).second_page()]
        main_logger.debug(pages)
        return pages

    def __repr__(self):
        return f"<ContentEmbed:{self.content.type.capitalize()}/{self.content.title}>"
