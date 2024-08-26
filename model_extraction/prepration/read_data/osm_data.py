import geopandas as gpd
import osmnx as osm
from shapely.geometry import Polygon


class ProcessOsm(object):
    def __init__(self):
        pass

    def fetch_osm_data(self, bounding_box):
        polygon = Polygon(bounding_box)
        tags = {'building': True}
        osm_data = osm.features_from_polygon(polygon, tags)
        osm_gdf = gpd.GeoDataFrame(osm_data, geometry='geometry', crs='epsg:4326')
        return osm_gdf
