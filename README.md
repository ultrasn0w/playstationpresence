# playstationpresence

This is a fork of [playstationpresence](https://github.com/cadewey/playstationpresence), which itself is a fork of the original [playstationpresence](https://github.com/elsorino/playstationpresence) and a fork of the tooling from [PlayStationDiscord-Games](https://github.com/Tustin/PlayStationDiscord-Games).

So since this is a fork of a fork, I copied over the information of the original projects here:

- Original [playstationpresence](https://github.com/elsorino/playstationpresence), a python
app that syncs your PlayStation game status with Discord
- A fork of the tooling from [PlayStationDiscord-Games](https://github.com/Tustin/PlayStationDiscord-Games),
which is used to collect game icons and push them to Discord as app assets

# Differences and why I forked a fork

The fork of cadewey workes great, thank you very much for sharing your work.
But unfortunately all my physically owned games were not included in the fetched games (PSN API `[...]operationName=getPurchasedGameList[...]`) to pregenerate the game icons as discord assets.
 
I took a look at his code and got inspired to the idea "Why not fetch and generate the assets using the information what is currently played?". 
So I started to exactly implement that and here we are.

- Automatically fetch and upload assets of currently played game
- See differences of [playstationpresence](https://github.com/cadewey/playstationpresence) by cadewey to the original [playstationpresence](https://github.com/elsorino/playstationpresence) by elsorino.


# How to use

For now see README by cadewey at [playstationpresence](https://github.com/cadewey/playstationpresence)
