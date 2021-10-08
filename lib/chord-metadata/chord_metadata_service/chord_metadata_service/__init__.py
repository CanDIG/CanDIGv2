#!/usr/bin/env python3

import configparser
import os

from . import metadata
from . import patients


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), "package.cfg"))


name = config["package"]["name"]
__version__ = config["package"]["version"]
__all__ = ["name", "__version__", "metadata", "patients"]
