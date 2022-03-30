import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import yaml

logger = logging.getLogger(os.path.basename(__file__))


def start_web_hook(updater, token, ip, port, key, cert):
    updater.start_webhook(listen='0.0.0.0', port=port, url_path=token, key=key, cert=cert,
                          webhook_url='https://{}:{}/{}'.format(ip, port, token))


def init_logger():
    log_name = get_project_relative_path("app.log")
    file_handler = RotatingFileHandler(log_name, mode="w", maxBytes=100000, backupCount=1)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    file_handler.setLevel(logging.WARN)
    console_handler.setLevel(logging.INFO)
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().addHandler(file_handler)


def load_yaml(file):
    try:
        return yaml.safe_load(open(file))
    except yaml.YAMLError as e:
        print(e), sys.exit(1)


def dump_yaml(data, file):
    yaml.dump(data, open(file, 'w'), default_flow_style=False)


def merge_yaml_configs(config1, config2):
    for key, value in config2.items():
        config1[key] = value
    return config1


def get_project_relative_path(path):
    return Path.joinpath(Path(os.getcwd()).parent, path)


def check_configuration(config):
    def check_file_exists(path):
        return os.path.isfile(get_project_relative_path(path))

    telegram_network = config["telegram"]
    telegram_network_path = telegram_network["key"]
    cert_path = telegram_network["cert"]
    return check_file_exists(telegram_network_path) and check_file_exists(cert_path)
