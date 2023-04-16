from locust import HttpUser, task, between, constant
from locust.env import Environment

import socket
import gevent
import matplotlib.pyplot as plt
import numpy as np

swarm_ip = '10.2.6.25'
port = 8000
response_time_port = 65000

class User(HttpUser):
    wait_time = constant(0.5)
    host = "http://" + swarm_ip + ":" + str(port)

    @task
    def get_index(self):
        self.client.get('/')

def update_data(environment: Environment):
    while True:
        response_percentile = environment.stats.get("/", "GET").get_current_response_time_percentile(99.0)
        if isinstance(response_percentile, float):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                try:
                    server_socket.connect((swarm_ip, response_time_port))
                    server_socket.send(str(response_percentile).encode())
                    print("sent "+str(response_percentile))
                except:
                    print("socket failed")
        gevent.sleep(10)
        
env = Environment(user_classes=[User])
runner = env.create_local_runner()
web_ui = env.create_web_ui("10.2.5.226", 8089)
runner.start(1,1)
gevent.spawn(update_data(env))