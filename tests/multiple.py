
def test_photon_elasitc_index():

    from elasticsearch import Elasticsearch
    from elasticsearch_dsl import Search, Q
    from elasticsearch_dsl.connections import connections

    es = Elasticsearch()

    connections.create_connection(hosts=['130.108.85.186:9200'], timeout=20)

    test_bb = [39.7671048218,-84.0883362291,39.800371844,-84.0450561049]
    #test_bb = [-39.7671048218,-84.0883362291,-39.800371844,-84.0450561049]

    phrase_search = [Q({"filtered" : {
                      "filter" : {
                        "geo_bounding_box" : {
                          "coordinate" : {
                            "bottom_left" : {
                              "lat" : test_bb[0],
                              "lon" : test_bb[1]
                            },
                            "top_right" : {
                              "lat" : test_bb[2],
                              "lon" : test_bb[3]
                            }
                          }
                        }
                      },
                      "query": {
                        "match_all": {}
                        }
                      }
                  })]

    e_search = Search(index="photon_v1").query(Q('bool', must=phrase_search))

    assert e_search.count() > 0
