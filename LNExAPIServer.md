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

### Endpoint Examples

* /apiv1/LNEx/initZone?key=xx&bb=[lon1,lat1,lon2,lat2]&zone=ZoneName
* /apiv1/LNEx/destroyZone?key=xx&zone=ZoneName
* /apiv1/LNEx/bulkExtract?key=xx&zone=ZoneName (Requires POST of JSON, example below)
* /apiv1/LNEx/fullBulkExtract?key=xx&zone=ZoneName (Requires POST of JSON, example below)
* /apiv1/LNEx/results?key=xx&token=yy
* /apiv1/LNEx/geoInfo?key=xx&zone=ZoneName&geoIDs=[1,2,3]
* /apiv1/LNEx/photonID?key=xx&osm_id=1
* /apiv1/LNEx/zoneReady?key=xx&zone=ZoneName

Example Request
```json
{
	"data": [
		"This is an example text",
		"This is another example of text"
	]
}
```

Actual curl examples of init zone, extracting data, and destroying zone

```sh
curl -g "http://192.168.113.2/apiv1/LNEx/initZone?key=16911b06722f6c9682&bb=[-84.5852,40.4366,-83.6201,40.9412]&zone=Lima"
curl "http://192.168.113.2/apiv1/LNEx/zoneReady?key=16911b06722f6c9682&zone=Lima"
curl -XPOST "http://192.168.113.2/apiv1/LNEx/fullBulkExtract?key=16911b06722f6c9682&zone=Lima" -H 'Content-Type: application/json' -d'{"data":["2nd street"]}'
curl "http://192.168.113.2/apiv1/LNEx/results?key=16911b06722f6c9682&token=16911b7f8ff830a8d9"
curl "http://192.168.113.2/apiv1/LNEx/destroyZone?key=16911b06722f6c9682&zone=Lima"
```

### Logs 

Logs for the LNExAPI Server can be found within the LNEx-api container under /var/log/LNEx.log.

### LNExAPI-Deployment

[Back to main Readme](README.md)