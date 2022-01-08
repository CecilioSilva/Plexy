from urllib3.exceptions import NewConnectionError

from Commands.settings import Settings
from Commands.Plex.content import NewContent
from Commands.logger import main_logger
from discord.ext import commands, tasks
import discord



main_logger.info("Bot Starting")


intents = discord.Intents.default()
intents.members = True
settings = Settings()

cogs = [
    "Commands.Misc.testing",
    "Commands.Info.info",
    "Commands.Utils.utils",
    "Commands.Utils.errors",
]


client = commands.Bot(
    command_prefix=settings.general_config.prefix,
    help_command=None,
    intents=intents
)


is_life = True


@tasks.loop(minutes=settings.plex_config.refreshTime)
async def check_for_new_content():
    global is_life
    main_logger.info("Started Scan loop")
    try:
        await NewContent().send(client)
        if not is_life:
            await client\
                .get_channel(settings.secrets.notificationsChannelId)\
                .send('***🟢 ------------ Server Online ------------ 🟢***')
        is_life = True
    except Exception as e:
        main_logger.error('Failed scan loop')
        raise e
        if is_life:
            await client\
                .get_channel(settings.secrets.notificationsChannelId)\
                .send('***❌ ------------ Server Offline ------------ ❌***')
            is_life = False
    main_logger.info('Done Scan loop')


@tasks.loop(hours=settings.general_config.backup_hour_interval)
async def backup_task():
    main_logger.info("Started backup")
    settings.backup()
    main_logger.info("Finished backup")


@client.event
async def on_ready():
    main_logger.info(f"Bot is ready! Logged on as user {client.user}!")
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="Plex"))
    main_logger.info("Starting cog initialization:")
    for cog in cogs:
        try:
            main_logger.info(f"- Loading cog {cog}")
            client.load_extension(cog)
            main_logger.info(f"- Loaded cog {cog}")
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            main_logger.info("- Failed to load cog {}\n{}".format(cog, exc))
    main_logger.info("Done loading cogs\n")
    main_logger.info("Starting Task")
    if not settings.is_valid():
        await client.close()
        exit('No config and/or secrets file')
    check_for_new_content.start()
    backup_task.start()


client.run(settings.secrets.bot_token)
