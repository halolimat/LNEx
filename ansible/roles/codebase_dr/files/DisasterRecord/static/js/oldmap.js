$(".one").addClass("animated slideInRight");
mapboxgl.accessToken =
  "pk.eyJ1Ijoic2hydXRpa2FyIiwiYSI6ImNqZWVraDN3bTFiNzgyeG1rNnlvbWU5YWEifQ.3Uq8vnAz-XUAyL4YJ60l6Q";
var map = new mapboxgl.Map({
  container: "map",
  style: "mapbox://styles/mapbox/streets-v9",
  center: centroid,
  zoom: 13,
  maxZoom: 15
});
var months = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December"
];
var layers = [[150, "#f28cb1"], [20, "#f1f075"], [0, "#51bbd6"]];
// Disable default box zooming.
$('#menu').hide();
var txt_name = "";
map.boxZoom.disable();
var layers_name = [
  "Flooded Area",
  "Shelter/Food/Supplies Need",
  "Medical/Rescue Help Need",
  "Shelter/Food/Supplies Available",
  "Medical/Rescue Help Available","start","end","route"
];
var source_names = ["trees", "shelter", "rescue", "osm_shelter", "osm_rescue"];

// Create a popup, but don't add it to the map yet.
var popup = new mapboxgl.Popup({
  closeButton: false
});

map.on("load", function() {
  $("#loadingGif").show();

  var canvas = map.getCanvasContainer();

  // Variable to hold the starting xy coordinates
  // when `mousedown` occured.
  var start;

  // Variable to hold the current xy coordinates
  // when `mousemove` or `mouseup` occurs.
  var current;

  // Variable for the draw box element.
  var box;

  var start_LtLg;
  var end_LtLg;

  // Set `true` to dispatch the event before other functions
  // call it. This is necessary for disabling the default map
  // dragging behaviour.
  canvas.addEventListener("mousedown", mouseDown, true);

  // function unsetCanv() {
  //   // canvas.addEventListener("mousedown", mouseDown, false);
  //   // map.boxZoom.enable();
  //   console.log("unset!!!");
  // }

  // Return the xy coordinates of the mouse position
  function mousePos(e) {
    var rect = canvas.getBoundingClientRect();
    return new mapboxgl.Point(
      e.clientX - rect.left - canvas.clientLeft,
      e.clientY - rect.top - canvas.clientTop
    );
  }
  map.on("mousedown", function(e) {
    start_LtLg = e.lngLat;
  });
  map.on("mouseup", function(e) {
    end_LtLg = e.lngLat;
  });
  map.on("movestart", function(e) {
    console.log("moveend");
    if (box) {
      box.parentNode.removeChild(box);
      box = null;
    }
  });

  // Drone Stuff
  map.addLayer({
      "id": "droneClip3Line",
      "type": "line",
      "source": {
          "type": "geojson",
          "data": {
              "type": "Feature",
              "properties": {},
              "geometry": {
                  "type": "LineString",
                  "coordinates": [
                    [-77.909429, 34.781765],
                    [-77.909838, 34.781679],
                    [-77.910186, 34.781380],
                    [-77.910488, 34.781072],
                    [-77.911066, 34.780527],
                    [-77.911337, 34.780270],
                    [-77.911603, 34.779988],
                    [-77.912021, 34.779515],
                    [-77.912298, 34.779197],
                    [-77.912594, 34.778949],
                    [-77.913201, 34.779174]
                  ]
              }
          }
      },
      "layout": {
          "line-join": "round",
          "line-cap": "round"
      },
      "paint": {
          "line-color": "#CF1F19",
          "line-width": 2
      }
  });

  map.addLayer({
      "id": "droneClip13Line",
      "type": "line",
      "source": {
          "type": "geojson",
          "data": {
              "type": "Feature",
              "properties": {},
              "geometry": {
                  "type": "LineString",
                  "coordinates": [
                    [-77.907635, 34.784618],
                    [-77.904276, 34.785258],
                    [-77.904150, 34.785421],
                    [-77.903778, 34.785742],
                    [-77.903326, 34.786072],
                    [-77.902979, 34.786204],
                    [-77.902862, 34.786899],
                    [-77.902320, 34.786815],
                    [-77.901409, 34.787211],
                    [-77.900925, 34.787432]
                  ]
              }
          }
      },
      "layout": {
          "line-join": "round",
          "line-cap": "round"
      },
      "paint": {
          "line-color": "#CF1F19",
          "line-width": 2
      }
  });

  map.loadImage("/static/drone.png", function(error, drone) {
    if (error) throw error;
    map.addImage("drone", drone);
    map.addLayer({
      "id": "droneClips",
      "type": "symbol",
      "source": {
        "type": "geojson",
        "data": {
          "type": "FeatureCollection",
          "features": [
            {
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [-77.911337, 34.780270]
              },
              "properties": {
                "videoURL": "http://130.108.86.152/droneVideos/003.mp4"
              }
            },
            {
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [-77.903326, 34.786072]
              },
              "properties": {
                "videoURL": "http://130.108.86.152/droneVideos/013.mp4"
              }
            }
          ]
        }
      },
      "layout": {
        "icon-image": "drone",
        "icon-size": 0.15
      }
    });
  });

  map.loadImage("/static/car.png", function(error, vehicleFound) {
    if (error) throw error;
    map.addImage("vehicleFound", vehicleFound);
    map.addLayer({
      "id": "vehiclesDetected",
      "type": "symbol",
      "source": {
        "type": "geojson",
        "data": {
          "type": "FeatureCollection",
          "features": [
            {
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [-77.910488, 34.781072]
              },
              "properties": {
                "frameURL": "http://130.108.86.152/droneFrames/003/frame360.jpg",
                "objectType": "vehicle"
              }
            },
            {
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [-77.904276, 34.785258]
              },
              "properties": {
                "frameURL": "http://130.108.86.152/droneFrames/013/frame0.jpg",
                "objectType": "vehicle"
              }
            }
          ]
        }
      },
      "layout": {
        "icon-image": "vehicleFound",
        "icon-size": 0.25
      }
    });
  });

  map.on('click', 'vehiclesDetected', function (e) {

      var frameURL = e.features[0].properties.frameURL;
      var objectType = e.features[0].properties.objectType;
      var coordinates = e.features[0].geometry.coordinates.slice();

      var tmpMSG = `
        <div style="min-width:520px;">
        A ${objectType} was detected in this frame of the drone video<br/><br/>
        <img src="${frameURL}" width="500">
        </div>
      `

      new mapboxgl.Popup()
          .setLngLat(coordinates)
          .setHTML(tmpMSG)
          .addTo(map);
  });

  map.on('click', 'droneClips', function (e) {

      var videoURL = e.features[0].properties.videoURL;
      var coordinates = e.features[0].geometry.coordinates.slice();

      var tmpMSG = `
        <div style="min-width:520px;">
        Watch the drone video<br/><br/>
        <video controls width="500">
          <source src="${videoURL}"
                  type="video/mp4">
        </video>
        </div>
      `

      new mapboxgl.Popup()
          .setLngLat(coordinates)
          .setHTML(tmpMSG)
          .addTo(map);
  });

  map.on('mousemove', "vehiclesDetected", function(e) {
    map.getCanvas().style.cursor = 'pointer';
  });

  map.on('mouseleave', "vehiclesDetected", function(e) {
    map.getCanvas().style.cursor = '';
  });

  map.on('mousemove', "droneClips", function(e) {
    map.getCanvas().style.cursor = 'pointer';
  });

  map.on('mouseleave', "droneClips", function(e) {
    map.getCanvas().style.cursor = '';
  });


  var radio = "";
  $("input[type=radio][name=user_lvl]").change(function() {
    radio = this.value;
    if (radio == "individual") {
      // $('#loadingGif').show();
      $("#picture").empty();
      $("#menu").empty();
      $("#menu").css("display", "block");
      $(".marker").remove();
      $(".r_marker").remove();
      $("#steps").css("display", "none");
      $("#agg_content").css("display", "none");

      if (box) {
        box.parentNode.removeChild(box);
        box = null;
      }


      //Shruti: Add your AJAX call here:

      $.ajax({
        url: "/test",
        success: function(res) {
          response = JSON.parse(res);
          console.log(response);

          map.addSource("trees", {
            type: "geojson",
            data: response
          });
          // add heatmap layer here
          // add circle layer here
          map.addLayer(
            {
              id: "Flooded Area",
              type: "heatmap",
              source: "trees",
              minzoom: 9,
              maxzoom: 15,
              paint: {
                // increase weight as diameter breast height increases
                "heatmap-weight": {
                  property: "dbh",
                  type: "exponential",
                  stops: [[1, 0], [62, 1]]
                },
                // increase intensity as zoom level increases
                "heatmap-intensity": {
                  stops: [[11, 1.5], [15, 1.5]]
                },
                // assign color values be applied to points depending on their density
                "heatmap-color": [
                  "interpolate",
                  ["linear"],
                  ["heatmap-density"],
                  0,
                  "rgba(117, 207, 240, 0)",
                  0.2,
                  "rgb(117, 207, 240)",
                  0.4,
                  "rgb(117, 207, 240)",
                  0.6,
                  "rgb(117, 207, 240)",
                  0.8,
                  "rgb(117, 207, 240)"
                ],
                // increase radius as zoom increases
                "heatmap-radius": 15,
                /*
              'heatmap-radius': {
                  stops: [
                      [11, 15],
                      [15, 20]
                  ]
              },*/
                // decrease opacity to transition into the circle layer
                "heatmap-opacity": {
                  default: 1,
                  stops: [[5, 1], [20, 0]]
                }
              }
            },
            "waterway-label"
          );
        }
      });

      $.ajax({
        url: "/chennai/data",
        data: {
          start_date: +$('input[name="daterange"]').data("daterangepicker")
            .startDate,
          end_date: +$('input[name="daterange"]').data("daterangepicker")
            .endDate,
          min_lat: 13.2823848224,
          min_lng: 80.066986084,
          max_lat: 12.74,
          max_lng: 80.3464508057,
          q_str: "shelter_need"
        },
        success: function(res) {
          console.log(JSON.parse(res));
          response = JSON.parse(res);
          // console.log(response['features'].length);
          map.addSource("shelter", {
            type: "geojson",
            data: response
          });
          map.loadImage("/static/shelter_need.png", function(error, sh_image) {
            if (error) throw error;
            map.addImage("si", sh_image);
            map.addLayer({
              id: "Shelter/Food/Supplies Need",
              type: "symbol",
              source: "shelter",
              layout: {
                "icon-image": "si",
                "icon-size": 0.4
              }
            });
          });
          response.features = response.features.map(function(d) {
            d.properties.uxtm = new Date(d.properties.timestamp).getTime();
            return d;
          });
        }
      });

      $.ajax({
        url: "/chennai/data",
        data: {
          start_date: +$('input[name="daterange"]').data("daterangepicker")
            .startDate,
          end_date: +$('input[name="daterange"]').data("daterangepicker")
            .endDate,
          min_lat: 13.2823848224,
          min_lng: 80.066986084,
          max_lat: 12.74,
          max_lng: 80.3464508057,
          q_str: "rescue_need"
        },
        success: function(res) {
          console.log(JSON.parse(res));
          response = JSON.parse(res);
          // console.log(response['features'].length);
          map.addSource("rescue", {
            type: "geojson",
            data: response
          });
          map.loadImage("/static/ambulance_orange.png", function(
            error,
            re_image
          ) {
            if (error) throw error;
            map.addImage("re", re_image);
            map.addLayer({
              id: "Medical/Rescue Help Need",
              type: "symbol",
              source: "rescue",
              layout: {
                "icon-image": "re",
                "icon-size": 0.08
              }
            });
          });
          response.features = response.features.map(function(d) {
            d.properties.uxtm = new Date(d.properties.timestamp).getTime();
            return d;
          });
        }
      });

      $.ajax({
        url: "/chennai/data",
        data: {
          start_date: +$('input[name="daterange"]').data("daterangepicker")
            .startDate,
          end_date: +$('input[name="daterange"]').data("daterangepicker")
            .endDate,
          min_lat: 13.2823848224,
          min_lng: 80.066986084,
          max_lat: 12.74,
          max_lng: 80.3464508057,
          q_str: "osm_shelter"
        },
        success: function(res) {
          console.log(JSON.parse(res));
          response = JSON.parse(res);
          // console.log(response['features'].length);
          map.addSource("osm_shelter", {
            type: "geojson",
            data: response
          });
          map.loadImage("/static/shelter_green.png", function(error, o_sh) {
            if (error) throw error;
            map.addImage("osh", o_sh);
            map.addLayer({
              id: "Shelter/Food/Supplies Available",
              type: "symbol",
              source: "osm_shelter",
              layout: {
                "icon-image": "osh",
                "icon-size": 0.4
              }
            });
          });
        }
      });

      $.ajax({
        url: "/chennai/data",
        data: {
          start_date: +$('input[name="daterange"]').data("daterangepicker")
            .startDate,
          end_date: +$('input[name="daterange"]').data("daterangepicker")
            .endDate,
          min_lat: 13.2823848224,
          min_lng: 80.066986084,
          max_lat: 12.74,
          max_lng: 80.3464508057,
          q_str: "osm_rescue"
        },
        success: function(res) {
          console.log(JSON.parse(res));
          response = JSON.parse(res);
          // console.log(response['features'].length);
          map.addSource("osm_rescue", {
            type: "geojson",
            data: response
          });
          map.loadImage("/static/ambulance green.png", function(error, o_re) {
            if (error) throw error;
            map.addImage("ore", o_re);
            map.addLayer({
              id: "Medical/Rescue Help Available",
              type: "symbol",
              source: "osm_rescue",
              layout: {
                "icon-image": "ore",
                "icon-size": 0.08
              }
            });
          });

          $("#loadingGif").hide();
        }
      });

      // $('#loadingGif').show();

      var pop = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false
      });

      map.on("mouseenter", "Shelter/Food/Supplies Available", function(e) {
        map.getCanvas().style.cursor = "pointer";
        var coordinates = e.features[0].geometry.coordinates.slice();
        description =
          "<table><tr><th><div class='banner-section' id='img-container' style='float:left'></div></th>";
        description +=
          "<th style='padding: 10px'>" +
          e.features[0].properties.name +
          "</th></tr></table>";
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
          coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }
        pop
          .setLngLat(coordinates)
          .setHTML(description)
          .addTo(map);
        var img = new Image();
        $.ajax({
          url: "/data",
          success: function(res) {
            response = JSON.parse(res);
            img.src =
              response[e.features[0].properties.key][
                e.features[0].properties.value
              ];
          }
        });

        img.setAttribute("alt", "OSM-Icon");
        document.getElementById("img-container").appendChild(img);
      });
      map.on("mouseenter", "Medical/Rescue Help Available", function(e) {
        map.getCanvas().style.cursor = "pointer";
        var coordinates = e.features[0].geometry.coordinates.slice();
        description =
          "<table><tr><th><div class='banner-section' id='img-container' style='float:left'></div></th>";
        description +=
          "<th style='padding: 10px'>" +
          e.features[0].properties.name +
          "</th></tr></table>";
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
          coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }
        pop
          .setLngLat(coordinates)
          .setHTML(description)
          .addTo(map);
        var img = new Image();
        $.ajax({
          url: "/data",
          success: function(res) {
            response = JSON.parse(res);
            img.src =
              response[e.features[0].properties.key][
                e.features[0].properties.value
              ];
          }
        });
        img.setAttribute("alt", "OSM-Icon");
        document.getElementById("img-container").appendChild(img);
      });

      map.on("mouseleave", "Shelter/Food/Supplies Available", function() {
        map.getCanvas().style.cursor = "";
        pop.remove();
      });
      map.on("mouseleave", "Medical/Rescue Help Available", function() {
        map.getCanvas().style.cursor = "";
        pop.remove();
      });

      map.on("click", function(e) {
        var features = map.queryRenderedFeatures(e.point, {
          layers: ["Shelter/Food/Supplies Need", "Medical/Rescue Help Need"]
        });
        if (!features.length) {
          return;
        }
        var feature = features[0];
        // Populate the popup and set its coordinates
        // based on the feature found.
        var popup = new mapboxgl.Popup()
          .setLngLat(feature.geometry.coordinates)
          .setHTML(ClickedMatchObject(feature))
          .addTo(map);
        ///HERE
        document
          .getElementById("btn-collectobj")
          .addEventListener("click", function() {
            var start_cordd = feature.geometry.coordinates;
            var cls = feature.properties.needClass;
            getRoute(start_cordd, cls);
            popup.remove();
          });
      });
      function ClickedMatchObject(feature) {
        // Hide instructions if another location is chosen from the map
        $("#instructions").hide();
        var html = "";
        html += "<div>";
        html += "<fieldset class='with-icon spinner'>";
        html += "<p>" + feature.properties.text + "</p>";
        //html += "<img src='https://digitalsynopsis.com/wp-content/uploads/2016/06/loading-animations-preloader-gifs-ui-ux-effects-10.gif' height='100%' alt='artist' border='1' />"
        //html += "<button class='btn btn-primary ' id='btn-collectobj' value='Collect'>Get Direction</button>";
        html +=
          "<p style='text-align: center;'><input type='button' class='btn btn-primary ' id='btn-collectobj' value='&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Match Need' style='color: red; font-weight: bold; padding: 0.5em 1em; background: url(https://digitalsynopsis.com/wp-content/uploads/2016/06/loading-animations-preloader-gifs-ui-ux-effects-10.gif) no-repeat; background-size:50% 100%;'></p>";
        html += "</fieldset>";
        html += "</div>";
        return html;
      }

      function getRoute(cordd, cl) {
        $("#loadingGif").show();
        var start = cordd;
        var end = [80.255722, 13.079104]; //random point. To be matched.

        $.ajax({
          url: "/find_match",
          data: {
            start_date: +$('input[name="daterange"]').data("daterangepicker")
              .startDate,
            end_date: +$('input[name="daterange"]').data("daterangepicker")
              .endDate,
            min_lat: 13.2823848224,
            min_lng: 80.066986084,
            max_lat: 12.74,
            max_lng: 80.3464508057,
            start_0: start[0],
            start_1: start[1],
            cl: cl
          },
          success: function(res) {
            console.log(JSON.parse(res));
            response = JSON.parse(res);
            // console.log(response['features'].length);
            var end = response.end;
            var route_no = response.route_no;
            var ph = response.phone;
            if (route_no == "not available") {
              console.log("not available");
              console.log(end);
              map.loadImage(
                "/static/siren_emergency.png",
                function(error, helip) {
                  if (error) throw error;
                  console.log("helicop");
                  map.addImage("heli", helip);
                  map.addLayer({
                    id: "emergency",
                    type: "symbol",
                    source: {
                      type: "geojson",
                      data: {
                        type: "Feature",
                        geometry: {
                          type: "Point",
                          coordinates: start
                        }
                      }
                    },
                    layout: {
                      "icon-image": "heli",
                      "icon-size": 0.75
                    }
                  });
                }
              );
            } else {
              console.log("route is available?");
              console.log(end);
              console.log(route_no);
              var directionsRequest =
                "https://api.mapbox.com/directions/v5/mapbox/driving-traffic/" +
                start[0] +
                "," +
                start[1] +
                ";" +
                end[0] +
                "," +
                end[1] +
                "?overview=full&alternatives=true&steps=true&geometries=geojson&access_token=" +
                mapboxgl.accessToken;
              var result = $.ajax({
                method: "GET",
                url: directionsRequest
              }).done(function(data) {
                console.log(data);
                var route = data.routes[route_no].geometry;

                if (map.getLayer("route")) {
                  map.removeLayer("route");
                  map.removeSource("route");
                }
                map.addLayer({
                  id: "route",
                  type: "line",
                  source: {
                    type: "geojson",
                    data: {
                      type: "Feature",
                      geometry: route
                    }
                  },
                  paint: {
                    "line-width": 2,
                    "line-color": "blue"
                  }
                });
                $("#instructions").show();
                $("instructions").html("");
                $("instructions").empty();
                var instructions = document.getElementById("instructions");
                var steps = data.routes[route_no].legs[0].steps;
                instructions.innerHTML =
                  '<p id="dir_head" >' +
                  "Turn-by-Turn Directions" +
                  "</p>";
                steps.forEach(function(step) {
                  instructions.insertAdjacentHTML(
                    "beforeend",
                    '<p style="color:black;background-color:white;">' +
                      step.maneuver.instruction +
                      "</p>"
                  );
                });
                $("#instructions").show();
              });
              if (map.getLayer("start")) {
                map.removeLayer("start");
                map.removeSource("start");
              }
              map.addLayer({
                id: "start",
                type: "circle",
                source: {
                  type: "geojson",
                  data: {
                    type: "Feature",
                    geometry: {
                      type: "Point",
                      coordinates: start
                    }
                  }
                }
              });
              if (map.getLayer("end")) {
                map.removeLayer("end");
                map.removeSource("end");
              }
              map.addLayer({
                id: "end",
                type: "circle",
                source: {
                  type: "geojson",
                  data: {
                    type: "Feature",
                    geometry: {
                      type: "Point",
                      coordinates: end
                    }
                  }
                }
              });
            }
            $("#loadingGif").hide();
          }
        });
      }
      // $('#loadingGif').show();

      var toggleableLayerIds = [
        "Shelter/Food/Supplies Need",
        "Medical/Rescue Help Need",
        "Shelter/Food/Supplies Available",
        "Medical/Rescue Help Available",
        "Flooded Area"
      ];
      var about = [
        "Click the above tab to show or hide Shelter/Food/Supplies Help Need layer on the map. This layer corresponds to the tweets that are related to shelter/food/supplies. Clicking on the respective icon on the map will give you the tweet and a button to start a match with available shelter/food/supplies.",
        "Click the above tab to show or hide Medical/Rescue Help Need Layer on the map. This layer corresponds to the tweets that are related to medical/rescue. Clicking on the respective icon on the map will give you the tweet and a button to start a match with available helps for medical/recue.",
        "Click the above tab to show or hide Shelter/Food/Supplies Available layer on the map. This layer corresponds to the available locations that provide shelter/food/supplies obtained from OpenStreetMap. Hovering over the respective icons will give you the name of the location. When a match is made to these locations, an instruction box is provided with address, phone number and turn-by-turn directions to it.",
        "Click the above tab to show or hide Medical/Supplies Help Available layer on the map. This layer corresponds to the available locations that provide help for medical/rescue obtained from OpenStreetMap. Hovering over the respective icons will give you the name of the location. When a match is made to these locations, an instruction box is provided with address, phone number and turn-by-turn directions to the location.",
        "The Red Helicopter icon marks the reagion that is flooded and cannot be matched to any of the available helps."
      ];
      var img_src = [
        "/static/shelter_need.png",
        "/static/ambulance_orange.png",
        "/static/shelter_green.png",
        "/static/ambulance green.png",
        "/static/fl.png",
        "/static/siren_emergency.png"
      ];
      for (var i = 0; i < toggleableLayerIds.length; i++) {
        var id = toggleableLayerIds[i];
        var icon = document.createElement("img");
        icon.height = 34;
        id_obj = document.createElement("h5");
        id_obj.textContent = id;
        id_obj.style = "display: inline-block;";
        id_obj.id = "nav_id";
        icon.src = img_src[i];
        var link = document.createElement("a");
        link.href = "#";
        link.className = "active";

        var aboutE = document.createElement("p");
        aboutE.className = "about_E";
        aboutE.textContent = about[i];
        link.onclick = function(e) {
          var clickedLayer = this.textContent;
          e.preventDefault();
          e.stopPropagation();
          var visibility = map.getLayoutProperty(clickedLayer, "visibility");
          if (visibility === "visible") {
            map.setLayoutProperty(clickedLayer, "visibility", "none");
            this.className = "";
          } else {
            this.className = "active";
            map.setLayoutProperty(clickedLayer, "visibility", "visible");
          }
        };

        //Dipesh: place this on the right slider
        $('#menu').show();

        var layers = document.getElementById("menu");
        var info = document.createElement("img");
        info.src = "static/information-o.png";
        info.className = "info";
        var first_click = true;
        info.onclick = function(e) {
          if (first_click) {
            $(".about_E").css("display", "none");
            $(this)
              .next()
              .toggle();
            first_click = false;
          } else {
            $(".about_E").hide();
            first_click = true;
          }
        };
        link.appendChild(icon);
        link.appendChild(id_obj);
        //link.textContent = id;

        layers.appendChild(link);
        //        layers.appendChild(info);
        //        layers.appendChild(aboutE);
        // $('#agg_content').css('display', 'block');
        //link.onmouseenter = function(e){
        //    $('#nav_id').show();
        //    $(this).next().toggle();
        //};
        //link.onmouseleave = function(e){
        //    $('#nav_id').hide();
        //};
      }
    } else if (radio == "aggregated") {
      $("#menu").css("display", "none");
      $('#instructions').hide();
      $('#menu').hide();
      $("#steps").css("display", "block");

      //to clear all the layers from the map
      layers_name.forEach(function(lyr) {
        try {
          map.removeLayer(lyr);
          map.removeSource(lyr);
        } catch (err) {
          //        alert("Error!");
        }
      });
      //remove all the existing sources from the map
      source_names.forEach(function(lyr) {
        try {
          map.removeSource(lyr);
        } catch (err) {
          //        alert("Error!");
        }
      });
    }
  });

  function mouseDown(e) {
    // Continue the rest of the function if the shiftkey is pressed.
    if (!(e.shiftKey && e.button === 0) || radio == "individual") return;

    // Disable default drag zooming when the shift key is held down.
    map.dragPan.disable();

    // Call functions for the following events
    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
    document.addEventListener("keydown", onKeyDown);

    // Capture the first xy coordinates
    start = mousePos(e);
  }

  function onMouseMove(e) {
    // Capture the ongoing xy coordinates
    current = mousePos(e);

    // Append the box element if it doesnt exist
    if (!box) {
      box = document.createElement("div");
      box.classList.add("boxdraw");
      canvas.appendChild(box);
    }

    $(".marker").remove();
    $(".r_marker").remove();

    var minX = Math.min(start.x, current.x),
      maxX = Math.max(start.x, current.x),
      minY = Math.min(start.y, current.y),
      maxY = Math.max(start.y, current.y);

    // Adjust width and xy position of the box element ongoing
    var pos = "translate(" + minX + "px," + minY + "px)";
    box.style.transform = pos;
    box.style.WebkitTransform = pos;
    box.style.width = maxX - minX + "px";
    box.style.height = maxY - minY + "px";
    // console.log(pos);
  }

  function onMouseUp(e) {
    // Capture xy coordinates
    finish([start, mousePos(e)]);
  }

  function onKeyDown(e) {
    // If the ESC key is pressed
    if (e.keyCode === 27) finish();
  }

  function finish(bbox) {
    // map.off('mousemove',mouseMv);
    // console.log(bbox);
    console.log(start_LtLg);
    console.log(end_LtLg);
    // Remove these events now that finish has been called.
    document.removeEventListener("mousemove", onMouseMove);
    document.removeEventListener("keydown", onKeyDown);
    document.removeEventListener("mouseup", onMouseUp);
    map.dragPan.enable();

    $.ajax({
      url: "/chennai/count",
      data: {
        start_date: +$('input[name="daterange"]').data("daterangepicker")
          .startDate,
        end_date: +$('input[name="daterange"]').data("daterangepicker").endDate,
        min_lat: start_LtLg.lat,
        min_lng: start_LtLg.lng,
        max_lat: end_LtLg.lat,
        max_lng: end_LtLg.lng
      },
      success: function(res) {
        $("#steps").css("display", "none");
        $("#agg_content").css("display", "block");
        $(".list_head").addClass("animated flipInX");

        $("#date_holder").text(new Date($.now()));
        console.log(res);
        console.log(res.animals);
        $(".text_agg_list").empty();
        $(".img_agg_list").empty();
        $(".osm_agg_list").empty();
        $(".wc_agg_list").empty();
        $(".text_agg_list").append(
          "<td id='rescue_need' style='width: 20%;'><button class='button_1'><img src='/static/ambulance_orange.png' height='30px'><span id='zero_topic_text'>" +
          res.rescue_need +
"</button></td>"
        );
        $(".text_agg_list").append(
          "<td id='shelter_need' style='width: 20%;'><button class='button_1'><img src='/static/shelter_need.png' height='30px'><span id='zero_topic_text'>"+
          res.shelter_need+
"</button></td>"
        );

        $(".img_agg_list").append(
          "<td id='animals'><button class='button_1' id='img_btn'><img src='/static/animal.png' height='30px'><span id='zero_topic_text'>" +
          res.animals +
          "</button></td>"
        );
        $(".img_agg_list").append(
          "<td id='people'><button class='button_1' id='img_btn'><i class='fas fa-users'></i><span id='zero_topic_text'>" +
          res.people +
          "</button></td>"

        );
        $(".img_agg_list").append(
          "<td id='vehicles'><button class='button_1' id='img_btn'><i class='fas fa-car'></i><span id='zero_topic_text'>" +
          res.vehicles +
          "</button></td>"
        );

        $(".osm_agg_list").append(
          "<td id='osm_rescue'><span id='zero_topic_text'>Rescue: " +
            res.osm_rescue +
            "</td>"
          // "<li id=osm_rescue> osm_rescue => " + res.osm_rescue + "</li>"
        );
        $(".osm_agg_list").append(
          "<td id='osm_shelter'><span id='zero_topic_text'>Shelter: " +
            res.osm_shelter +
            "</td>"
          // "<li id=osm_shelter> osm_shelter => " + res.osm_shelter + "</li>"
        );

        $(".text_agg_list li").addClass("animated fadeIn");
        $(".osm_agg_list li").addClass("animated fadeIn");
        $(".img_agg_list li").addClass("animated fadeIn");

        //   for (var key in res) {
        //     if (res.hasOwnProperty(key)) {
        //         console.log(key + " => " + res[key]);
        //         $(".agg_list").append("<li id="+key+">"+key + " => " + res[key]+"</li>");
        //     }
        // }
      }
    });
  }

  $(document).on("click", ".text_agg_list td", function() {
    console.log("Clicked list. " + this.id);
    var txt_name = this.id;
    $(".marker").remove();
    $(".r_marker").remove();
    $("#zero_container").empty();
    $("#close_zero").css("display", "block");
    $(".zero").css("display", "block");
    $(".zero").removeClass("animated slideOutRight");
    $(".zero").addClass("animated slideInRight");
    $("#map").css("z-index", "-1");
    $("#zero_topic").empty();
    if (this.id == "rescue_need") {
      $("#zero_topic").append(
        "<img src='/static/ambulance_orange.png' height='35px'> <span id='zero_topic_text'>" +
          this.id +
          "</span>"
      );
    } else {
      $("#zero_topic").append(
        "<img src='/static/shelter_need.png' height='35px'> <span id='zero_topic_text'>" +
          this.id +
          "</span>"
      );
    }

    $.ajax({
      url: "/wc",
      data: {
        start_date: +$('input[name="daterange"]').data("daterangepicker")
          .startDate,
        end_date: +$('input[name="daterange"]').data("daterangepicker").endDate,
        min_lat: start_LtLg.lat,
        min_lng: start_LtLg.lng,
        max_lat: end_LtLg.lat,
        max_lng: end_LtLg.lng,
        q_str: this.id
      },
      success: function(res) {
        console.log(res);

        // var layers = document.getElementById('picture')
        $("#picture").empty();

        $("#picture").append(
          "<img src='data:image/png;base64," +
            res +
            "' height='165px' id='wc_img'>"
        );
        // var icon = document.createElement('img');
        //   icon.height = 80;
        //   icon.src = 'data:image/png;base64,' + res;
        //  layers.appendChild(icon);

        //        $(".wc_agg_list").src = 'data:image/png,' + res;
        // "<li id=osm_shelter> osm_shelter => " + res.osm_shelter + "</li>"
        $("#wc").remove();
        $(".list_head").removeClass("animated flipInX");
        /*$("#agg_content").append(
          "<div class='list_head' id='wc'>Word Cloud:</div>"
        );
        $("#wc").addClass("animated flipInX");*/
      }
    });

    $.ajax({
      url: "/chennai/loc_name",
      data: {
        start_date: +$('input[name="daterange"]').data("daterangepicker")
          .startDate,
        end_date: +$('input[name="daterange"]').data("daterangepicker").endDate,
        min_lat: start_LtLg.lat,
        min_lng: start_LtLg.lng,
        max_lat: end_LtLg.lat,
        max_lng: end_LtLg.lng,
        q_str: this.id
      },
      success: function(res) {
        console.log(JSON.parse(res));
        response = JSON.parse(res);
        // console.log(response.features);
        // if (this.id='shelter_need'){

        for (var key in response.features) {
          if (response.features.hasOwnProperty(key)) {
            //            console.log(key + " => " + response.features[key]);
            id_n = key.replace("#", "");
            var id_name = id_n.replace(/ /g, "_");
            $("#zero_container").append(
              key +
                " [" +
                response.features[key].length +
                "] <img src='/static/plus.png' height='15px' class='plus' id='plus-" +
                id_name +
                "'><br>"
            );
            $("#zero_container").append(
              " <div id='" + id_name + "' class='twt_pack'></div>"
            );
            var count = 0;
            for (var k in response.features[key]) {
              if (response.features[key].hasOwnProperty(k)) {
                var el = document.createElement("div");
                //                console.log("txt_agg:",txt_name);

                if (txt_name == "shelter_need") {
                  el.className = "marker";
                } else if (txt_name == "rescue_need") {
                  el.className = "r_marker";
                }

                // make a marker for each feature and add to the map
                new mapboxgl.Marker(el)
                  .setLngLat(response.features[key][k].geometry.coordinates)
                  .addTo(map);
                var id = "#" + id_name;
                count = count + 1;
                $(id).append(
                  " <div id='twt_content' class='animated flipInX'>" +
                    response.features[key][k].properties.text +
                    "</div>"
                );
                // console.log(k + " => " + response.features[key][k].geometry.coordinates);
              }
            }
            $(id)
              .children()
              .mark(key);
            //            console.log(count);
          }
        }
        //  response["features"].forEach(function(marker) {

        //   // create a HTML element for each feature
        //   var el = document.createElement('div');
        //   el.className = 'marker';

        //   // make a marker for each feature and add to the map
        //   new mapboxgl.Marker(el)
        //   .setLngLat(marker.geometry.coordinates)
        //   .addTo(map);
        //   // $('.marker').addClass('animated fadeInUp');
        // });
        //   // $('.marker').addClass('animated fadeInUp');
        // }
        // if (response["features"].length == 0) {
        //   $("#zero_container").append(
        //     "<h3 id='no_data' class='animated rubberBand'>No Data Avaiable</h3>"
        //   );
        // } else {
        //   response["features"].forEach(function(featr) {
        //     console.log(featr.properties.text);
        //     $("#zero_container").append(
        //       "<div id='twt_content' class='animated flipInX'>" +
        //         featr.properties.text +
        //         "</div>"
        //     );
        //   });
        // }

        //   for (var key in response.features) {
        //     if (response.features.hasOwnProperty(key)) {
        //         console.log(key + " => " + response.features[key]);
        //         for (var k in response.features[key]) {
        //           if (response.features[key].hasOwnProperty(k)) {
        //               console.log(k + " => " + response.features[key][k].geometry.coordinates);
        //           }
        //       }
        //         $("#zero_container").append(key+"<br>");
        //     }
        // }
      }
    });
  });

  // $(document).on("click", ".osm_agg_list li", function() {
  //   console.log("Clicked list. " + this.id);
  //   $("#zero_container").empty();
  //   $(".zero").css("display", "block");
  //   $(".zero").removeClass("animated slideOutRight");
  //   $(".zero").addClass("animated slideInRight");
  //   $("#map").css("z-index", "-1");

  //   $.ajax({
  //     url: "/chennai/data",
  //     data: {
  //       start_date: +$('input[name="daterange"]').data("daterangepicker")
  //         .startDate,
  //       end_date: +$('input[name="daterange"]').data("daterangepicker")
  //         .endDate,
  //       min_lat: start_LtLg.lat,
  //       min_lng: start_LtLg.lng,
  //       max_lat: end_LtLg.lat,
  //       max_lng: end_LtLg.lng,
  //       q_str: this.id
  //     },
  //     success: function(res) {
  //       console.log(JSON.parse(res));
  //       response=JSON.parse(res);

  //       response['features'].forEach(function (featr) {
  //         console.log(featr.properties.text);
  //         $('#zero_container').append("<div id='twt_content' class='animated bounceIn'>"+featr.properties.text+"</div>")
  //     });

  //       //   for (var key in response) {
  //       //     if (Response.hasOwnProperty(key)) {
  //       //         // console.log(key + " => " + response[key]);
  //       //         $(".agg_list").append("<li id="+key+">"+key + " => " + response[key]+"</li>");
  //       //     }
  //       // }
  //     }
  //   });
  // });

  $(document).on("click", ".img_agg_list td", function() {
    //    console.log("Clicked list. " + this.id);
    $(".marker").remove();
    $(".r_marker").remove();
    $("#zero_container").empty();
    $("#zero_topic").empty();
    $("#close_zero").css("display", "block");
    $(".zero").css("display", "block");
    $(".zero").removeClass("animated slideOutRight");
    $(".zero").addClass("animated slideInRight");
    $("#map").css("z-index", "-1");

    $("#zero_topic").append(
      "<span id='zero_topic_img_txt'>" + this.id + "</span>"
    );

    $.ajax({
      url: "/chennai/data",
      data: {
        start_date: +$('input[name="daterange"]').data("daterangepicker")
          .startDate,
        end_date: +$('input[name="daterange"]').data("daterangepicker").endDate,
        min_lat: start_LtLg.lat,
        min_lng: start_LtLg.lng,
        max_lat: end_LtLg.lat,
        max_lng: end_LtLg.lng,
        q_str: this.id
      },
      success: function(res) {
        console.log(JSON.parse(res));
        response = JSON.parse(res);
        // console.log(response['features'].length);

        if (response["features"].length == 0) {
          $("#zero_container").append(
            "<h3 id='no_data' class='animated rubberBand'>No Data Avaiable</h3>"
          );
        } else {
          response["features"].forEach(function(featr) {
            //            console.log(featr.properties.image[0].imageURL);
            $("#zero_container").append(
              "<div id='twt_content' class='animated flipInX'>" +
                featr.properties.text +
                "<br><img src='" +
                featr.properties.image[0].imageURL +
                "' height='100px'>" +
                "</div>"
            );
          });
        }

        //   for (var key in response) {
        //     if (Response.hasOwnProperty(key)) {
        //         // console.log(key + " => " + response[key]);
        //         $(".agg_list").append("<li id="+key+">"+key + " => " + response[key]+"</li>");
        //     }
        // }
      }
    });
  });

  $("#daterange").on("apply.daterangepicker", function(ev, picker) {
    $(".marker").remove();
    $(".r_marker").remove();
  });

  // $("input[type=radio][name=user_lvl]").change(function() {
  //   if (this.value == "individual") {
  //     unsetCanv();
  //   } else if (this.value == "aggregated") {
  //     console.log(this.value);
  //   }
  // });
  // map.on('mousemove', function(e) {
  //     popup.setLngLat(e.lngLat)
  //         .setText("Demo")
  //         .addTo(map);
  // });
  $("#loadingGif").hide();
});
//----------------------------------------------------------------------

// ---------------------------------------------------------------------
var pop = new mapboxgl.Popup({
  closeButton: false,
  closeOnClick: false
});