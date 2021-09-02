import yaml

def load_game_data():
    with open('../.local/games.yaml') as games_file:  
        return yaml.safe_load(games_file)

def save_game_data(game_data):
    with open('../.local/games.yaml', 'w+') as games_file:
        yaml.dump(game_data, games_file)

def load_config():
    with open("../.local/config.yaml", "r") as f:
        return yaml.safe_load(f)

def save_config(config):
    with open("../.local/config.yaml", 'w+') as f:
        yaml.dump(config, f)