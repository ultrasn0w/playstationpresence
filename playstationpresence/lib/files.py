import yaml

__CONFIG_PATH = ".local/config.yaml"
__GAMES_PATH = ".local/games.yaml"
__IGNORED_TITLES_PATH = ".local/ignored_titles.yaml"

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

def load_config():
    return __read_file(__CONFIG_PATH)

def save_config(config):
    __write_file(config, __CONFIG_PATH)

def load_ignored_titles():
    return __read_file(__IGNORED_TITLES_PATH)