"""
Pseudocode

get 99th percentile average response time
if average time > max_response_time
    scale up by ceil(response_percentile - max_response_time)/ 2000 (n processes for n users)
elif average time < min_response_time
    scale down by floor(response_percentile - min_response_time)/ 2000 (n processes for n users) 
    as long as scale>0 (cant have 0 services)
    
Parameters

max_response_time = 5000.0
min_response_time = 3000.0

Explanation
in an ideal schenario (1 user per user) the response time is around 2000-2100ms max, thus in
an optimal schenario, the response time would be less than 3000ms and we would be safe to scale
down.
we went for a maximum response time of 5000ms as that means that the app is pretty overloaded 
with more than 3 users per worker.
we also constrain that the minimum number of replicas must be 1 as we must have at least one
replica of the service 
"""

import socket
import docker
from math import ceil, floor
import matplotlib.pyplot as plt
max_response_time = 5000.0
min_response_time = 3000.0
HOST = socket.gethostbyname(socket.gethostname())
DATA_SIZE = 64
PORT = 65000
web_app_name = 'app_name_web'
client = docker.from_env()
web_app = client.services.get(web_app_name)
if __name__ == "__main__":
    active_services = web_app.attrs["Spec"]["Mode"]["Replicated"]["Replicas"]
    print("Started {} services)".format(active_services))
    fig, ax = plt.subplots()
    ax.set_title('Number of Services')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Number of Services')

    times = [0]
    services = [active_services]
    ax.plot(times, services)
    response_range = max_response_time - min_response_time
    active_services = web_app.attrs["Spec"]["Mode"]["Replicated"]["Replicas"]

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            client_socket, client_address = server_socket.accept()
            with client_socket:
                response_percentile = float(client_socket.recv(DATA_SIZE).decode())
                print("Received " + str(response_percentile))
                if response_percentile > max_response_time:
                    to_add = ceil((response_percentile - max_response_time) / response_range)
                    replicas = active_services + to_add
                    web_app.update(mode={'Replicated': {'Replicas': int(replicas)}})
                    web_app = client.services.get(web_app_name)
                elif response_percentile < min_response_time:
                    to_add = floor((response_percentile - min_response_time) / response_range)
                    if (active_services + to_add) > 0:
                        replicas = active_services + to_add
                        web_app.update(mode={'Replicated': {'Replicas': int(replicas)}})
                        web_app = client.services.get(web_app_name)
                active_services = web_app.attrs["Spec"]["Mode"]["Replicated"]["Replicas"]
                times.append(times[-1] + 10)
                services.append(active_services)
                ax.plot(times, services, color='blue')
                plt.savefig("plot.png")
                plt.pause(0.01)