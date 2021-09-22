from playstationpresence.dataclasses.config import Config
import marshmallow_dataclass
import sys
import yaml

from playstationpresence.dataclasses.config import Config

if not getattr(sys, 'frozen', False):
    __CONFIG_PATH = ".local/config.yaml"
    __GAMES_PATH = ".local/games.yaml"
else:
    __CONFIG_PATH = "config.yaml"
    __GAMES_PATH = "games.yaml"

__IGNORED_TITLES_PATH = ".local/ignored_titles.yaml"

__config_schema = marshmallow_dataclass.class_schema(Config)()

def __read_file(file):
    with open(file, "r") as f:
        return yaml.safe_load(f)

def __write_file(data, file):
    with open(file, "w+") as f:
        yaml.dump(data, f)

def load_game_data():
    return __read_file(__GAMES_PATH)

def save_game_data(game_data):
    __write_file(game_data, __GAMES_PATH)

def load_config() -> Config:
    return __config_schema.load(__read_file(__CONFIG_PATH))

def save_config(config: Config):
    __write_file(__config_schema.dump(config), __CONFIG_PATH)

def load_ignored_titles():
    return __read_file(__IGNORED_TITLES_PATH)