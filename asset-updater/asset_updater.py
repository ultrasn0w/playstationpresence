#!/usr/bin/env python3
import argparse
import json
import os
import requests
import shutil
import sys
import time
import yaml

from discord_push import push_assets
from urllib.parse import urlparse, parse_qs

icon_dir = ".local/game_icons"
ps_graph_api = "https://web.np.playstation.com/api/graphql/v1/op"

# Anything we don't care to push assets for (e.g. streaming apps, artbooks, etc)
# since the library page doesn't seem to let us filter out non-games and such.
def load_config():
    with open("../.local/config.yaml", 'r') as f:
        return yaml.safe_load(f)

def save_config(config):
    with open("../.local/config.yaml", 'w+') as f:
        yaml.dump(config, f)

def get_purchased_games(config):
    variables = {
        "isActive": True,
        "platform": [ "ps4","ps5" ],
        "size": 50,
        "start": 0,
        "sortBy": "productName",
        "sortDirection": "asc",
        "subscriptionService": "NONE"
    }

    extensions = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": "2c045408b0a4d0264bb5a3edfed4efd49fb4749cf8d216be9043768adff905e2"
        }
    }

    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        'authority': 'web.np.playstation.com',
        'authorization': f'Bearer {get_access_token(config)}',
        'content-type': 'application/json',
        'origin': 'https://library.playstation.com',
        'referer': 'https://library.playstation.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.18 Safari/537.36 Edg/93.0.961.11'
    }

    url = f'{ps_graph_api}?operationName=getPurchasedGameList&variables={json.dumps(variables)}&extensions={json.dumps(extensions)}'
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

def get_oauth_code(npsso):
    params = {
        'access_type' : 'offline',
        'app_context' : 'inapp_ios',
        'auth_ver' : 'v3',
        'cid' : '60351282-8C5F-4D5E-9033-E48FEA973E11',
        'client_id' : 'ac8d161a-d966-4728-b0ea-ffec22f69edc',
        'darkmode' : 'true',
        'device_base_font_size' : 10,
        'device_profile' : 'mobile',
        'duid' : '0000000d0004008088347AA0C79542D3B656EBB51CE3EBE1',
        'elements_visibility' : 'no_aclink',
        'no_captcha' : 'true',
        'redirect_uri' : 'com.playstation.PlayStationApp://redirect',
        'response_type' : 'code',
        'scope' : 'psn:mobile.v1 psn:clientapp',
        'service_entity' : 'urn:service-entity:psn',
        'service_logo' : 'ps',
        'smcid' : 'psapp:settings-entrance',
        'support_scheme' : 'sneiprls',
        'token_format' : 'jwt',
        'ui' : 'pr'
    }

    headers = {
        'cookie': f'npsso={npsso}'
    }

    query_string = "&".join([f"{k}={v}" for k,v in params.items()])

    response = requests.get(f"https://ca.account.sony.com/api/authz/v3/oauth/authorize?{query_string}", headers=headers, allow_redirects=False)
    return parse_qs(urlparse(response.headers.get('Location')).query)['code']

def get_refresh_token(oauth_code, config):
    data = {
        'smcid' : 'psapp%3Asettings-entrance',
        'access_type' : 'offline',
        'code' : oauth_code,
        'service_logo' : 'ps',
        'ui' : 'pr',
        'elements_visibility' : 'no_aclink',
        'redirect_uri' : 'com.playstation.PlayStationApp://redirect',
        'support_scheme' : 'sneiprls',
        'grant_type' : 'authorization_code',
        'darkmode' : 'true',
        'device_base_font_size' : 10,
        'device_profile' : 'mobile',
        'app_context' : 'inapp_ios',
        'token_format' : 'jwt'
    }

    headers = {
        'authorization': 'Basic YWM4ZDE2MWEtZDk2Ni00NzI4LWIwZWEtZmZlYzIyZjY5ZWRjOkRFaXhFcVhYQ2RYZHdqMHY=',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post("https://ca.account.sony.com/api/authz/v3/oauth/token", data=data, headers=headers, allow_redirects=False)
    j = response.json()

    config["refresh_token"] = j["refresh_token"]
    config["refresh_token_expires_in"] = time.time() + j["refresh_token_expires_in"]

def get_access_token(config):

    data = {
        'refresh_token': config["refresh_token"],
        'grant_type': 'refresh_token',
        'scope': 'psn:clientapp psn:mobile.v1',
        'token_format': 'jwt'
    }

    auth_header = {
        'Authorization': 'Basic YWM4ZDE2MWEtZDk2Ni00NzI4LWIwZWEtZmZlYzIyZjY5ZWRjOkRFaXhFcVhYQ2RYZHdqMHY='
    }

    response = requests.post("https://ca.account.sony.com/api/authz/v3/oauth/token", data=data, headers=auth_header)

    return response.json()['access_token']

def build_game_library(config):
    print("Retrieving game library...")

    data = get_purchased_games(config)
    ignored_titles = config['ignored_titles']
    
    # Some games may not appear as "purchased" because they are, e.g., pack-ins (like Astro's Playroom).
    # Initialize the library with these games to make sure they're included in the asset gathering process.
    library = {
        "ps5": {
            "ASTRO's PLAYROOM": {
                "name": "ASTRO's PLAYROOM",
                "titleId": "PPSA01325_00",
                "image": "https://image.api.playstation.com/vulcan/ap/rnd/202010/2012/T3h5aafdjR8k7GJAG82832De.png"
            }
        },
        "ps4": { }
    }

    for game in data['data']['purchasedTitlesRetrieve']['games']:
        if game['titleId'] in ignored_titles:
            continue

        if game['platform'].lower() == "ps4":
            # If we find a PS4 title we already saw on PS5, ignore the PS4 version
            if game['name'] in library['ps5']:
                continue
        elif game['platform'].lower() == "ps5":
            # If we find a PS5 title we already saw on PS4, delete the PS4 record
            if game['name'] in library['ps4']:
                del(library['ps4'][game['name']])

        library[game['platform'].lower()][game['name']] = {
            'name': game['name'],
            'titleId': game['titleId'],
            'image': game['image']['url']
        }

    print(f"Found {len(library['ps4']) + len(library['ps5'])} games in library")
    
    return library
    
def retrieve_game_icons(library):
    if len(library['ps4']) == 0 and len(library['ps5']) == 0:
        return

    if os.path.exists(icon_dir):
        shutil.rmtree(icon_dir)
		
    os.mkdir(icon_dir)

    for game in { **library['ps4'], **library['ps5'] }.values():
        print(f"Downloading image for {game['name']} ({game['titleId']})")
        output_file = f"{icon_dir}/{game['titleId']}.png"
        with requests.get(game['image'], stream=True) as r:
            with open(output_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

def write_games_yaml(library):
    print("Writing ../.local/games.yaml...")

    # Strip out the image URLs before we write to disk; the presence client doesn't need them
    game_data = \
        [{k: item[k] for k in item if k != "image"} for item in library['ps5'].values()] + \
        [{k: item[k] for k in item if k != "image"} for item in library['ps4'].values()]

    with open('../.local/games.yaml', 'w+') as games_file:
        yaml.dump(game_data, games_file)

def generate(args):
    config = load_config()
    library = build_game_library(config)

    if not args.skip_icons:
        retrieve_game_icons(library)

    write_games_yaml(library)

def login(args):
    config = load_config()
    oauth_code = get_oauth_code(config["npsso"])
    get_refresh_token(oauth_code, config)
    save_config(config)

def push(args):
    config = load_config()
    push_assets(config)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", title="Available commands", metavar="")

    generate_command = subparsers.add_parser("generate", help="Build library, download icons, and write games.json")
    generate_command.add_argument("--skip-icons", help="Skip icon download step", action="store_true")
    generate_command.set_defaults(func=generate)

    push_command = subparsers.add_parser("push", help="Push assets to Discord")
    push_command.set_defaults(func=push)

    login_command = subparsers.add_parser("login", help="Log in to PSN")
    login_command.set_defaults(func=login)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()