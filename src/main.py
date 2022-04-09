import logging
import os
from typing import Dict

import paho.mqtt.properties
from paho.mqtt.packettypes import PacketTypes

from bot import telegram_bot
from cameras.camera import Camera
from cameras.camera_loader import CameraLoader
from mqtt import mqtt_client
from mqtt.mqtt_client import MqttClient
from mqtt.mqtt_topic_handler import MQTTTopicHandler
from ping import ping_service
from switches.switch import Switch
from switches.switch_loader import SwitchLoader
from utils import utils

if __name__ == '__main__':
    properties = paho.mqtt.properties.Properties(PacketTypes.Names)
    print(properties.names)
    print(properties.types)
    print(properties.properties)
    # WORKING DIRECTORY
    abspath = os.path.abspath(__file__)
    d_name = os.path.dirname(abspath)
    os.chdir(d_name)

    # INIT
    utils.init_logger()
    logger = logging.getLogger(os.path.basename(__file__))
    user_config = utils.load_yaml("../config.yaml")
    camera_types = utils.load_yaml("../camera-types.yaml")
    switch_types = utils.load_yaml("../switch_types.yaml")
    config = utils.merge_yaml_configs(user_config, camera_types)
    config = utils.merge_yaml_configs(config, switch_types)

    utils.check_configuration(config)
    logger.info("Configuration loaded")

    # SERVICES
    services: Dict = dict()

    # MQTT
    mqtt_client: MqttClient = mqtt_client.MqttClient(config)
    services["mqtt"] = mqtt_client
    utils.init_mqtt_logger(mqtt_client)

    # CAMERAS
    camera_loader = CameraLoader(config)
    camera_instances: Dict[str, Camera] = camera_loader.load_camera_instances(services)

    # SWITCHES
    switch_loader = SwitchLoader(config)
    switch_instances: Dict[str, Switch] = switch_loader.load_switch_instances(services)

    # DB
    authChatIds = dict()

    # BOT
    telegram_bot = telegram_bot.TelegramBot(config, authChatIds, camera_instances, switch_instances)
    # telegram_bot.start_web_hook()
    telegram_bot.start_polling()

    # MQTT TOPIC HANDLER
    topic_handler = MQTTTopicHandler(config, telegram_bot.utils)
    mqtt_client.set_on_connect(topic_handler.on_connect)
    mqtt_client.set_on_message(topic_handler.on_message)
    mqtt_client.connect_and_start()

    # PING SERVICE
    pingService = ping_service.PingService(telegram_bot.utils, config)
    pingService.start_service_async()

    # Reset mqtt retained messages sending empty mqtt
    # logger.error("")
