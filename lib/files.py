import yaml

_CONFIG_PATH = ".local/config.yaml"
_GAMES_PATH = ".local/.config.yaml"

def load_game_data():
    with open(_GAMES_PATH) as games_file:  
        return yaml.safe_load(games_file)

def save_game_data(game_data):
    with open(_GAMES_PATH, 'w+') as games_file:
        yaml.dump(game_data, games_file)

def load_config():
    with open(_CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def save_config(config):
    with open(_CONFIG_PATH, 'w+') as f:
        yaml.dump(config, f)