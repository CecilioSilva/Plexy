from typing import List
from Commands.config_parser import Config
import os
import shutil


def move(source: str, dest: str):
    if os.path.exists(dest):
        os.remove(dest)
    shutil.copyfile(source, dest)


class StyleConfig:
    def __init__(self, json: dict):
        self.iconLink: str = json.get('iconLink')
        self.defaultThumbLink: str = json.get('defaultThumbLink')
        self.loadingImgLink: str = json.get('loadingImgLink')
        self.requestImgLink: str = json.get('requestImgLink')
        self.infoThumbLink: str = json.get('infoThumbLink')
        self.defaultEmbedColor = eval(json.get('defaultEmbedColor').replace("#", "0x"))
        self.helpEmbedColor = eval(json.get('helpEmbedColor').replace("#", "0x"))
        self.newContentEmbedColor = eval(json.get('newContentEmbedColor').replace("#", "0x"))


class PlexConfig:
    def __init__(self, json: dict):
        self.refreshTime: int = int(json.get('refreshTime'))
        self.scanLibraries: List[str] = json.get('scanLibraries')
        self.allLibraries: List[str] = json.get('allLibraries')
        self.max_recently_added: int = json.get('max-recently-added')


class GeneralConfig:
    def __init__(self, json: dict):
        self.prefix: List[str] = json.get('prefix')
        self.safe_mode: bool = json.get('safe-mode')
        self.log_level: str = json.get('log-level')
        self.log_format: str = json.get('log-format')
        self.backup_hour_interval: int = json.get('backup-hour-interval')


class CommandConfig:
    class __Aliases:
        def __init__(self, json: dict):
            self.ping: List[str] = json.get('ping')
            self.info: List[str] = json.get('info')
            self.summary: List[str] = json.get('summary')
            self.search: List[str] = json.get('search')
            self.random: List[str] = json.get('random')
            self.request: List[str] = json.get('request')
            self.report: List[str] = json.get('report')
            self.dashboard: List[str] = json.get('dashboard')
            self.libraries: List[str] = json.get('libraries')
            self.flags: List[str] = json.get('flags')


    class __IsEnabled:
        def __init__(self, json: dict):
            self.help: bool = json.get('help')
            self.ping: bool = json.get('ping')
            self.info: bool = json.get('info')
            self.summary: bool = json.get('summary')
            self.search: bool = json.get('search')
            self.random: bool = json.get('random')
            self.request: bool = json.get('request')
            self.report: bool = json.get('report')
            self.dashboard: bool = json.get('dashboard')
            self.libraries: bool = json.get('libraries')
            self.flags: bool = json.get('flags')


    class __CommandSettings:
        def __init__(self, json: dict):
            self.max_random_amount: int = json.get('max-random-amount')
            self.max_search_amount: int = json.get('max-search-amount')
            self.max_summary_amount: int = json.get('max-summary-amount')
            self.max_embed_amount: int = json.get('max-embed-amount')


    class __Cooldowns:
        def __init__(self, json: dict) -> None:
            self.help: int = json.get('help')
            self.ping: int = json.get('ping')
            self.info: int = json.get('info')
            self.summary: int = json.get('summary')
            self.search: int = json.get('search')
            self.random: int = json.get('random')
            self.request: int = json.get('request')
            self.report: int = json.get('report')
            self.dashboard: int = json.get('dashboard')
            self.libraries: int = json.get('libraries')
            self.flags: int = json.get('flags')


    def __init__(self, json: dict):
        self.aliases = self.__Aliases(json.get('aliases'))
        self.is_visible = self.__IsEnabled(json.get('is_enabled'))
        self.settings = self.__CommandSettings(json.get('settings'))
        self.cooldowns = self.__Cooldowns(json.get('cooldowns'))
        self.args: dict[str, List[str]] = json.get('args')


class Secrets:
    def __init__(self, json: dict):
        self.bot_token: str = json['bot_token']
        self.notificationsChannelId: int = json['notificationsChannelId']
        self.plexAdminDiscordId: int = json['plexAdminDiscordId']
        self.plexBaseUrl: str = json['plexBaseUrl']
        self.plexToken: str = json['plexToken']
        self.contentUrl: str = json['contentUrl']


class Settings:
    def __init__(self):
        self.config_path = 'configs/config.json'
        self.secrets_path = 'configs/secrets.json'
        self.help_path = 'configs/help_config.json'
        self.database_path = 'data/content_database.sqlite'

        self.__config: Config = Config(self.config_path)
        self.__secrets: Config = Config(self.secrets_path)

        self.plex_config = PlexConfig(self.__config['plex_config'])
        self.general_config = GeneralConfig(self.__config['general_config'])
        self.style_config = StyleConfig(self.__config['style_config'])
        self.command_config = CommandConfig(self.__config['command_config'])
        self.secrets = Secrets(self.__secrets)

    def is_valid(self):
        return os.path.exists(self.config_path) and os.path.exists(self.secrets_path)

    def backup(self):
        if not os.path.exists("data/backup/"):
            os.makedirs('data/backup/')

        move(self.config_path, 'data/backup/backup_config.json')
        move(self.secrets_path, 'data/backup/backup_secrets.json')
        move(self.help_path, 'data/backup/backup_help_config.json')
        move(self.database_path, 'data/backup/backup_content_database.sqlite')