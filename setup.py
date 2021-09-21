from setuptools import setup
import py2exe, sys, os

setup(
    data_files= [
        (".", ["./logo.ico", "./.local/config.yaml", "./.local/games.yaml"])
    ],
    options = {
        'py2exe': {
            'bundle_files': 1,
            'compressed': False,
            'excludes': ["difflib", "doctest", "pdb",
                         "pickle", "unittest", "tcl", "tkinter"]
        }
    },
    windows = [
        {
            'script': "presence.py",
            'icon_resources': [(1, "logo.ico")],
            'dest_base': "playstationpresence"
        }
    ],
    zipfile = None
)