"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

Edited by: Shruti Kar, shruti@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

import json, os
import unicodedata
import numpy as np
from bottle import route, run, template,get,post,request
import datetime
import LNEx as lnex
import dateutil.parser

################################################################################
################################################################################

def strip_non_ascii(s):
    if isinstance(s, unicode):
        nfkd = unicodedata.normalize('NFKD', s)
        return str(nfkd.encode('ASCII', 'ignore').decode('ASCII'))
    else:
        return s

################################################################################

def read_tweets():

    tweets_file = "_Data/sample_tweets.txt"

    # read tweets from file to list
    with open(tweets_file) as f:
        tweets = f.read().splitlines()

    return tweets

################################################################################

def init_using_files():

    with open("_Data/Houston_geo_locations.json") as f:
        geo_locations = json.load(f)

    with open("_Data/Houston_geo_info.json") as f:
        geo_info = json.load(f)

    with open("_Data/Houston_extended_words3.json") as f:
        extended_words3 = json.load(f)

    lnex.initialize_using_files(geo_locations, extended_words3)

    return geo_info

################################################################################

def init_using_elasticindex():

    lnex.elasticindex(conn_string='localhost:9200', index_name="photon")

    # Houston flood bounding box
    bb = [29.390551,-96.289673,30.121373,-94.437103]

    return lnex.initialize(bb, augment=True)

################################################################################

def get_all_tweets_and_annotations(gaz_name):

    with open("_Data/Houston_annotations_with_time.json".replace('\r\n','')) as f:
        data = json.load(f,strict=False)

    all_tweets_and_annotations = list()
    keys=list()
    
    for k, x in data.iteritems():

        toponyms_and_indexes = list()

        text = x["text"]
	keys.append(k)
	time=x["created_at"]
        #print x
	for key, y in x.iteritems():

            # ignore the field which has the tweet text
            if key != "text":
		if key !="created_at":
                	start_idx = int(y["start_idx"])
                	end_idx = int(y["end_idx"])

                	toponyms_and_indexes.append((y["type"], (start_idx,end_idx)))

        all_tweets_and_annotations.append((text, toponyms_and_indexes,k,time))
    
    return all_tweets_and_annotations

def prepare_geo_points(gaz_name, geo_info):

    all_geo_points = list()
    #keys,tw=get_all_tweets_and_annotations(gaz_name.title())

    for tweet in get_all_tweets_and_annotations(gaz_name.title()):
	
        for ln in lnex.extract(tweet[0]):

            if ln[0].lower() == gaz_name.lower():
                continue

            ln_offsets = ln[1]

            geoinfo = [geo_info[x] for x in ln[3]]

            if len(geoinfo) == 0:
                continue

            for geopoint in geoinfo:

                lat = geopoint["geo_item"]["point"]["lat"]
                lon = geopoint["geo_item"]["point"]["lon"]

                marked_tweet = tweet[0][:ln_offsets[0]] + "<mark>" + tweet[0][ln_offsets[0]:ln_offsets[1]] + "</mark>" + tweet[0][ln_offsets[1]:]

                try:
                    description = """   <table>
                                            <tr>
                                                <td colspan="2">marked_tweet</td>
                                            </tr>
                                        </table> """

                    description = description.replace("marked_tweet", marked_tweet)

                    marker_icon = "marker"

                    all_geo_points.append({"type": "Feature", "geometry": {"type": "Point","coordinates": [lon, lat]}, "properties": { "description": description, "icon": marker_icon},"id":tweet[2],"timestamp":tweet[3]})

                except Exception as e:
                    print e
                    print "ERROR:>>> ", marked_tweet
                    exit()

                #all_geo_points.append(str(lat)+","+str(lon))

    return {"type": "FeatureCollection", "features": all_geo_points}

################################################################################

def create_map(data_str, centroid):

    type = "heat"
    type = "clusteredPoints"
    
    if type == "clusteredPoints":
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset='utf-8' />
            <title></title>
            <meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
            <script src='https://api.tiles.mapbox.com/mapbox-gl-js/v0.32.1/mapbox-gl.js'></script>
            <link href='https://api.tiles.mapbox.com/mapbox-gl-js/v0.32.1/mapbox-gl.css' rel='stylesheet' />
            <style>
                body { margin:0; padding:0; }
                #map { position:absolute; top:0; bottom:0; width:100%; }
            </style>
        </head>
        <body>
        <style>
            .mapboxgl-popup {
                max-width: 400px;
                font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
            }
        </style>
        <div id='map'></div>
        <script>
        mapboxgl.accessToken = 'pk.eyJ1IjoiaGFsb2xpbWF0IiwiYSI6ImNpbGwzbmdoajVtcTR0c2twdXlhd2U0YngifQ.9ToQIL6EuHciG7WWOZu-Mw';
        var map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/dark-v9',
            center: ["""+",".join(str(e) for e in centroid)+"""],
            zoom: 5
        });
        map.on('load', function() {
            // Add a new source from our GeoJSON data and set the
            // 'cluster' option to true.
            map.addSource("earthquakes", {
                type: "geojson",
                // Point to GeoJSON data. This example visualizes all M1.0+ earthquakes
                // from 12/22/15 to 1/21/16 as logged by USGS' Earthquake hazards program.
                data: """+data_str+""",
                cluster: true,
                clusterMaxZoom: 14, // Max zoom to cluster points on
                clusterRadius: 50 // Radius of each cluster when clustering points (defaults to 50)
            });
            // Use the earthquakes source to create five layers:
            // One for unclustered points, three for each cluster category,
            // and one for cluster labels.
            map.addLayer({
                "id": "unclustered-points",
                "type": "symbol",
                "source": "earthquakes",
                "filter": ["!has", "point_count"],
                "layout": {
                    "icon-image": "marker-15"
                }
            });
            // Display the earthquake data in three layers, each filtered to a range of
            // count values. Each range gets a different fill color.
            var layers = [
                [150, '#f28cb1'],
                [20, '#f1f075'],
                [0, '#51bbd6']
            ];
            layers.forEach(function (layer, i) {
                map.addLayer({
                    "id": "cluster-" + i,
                    "type": "circle",
                    "source": "earthquakes",
                    "paint": {
                        "circle-color": layer[1],
                        "circle-radius": 18
                    },
                    "filter": i === 0 ?
                        [">=", "point_count", layer[0]] :
                        ["all",
                            [">=", "point_count", layer[0]],
                            ["<", "point_count", layers[i - 1][0]]]
                });
            });
            // Add a layer for the clusters' count labels
            map.addLayer({
                "id": "cluster-count",
                "type": "symbol",
                "source": "earthquakes",
                "layout": {
                    "text-field": "{point_count}",
                    "text-font": [
                        "DIN Offc Pro Medium",
                        "Arial Unicode MS Bold"
                    ],
                    "text-size": 12
                }
            });
        });
        // When a click event occurs near a place, open a popup at the location of
        // the feature, with description HTML from its properties.
        map.on('click', function (e) {
            var features = map.queryRenderedFeatures(e.point, { layers: ['unclustered-points'] });
            if (!features.length) {
                return;
            }
            var feature = features[0];
            // Populate the popup and set its coordinates
            // based on the feature found.
            var popup = new mapboxgl.Popup()
                .setLngLat(feature.geometry.coordinates)
                .setHTML(feature.properties.description)
                .addTo(map);
        });
        // Use the same approach as above to indicate that the symbols are clickable
        // by changing the cursor style to 'pointer'.
        map.on('mousemove', function (e) {
            var features = map.queryRenderedFeatures(e.point, { layers: ['unclustered-points'] });
            map.getCanvas().style.cursor = (features.length) ? 'pointer' : '';
        });
        </script>
        </body>
        </html>
        """


    return """

        <!DOCTYPE html>
        <html>
        <head>
            <meta charset='utf-8' />
            <title></title>
            <meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
            <script src='https://api.tiles.mapbox.com/mapbox-gl-js/v0.32.1/mapbox-gl.js'></script>
            <link href='https://api.tiles.mapbox.com/mapbox-gl-js/v0.32.1/mapbox-gl.css' rel='stylesheet' />
            <style>
                body { margin:0; padding:0; }
                #map { position:absolute; top:0; bottom:0; width:100%; }
            </style>
        </head>
        <body>

        <div id='map'></div>

        <script>
        mapboxgl.accessToken = 'pk.eyJ1IjoiaGFsb2xpbWF0IiwiYSI6ImNpbGwzbmdoajVtcTR0c2twdXlhd2U0YngifQ.9ToQIL6EuHciG7WWOZu-Mw';
        var map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/dark-v9',
            center: ["""+",".join(str(e) for e in centroid)+"""],
            zoom: 5
        });

        map.on('load', function() {

            // Add a new source from our GeoJSON data and set the
            // 'cluster' option to true.
            map.addSource("earthquakes", {
                type: "geojson",
                // Point to GeoJSON data. This example visualizes all M1.0+ earthquakes
                // from 12/22/15 to 1/21/16 as logged by USGS' Earthquake hazards program.
                data: """+data_str+""",
                cluster: true,
                clusterMaxZoom: 15, // Max zoom to cluster points on
                clusterRadius: 20 // Use small cluster radius for the heatmap look
            });

            // Use the earthquakes source to create four layers:
            // three for each cluster category, and one for unclustered points

            // Each point range gets a different fill color.
            var layers = [
                [0, 'green'],
                [20, 'orange'],
                [200, 'red']
            ];

            layers.forEach(function (layer, i) {
                map.addLayer({
                    "id": "cluster-" + i,
                    "type": "circle",
                    "source": "earthquakes",
                    "paint": {
                        "circle-color": layer[1],
                        "circle-radius": 70,
                        "circle-blur": 1 // blur the circles to get a heatmap look
                    },
                    "filter": i === layers.length - 1 ?
                        [">=", "point_count", layer[0]] :
                        ["all",
                            [">=", "point_count", layer[0]],
                            ["<", "point_count", layers[i + 1][0]]]
                }, 'waterway-label');
            });

            map.addLayer({
                "id": "unclustered-points",
                "type": "circle",
                "source": "earthquakes",
                "paint": {
                    "circle-color": 'rgba(0,255,0,0.5)',
                    "circle-radius": 20,
                    "circle-blur": 1
                },
                "filter": ["!=", "cluster", true]
            }, 'waterway-label');
        });
        </script>
        </body>
        </html>

        """
@route('/<gaz_name>',method='GET')
def index(gaz_name):
    return '''
	<form action="/map" method="post">
    		Start year-month-date hour:min:sec :<input name="start_range" type="text"/>
		End year-month-date hour:min:sec :<input name="end_range" type="text"/>
		Dataset:<input name="dataset" type="text"/>
		<input value="submit" type="submit" />
	</form>
	'''

@route('/map',method='POST')
def _index():

    date1=request.forms.get('start_range')
    date2=request.forms.get('end_range')
    gaz_name=str(request.forms.get('dataset'))
    print date1,date2

    if gaz_name not in ["chennai", "Houston"]:

        options = """

        Try:

        <p><a href="http://130.108.85.187:8080/houston">Houston</a></p>
        <p><a href="http://130.108.85.187:8080/chennai">Chennai</a></p>

        """

        return options
    with open("_Data/"+gaz_name+"_all_geo_points.json") as f:
  	data = json.load(f)


    new_file=list()
    lons = list()
    lats = list()
    marker_icon = "marker"

    for x in data["features"]:



		t=str(datetime.datetime.fromtimestamp(x["timestamp"]/ 1000.0))

		parsed1=dateutil.parser.parse(date1)
		parsed2=dateutil.parser.parse(date2)
		parsedt=dateutil.parser.parse(t)

		if parsed1<=parsedt<=parsed2:
			new_file.append({"type": "Feature", "geometry": {"type": "Point","coordinates": [x["geometry"]["coordinates"][0],x["geometry"]["coordinates"][1]]}, "properties": { "description": x["properties"]["description"], "icon": marker_icon}})

			lons.append(x["geometry"]["coordinates"][0])
			lats.append(x["geometry"]["coordinates"][1])



    centroid = [np.average(lons), np.average(lats)]
    new_data_str={"type": "FeatureCollection", "features": new_file}
    data_str = str(json.dumps(new_data_str))
    return create_map(data_str, centroid)


################################################################################

def prepare_data():

    #geo_info = init_using_files()
    geo_info = init_using_elasticindex()

    all_geo_points = prepare_geo_points("Houston", geo_info)

    with open("_Data/Houston_all_geo_points.json", "w") as f:
        json.dump(all_geo_points, f)

if __name__ == "__main__":

    prepare_data()

    run(host='0.0.0.0', port=8080)
