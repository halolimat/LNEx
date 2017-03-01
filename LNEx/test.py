
import prepare_osm_gazetteer

# chennai flood bounding box
chennai_bb = [  12.74,  80.066986084,
                13.2823848224,  80.3464508057 ]

print prepare_osm_gazetteer.build_bb_gazetteer(chennai_bb)
