
import asyncio
import snapcast.control

import yaml

import logging

import time

# Init logging
def create_logger():
    logger = logging.getLogger(__name__)
    c_handler = logging.StreamHandler()
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

    c_handler.setLevel(logging.INFO)
    c_handler.setFormatter(c_format)

    logger.addHandler(c_handler)

    logger.setLevel(logging.INFO)
    return logger

# Init constants
FRIENDLY_NAME = 'friendly_name'
STATUS = 'status'

STREAMS_KEY = 'streams'
HOST_KEY = 'host'
PORT_KEY = 'port'
PULL_INTERVALL_KEY = 'pull_intervall'

PLAYING_STATUS = 'playing'
IDLE_STATUS = 'idle'


def read_config(conf='./config.yml'):
    with open(conf) as file:
        config = yaml.load(file, Loader = yaml.FullLoader)
    return config
        
def get_group_ids():
    global server
    group_ids = []
    for group in server.groups:
        group_ids.append(group.identifier)
    return group_ids

def get_streams(server, watched_streams):
    streams = {}
    for stream in server.streams:
        if (stream.friendly_name in watched_streams):
            stream_dict = {}
            stream_dict[FRIENDLY_NAME] = stream.friendly_name
            stream_dict[STATUS] = stream.status
        
            streams[stream.name] = stream_dict
    return streams


def group_clients(group_id, clients):
    try:
        loop.run_until_complete(server.group_clients(group_id,clients))
    except Exception as e:
        logger.warning(e)

def configure_devices(stream_name, config):
    logger.info("Stream to configure:" + stream_name)
    stream_config = config['streams'][stream_name]
    clients = stream_config['clients']
    group_id = get_group_ids()[0]
    group_clients(group_id, clients)
    logger.info("Set clients" + str(clients) + " to group " + group_id)
    loop.run_until_complete(server.group_stream(group_id, stream_name))
    logger.info("Set stream " + stream_name + "on group " + group_id)
    
    
def handle_stream_change(streams, old_streams, config):
    for name in streams:
        stream = streams[name]
        status = stream[STATUS]
        old_status = old_streams[name][STATUS] if name in old_streams else IDLE_STATUS
        if (status==PLAYING_STATUS):
            if (status!=old_status):
                logger.info("Stream " + stream[FRIENDLY_NAME] + " changed to playing")
                configure_devices(name, config)

def create_server_state(server, config):
    watched_streams = config[STREAMS_KEY]
    state = {}
    streams = get_streams(server, watched_streams)
    state[STREAMS_KEY] = streams
    return state
    

def main(config):
    global server
    global old_state
    # Listen for stream changes:
    SERVER = config[HOST_KEY]
    PORT = config[PORT_KEY]
    logger.info("Watching server " + SERVER + ":" + str(PORT))
    ii=0
    while True:
        server = loop.run_until_complete(snapcast.control.create_server(loop, SERVER, reconnect=True))
        state = create_server_state(server, config)
        handle_stream_change(state[STREAMS_KEY], old_state[STREAMS_KEY], config)
        time.sleep(config[PULL_INTERVALL_KEY])
        old_state = dict(state)

# Init previous state variable
old_state = {}
old_state[STREAMS_KEY] = {}

loop = asyncio.get_event_loop()
logger = create_logger()
config = read_config()
main(config)

