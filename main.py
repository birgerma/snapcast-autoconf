
import asyncio
import snapcast.control

SERVER = '192.168.1.175'

loop = asyncio.get_event_loop()

old_server = loop.run_until_complete(snapcast.control.create_server(loop, SERVER, reconnect=True))

old_state = {}
old_state['streams'] = {}

import yaml
def read_config(conf='./config.yml'):
    with open(conf) as file:
        config = yaml.load(file, Loader = yaml.FullLoader)
    return config
        
def stream_to_string(stream):
    # return "Id:" + stream.identifier + " Name:" + stream.friendly_name + " Status:" + stream.status
    return "Name:" + stream.friendly_name + " Status:" + stream.status

def client_to_string(client):
    groupName = client.group.friendly_name
    return  "Id:" + client.identifier + " Name:" + client.friendly_name + " Group:" + groupName

def print_clients():
    for client in server.clients:
        # print(dir(client))
        # print(client.friendly_name)
        print(client_to_string(client))
        # print(client.group.stream)
        print('---------------')

# print_clients()

def print_streams(server):
    # print("Print streams")
    for stream in server.streams:
        # print(dir(stream))
        print(stream_to_string(stream))
        # print(stream)
        # print(stream.meta)
        # print(client.group.stream)
        print('---------------')

def get_group_ids():
    global server
    group_ids = []
    for group in server.groups:
        # print(group.identifier, group.clients)
        group_ids.append(group.identifier)
    return group_ids

def callback():
    print("Something changed")

def get_streams(server, watched_streams):
    streams = {}
    # print("watched streams:", watched_streams)
    for stream in server.streams:
        # print('get_streams', stream.friendly_name, (name in watched_streams))
        if (stream.friendly_name in watched_streams):
            stream_dict = {}
            stream_dict['friendly_name'] = stream.friendly_name
            stream_dict['status'] = stream.status
        
            streams[stream.name] = stream_dict
    return streams


def group_clients(group_id, clients):
    try:
        loop.run_until_complete(server.group_clients(group_id,clients))
    except Exception as e:
        print("Error:", e)

def configure_devices(stream_name, config):
    print("Stream to configure:", stream_name)
    stream_config = config['streams'][stream_name]
    print(stream_config)
    clients = stream_config['clients']
    # response = server.group_clients(5, clients)
    group_id = get_group_ids()[0]
    group_clients(group_id, clients)
    print("Groupind", clients, "in group", group_id)

    loop.run_until_complete(server.group_stream(group_id, stream_name))
    print("Set stream", stream_name, "on group", group_id)
    
    
def handle_stream_change(streams, old_streams, config):
    # print('Check status change:')
    for name in streams:
        stream = streams[name]
        status = stream['status']
        old_status = 'idle'
        if (status=='playing'):
            if(name in old_streams):
                old_status = old_streams[name]['status']
            if (status!=old_status):
                # print(stream.friendly_name, status, old_status )
                print(stream['friendly_name'], status, old_status)
                print("Has started to play!!!")
                configure_devices(name, config)

def create_server_state(server, config):
    watched_streams = config['streams']
    state = {}
    streams = get_streams(server, watched_streams)

    state['streams'] = streams
    return state
    
import time
def main(config):
    global server
    global old_state
    # Listen for stream changes:
    ii=0
    while ii<100:
        server = loop.run_until_complete(snapcast.control.create_server(loop, SERVER, reconnect=True))
        state = create_server_state(server, config)
        # print(state)
        # changes = get_stream_changes(old_server, old_server)
        # print("Changes:", changes)
        handle_stream_change(state['streams'], old_state['streams'], config)
        # old_server = server
        time.sleep(2)
        old_state = dict(state)
        # status = server.status()
        # server.synchronize(status)
        ii+=1
        print(ii)

config = read_config()
main(config)
# server = loop.run_until_complete(snapcast.control.create_server(loop, SERVER, reconnect=True))



# group_ids = get_group_ids()
# loop.run_until_complete(server.group_clients('1', ['xps13']))
# server.group_clients('8622f487-9faa-2fa6-c937-da38c09d2538', ['xps13'])
# group_id = group_ids[0]
# group_id = 'new'
# group_id = '4dcc4e3b-c699-a04b-7f0c-8260d23c43e1'
# clients = ["xps13", 'rasp-stereo']
# clients = ["xps13"]
# print('Move', clients, 'to', group_id)
# try:
#     loop.run_until_complete(server.group_clients(group_id,clients))
# except Exception as e:
#     print("Error:", e)
#     pass
# print("New group configuration")
# get_group_ids()

# stream_ids = []
# for stream in server.streams:
#     print(stream, stream.identifier)
#     stream_ids.append(stream.identifier)

# stream_id = stream_ids[0]
# print(stream_id)

# server.group_stream(group_id, stream_id)


# import threading
# my_lock = threading.Lock()
# # event = threading.Event()
# server.set_on_update_callback(callback)
# # event.wait()
# while True:
#     with my_lock:
#         pass
# print_streams()

# print(dir(server))
# print()
# print(dir(server.status()))
# print(server.status())
# print(config)
print("Done")
