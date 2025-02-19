import platform
import configparser
import os
import pathlib

rootPath = str(pathlib.Path(__file__).parent.absolute())

class Parameters:
    config = configparser.ConfigParser()
    configPath = os.path.join(rootPath, '../config.ini')
    config.read(configPath)

    SENDER_MAIL = config['general']['sender_email']
    RECEIVER_MAIL = config['general']['receiver_email']
    APP_PASSWORD = config['general']['app_password']

    NORMAL = 0
    RICH = 1
    FULL = 2
    verbosity = int(config['debug']['verbosity'])

    sw_version = "v1.0"
