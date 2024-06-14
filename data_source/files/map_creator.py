import folium
from folium.plugins import Draw
import osmnx as ox
import geopandas as gpd


class MapCreator:
    def __init__(self, center_coordinates):
        self.map = folium.Map(location=center_coordinates, zoom_start=14)
        draw = Draw(export=True)
        draw.add_to(self.map)

    def save_map(self, filepath):
        self.map.save(filepath)

    def load_polygon_data(self, polygon_geojson):
        gdf = gpd.GeoDataFrame.from_features(polygon_geojson['features'])
        return gdf

    def add_buildings_to_map(self, osm_data):
        folium.GeoJson(osm_data).add_to(self.map)
