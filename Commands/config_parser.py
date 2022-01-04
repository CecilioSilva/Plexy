import json


class Config:
    def __init__(self, config_location: str):
        """Main Config Parser

        :param config_location: Location of the config file
        """
        self.config_location = config_location


    def __getitem__(self, item):
        """Actively get a config value"""
        try:
            with open(self.config_location) as f:
                self.data = json.load(f)

            return self.data.get(item)
        except Exception as e:
            raise e
