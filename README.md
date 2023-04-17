ECE 422: Reliable and Secure Systems Design 
=============
### Authors:
Kyle Bricker - kbricker  
Ashutosh Lamba - alamba  

-------------
This repository provides the starter kit for the Reliability project. The `docker-images` folder
contains the Dockerfile, a simple application in `Python` and a requirement file including dependencies for
the application. This directory is for your information and reference as the image (simpleweb) has already been built and pushed to [Docker Hub](https://hub.docker.com/r/zhijiewang22/simpleweb) repository.

The following steps show how you can prepare the deployment environment on Cybera Cloud; briefly, you need to a) provision 
Virtual Machines (VMs) on Cybera b) install Docker on VMs c) create a Swarm cluster of at least two of 
VMs and d) deploy a web application on the Swarm cluster as microservices.

Also, this repository contains a base implementation of an HTTP client program that may be customized or extended 
according to your needs. 

Initial steps for accomplishing your project:   

1. Create 3 VMs on Cybera cloud with the following specifications:

    1. Use `Ubuntu 18.04` or `Ubuntu 20.04` as the image for all VMs.

    2. You need one of these VMs to run the client program for which you may use `m1.small` flavor. Let's call this VM as
the `Client_VM`.

    3. For the other two VMs, please still consider `m1.small` flavor. These two VMs will construct your Swarm cluster.

    4. You need to open the following TCP ports in the `default security group` in Cybera:
        - 22 (ssh), 2376 and 2377 (Swarm), 5000 (Visualization), 8000 (webapp), 6379 (Redis)
        - You can do this on Cybera by going to `Network` menu and `Security Groups`. ([See Here](./figures/sg.png))

2. On the `Client_VM` run
    ```bash
    $ sudo apt -y install python-pip
    $ pip install requests
    $ pip install locust
    ```

3. Then, you need to install *Docker*, pip and the reqired modules on VMs that constitute your Swarm Cluster. Run the following on each node.
    ```bash
    $ sudo apt update
    $ sudo apt -y install docker.io
    $ sudo apt -y install python-pip
    $ pip install matplotlib
    $ pip install docker
    ```
    
4. Now that Docker is installed on the two VMs, you will create the Swarm cluster.
    1. For the VM that you want to be your Swarm Manger run:
    ```bash
    $ sudo docker swarm init
    ```

    2. The above `init` command will produce something like the bellow command that you need to run on all worker nodes.
    ```bash
    $ docker swarm join \
        --token xxxxxxxxxxxxxxxxxx \
        swarm_manager_ip:2377
    ```
    3. Above command attaches your worker to the Swarm cluster.
5. On your Swarm manager, download the docker-compose.yml file:
    ```bash
    $ wget https://raw.githubusercontent.com/zhijiewang22/ECE422-Proj2-StartKit/master/docker-compose.yml
    ```
6. Run the following to deploy your application:
    ```bash
    $ sudo docker stack deploy --compose-file docker-compose.yml app_name
    ```
    1. after deployment you can run the auto_scaler.py to automatically scale the application, this is available at https://github.com/ECE422-kyle-ash/project2/blob/master/auto_scaler.py, again you must have access
    2. run the auto_scaler using the command:
    ```bash
    $ python3 auto_scaler.py
    ```

7. Your deployed application should include three microservices:
    1. A visualization microservice that is used to visualize the Swarm cluster nodes and the running microservices. 
        - Open `http://swarm_manager_ip:5000` in your browser. Note that you should have the Cybera VPN client 
    running in order to see the page. ([Sample](./figures/vis.png))
    2. A web application that is linked to a Redis datastore. This simple application shows the number that it has 
    been visited and the period that took it to solve a hard problem. 
        - Open `http://swarm_manager_ip:8000` to see the web application. Try to refresh the page. You should see the hitting number increase one by one and also the computation time change each time. ([Sample](./figures/app.png))
    3. A Redis microservice which in fact doesn't do anything fancy but return the number of hitting.

8. Now, login into your `Client_VM` and download the locust client program:
    The file is available at https://github.com/ECE422-kyle-ash/project2/blob/master/locustfile.py, you would need access to the private repository to download it.

9. Then run the client program using the command
    ```bash
    $ locust run
    ```
    1. you can go to http://10.2.5.226:8089/ to view the dashboard, do note that for a different machine you would have to replace the ip with your VM's ip in the code and the link (also make sure the port is open).
    2. you can use the GUI to edit the number of users making requests and view the requests, users and response time graphs.
    3. If you increase the number of users or decrease the think time, ie increasing the workload, the response 
    time should increase.
    4. **Important Note**: for development and testing purposes you may run the client program on your laptop 
    which is a reasonable strategy. However, running the client program for a long time on your laptop might appear as 
    a DoS attack to Cybera firewall which may result in unexpected outcomes for your VMs. Therefore, try to run the 
    http client program on the `Client_VM`.
    
    
 Good Luck!
