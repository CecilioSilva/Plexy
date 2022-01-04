from Commands.plex import PlexConnection, Content
from Commands.settings import Settings
from Commands.logger import main_logger
import sqlite3
import itertools
import discord




class EmbedContent:
    def __init__(self, type: str, library: str, key: str, season_episode: str, title: str, thumbnail: str):
        self.type = type
        self.library = library
        self.key = key
        self.season_episode = season_episode
        self.thumbnail = thumbnail
        self.title = title


class NewContent:

    def __init__(self):
        self.plex_con = PlexConnection()
        self.settings = Settings()
        self.first_scan = True

        self.db_con = sqlite3.connect(f"data/content_database.sqlite")
        self._create_db_table()

    def _insert_content(self, content: EmbedContent):
        if self.settings.general_config.safe_mode:
            url = "https://www.plex.tv/"
        else:
            url = f"{self.settings.secrets.contentUrl}details?key={content.key}&context=library%3Acontent.library"
        cursor_obj = self.db_con.cursor()
        cursor_obj.execute(
            'INSERT INTO Content(type, library, key, season_episode, title, image, content_link) VALUES(?, ?, ?, ?, ?, ?, ?)',
            [content.type, content.library, content.key, content.season_episode, content.title, content.thumbnail, url])
        self.db_con.commit()
        main_logger.debug(f"Added content {content.title} - {content.season_episode} to database")

    def _recently_added(self):
        recently_added_movies: list[EmbedContent] = list()
        recently_added_episodes: list[EmbedContent] = list()

        for lib in self.settings.plex_config.scanLibraries:
            lib_type = self.plex_con.library.section(lib).type
            if lib_type == "movie":
                for content in self.plex_con.library.section(lib).recentlyAdded(maxresults=self.settings.plex_config.max_recently_added):
                    if self.settings.general_config.safe_mode:
                        thumburl = self.settings.style_config.defaultThumbLink
                    else:
                        thumburl = str(content.thumbUrl)

                    movie_embed_content = EmbedContent(
                        type=content.type,
                        library=content.librarySectionTitle,
                        key=content.key,
                        season_episode=None,
                        title=content.title,
                        thumbnail=thumburl
                    )

                    recently_added_movies.append(movie_embed_content)

            elif lib_type == "show":
                for content in self.plex_con.library.section(lib).recentlyAddedEpisodes(maxresults=self.settings.plex_config.max_recently_added):
                    if self.settings.general_config.safe_mode:
                        thumburl = self.settings.style_config.defaultThumbLink
                    else:
                        thumburl = f"{self.settings.secrets.plexBaseUrl}{content.grandparentThumb}?X-Plex-Token={self.settings.secrets.plexToken}"

                    show_embed_content = EmbedContent(
                        type=content.type,
                        library=content.librarySectionTitle,
                        key=content.key,
                        season_episode=content.seasonEpisode,
                        title=content.grandparentTitle,
                        thumbnail=thumburl
                    )
                    recently_added_episodes.append(show_embed_content)

        newly_added_episodes = list()
        for key, group in itertools.groupby(recently_added_episodes, lambda x: x.title):
            newly_added_episodes.append(list(group)[0])

        return recently_added_movies + newly_added_episodes

    def _create_db_table(self):
        try:
            db_cursor = self.db_con.cursor()
            db_cursor.execute("CREATE TABLE content(id INTEGER PRIMARY KEY, type VARCHAR, library VARCHAR, key VARCHAR, season_episode VARCHAR, title VARCHAR, image VARCHAR, content_link VARCHAR)")
            self.db_con.commit()
        except sqlite3.OperationalError:
            main_logger.debug('Database exists')
            self.first_scan = False

    def _get_new_recently_added(self):
        self.recently_added_content = self._recently_added()
        db_cur = self.db_con.cursor()
        db_cur.execute('SELECT title,season_episode FROM content')
        db_rows = db_cur.fetchall()

        new_content = list()
        for content in self.recently_added_content:
            if not (content.title, content.season_episode) in db_rows:
                new_content.append(content)

        for content in new_content:
            self._insert_content(content)
        return new_content

    def _create_embed(self, content: EmbedContent):
        embed = discord.Embed(color=self.settings.style_config.newContentEmbedColor)
        embed.title = f"Newly added {content.library}:"
        embed.description = content.title

        if self.settings.general_config.safe_mode:
            embed.url = "https://www.plex.tv/"
        else:
            embed.url = f"{self.settings.secrets.contentUrl}details?key={content.key}&context=library%3Acontent.library"

        embed.set_image(url=content.thumbnail if content.thumbnail else self.settings.style_config.defaultThumbLink)

        if content.type == "episode":
            embed.add_field(name="Episode", value=content.season_episode.split("e")[1], inline=False)
            embed.set_footer(text=content.season_episode.upper().replace("S", f"{content.library} - Season: ").replace("E", " - Episode: ", 1))

        elif content.type == "movie":
            embed.add_field(name="Type", value="Movie", inline=False)
            embed.set_footer(text="Movie")
        return embed

    def _get_content_embeds(self):
        new_content = self._get_new_recently_added()
        embed_list = list()
        for content in new_content:
            embed_list.append(self._create_embed(content))
        return embed_list

    async def send(self, client):
        channel = client.get_channel(self.settings.secrets.notificationsChannelId)
        if not self.first_scan:
            for embed in self._get_content_embeds()[:30]:
                main_logger.info(f'Send new content embed: {embed.title}')
                await channel.send(embed=embed)
