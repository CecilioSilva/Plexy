import logging
import os
from logging.handlers import RotatingFileHandler
from Commands.settings import Settings
import datetime


class Logger(logging.Logger):
    def __init__(self):
        super().__init__(__name__)
        self.settings = Settings()
        self.setLevel(self.settings.general_config.log_level)
        log_formatter = logging.Formatter(self.settings.general_config.log_format)
        self.date = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")


        if not os.path.exists("data/logs/"):
            os.makedirs("data/logs/")

        file_handler = RotatingFileHandler(f"data/logs/plexy_{self.date}.log", mode='a', maxBytes=50000000, backupCount=5)
        file_handler.setFormatter(log_formatter)
        self.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        self.addHandler(console_handler)

    def command(self, command: str, ctx):
        self.info(f"{command} command by {ctx.author.name}#{ctx.author.discriminator}")


main_logger = Logger()
