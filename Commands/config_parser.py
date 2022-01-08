import json


class Config:
    def __init__(self, config_location: str):
        self.config_location = config_location


    def __getitem__(self, item):
        try:
            with open(self.config_location) as f:
                self.data = json.load(f)

            return self.data.get(item)
        except Exception as e:
            raise e
