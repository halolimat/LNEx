# LNExAPI - Server

LNExAPI Server extends the usefulness of the Location Name Extraction tool ([LNEx](#)) so that it can handle requests from clients over HTTP. LNExAPI Server uses in-memory caching to speedup extraction of locations from text. 

### Startup and Setup

Once `vagrant up` has been issued on the host 2 docker containers should be created. You can SSH into them with `vagrant ssh LNEx-api` and `vagrant ssh LNEx-redis`. LNEx-api is the container containing the code for the LNExAPI Server. When you SSH into the LNEx-api container you will land in the /root directory. This directory contains some important scripts to start and manage the server.

* startAPI - This script will start the LNExAPI Server.
* killAPI - This script will kill the LNExAPI Server.
* LNExCLI - This script provides functions to create and manage users and other aspects of the service. Type `./LNExCLI help` for more information.
* startSafetyCheck - This script starts a safety check service to ensure the health of the API
* killSafetyCheck - This script will kill the safety check service

To create a user and activate them please issue the following commands:
```
./LNExCLI create user <name> <email>
./LNExCLI activate user <name>
```

### Logs 

Logs for the LNExAPI Server can be found within the LNEx-api container under /var/log/LNEx.log.

### LNExAPI-Deployment

[Back to main Readme](README.md)