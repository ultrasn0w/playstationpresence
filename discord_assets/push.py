# Adapted from https://github.com/Tustin/PlayStationDiscord-Games/blob/master/discord_push.py
import base64
from discord_assets.client import AssetClient

icon_dir = ".local/game_icons"

def push_assets(config, supported_games):
    if len(supported_games) == 0:
        print('no games saved')
        exit(1)
    
    client = AssetClient(config['discordClientId'], config['discordToken'])

    print(f'found {len(supported_games)} supported games in games.yaml')

    discord_assets = client.get_assets()
    discord_asset_names = set(n['name'] for n in discord_assets if n['name'] != 'ps5_main') # dont remove the main icon
    print(f'found {len(discord_assets)} discord assets')
    if len(discord_assets) > 0:
        # games that have a discord asset that are no longer supported by this repo
        removed_games = [ i for i in discord_asset_names if i.upper() not in supported_games ]
        if len(removed_games) > 0:
            print(f'removing {len(removed_games)} game(s)')
            for game in removed_games:
                asset_id = next(i for i in discord_assets if i['name'] == game)['id']
                try:
                    client.delete_asset(asset_id)
                    print(f'deleted {asset_id}')
                except:
                    print(f'failed deleting {asset_id}')
        else:
            print('no games need to be removed')
    else:
        print('no discord assets found so none were removed')

    # games that are now supported that don't exist in the discord application
    added_games = [ i for i in supported_games if i.lower() not in discord_asset_names ]
    if len(added_games) > 0:
        print('adding %d game(s)...' % len(added_games))
        for game in added_games:
            with open(f'{icon_dir}/{game}.png', "rb") as image_file:
                try:
                    encoded_string = base64.b64encode(image_file.read())
                    client.add_asset(game, f'data:image/png;base64,{encoded_string.decode("utf-8")}')
                    print(f'added {game}')
                except:
                    print(f'request failed while trying to add {game}')
    else:
        print('no new games added')