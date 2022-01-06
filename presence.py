import argparse
import os

from playstationpresence.playstationpresence import PlaystationPresence

def main():
    pspresence = PlaystationPresence()

    pspresence.mainloop(notifier=None)

if __name__ == "__main__":
    main()