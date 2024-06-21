import json
from model_extraction.prepration.osm_data import ProcessOsm
from model_extraction.prepration.shapefile_data import ProcessShapefile
from model_extraction.prepration.utils import GdfUtils
import geopandas as gpd
from shapely.geometry import Polygon


class PrepMain:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.shapefile_path = config['shapefile_path']
        self.output_path = config['building_path']
        self.bbox_coords = config['study_case']
        self.osm_processor = ProcessOsm()
        self.shapefile_processor = ProcessShapefile()

    def process_data(self):
        bounding_box = Polygon(self.bbox_coords)
        osm_gdf = self.osm_processor.fetch_osm_data(bounding_box)
        shapefile_gdf = self.shapefile_processor.process_shapefile(self.shapefile_path, bounding_box)
        # osm_gdf = osm_gdf.to_crs(epsg=32632)
        # shapefile_gdf = shapefile_gdf.to_crs(epsg=32632)
        final_gdf = gpd.overlay(osm_gdf, shapefile_gdf, how='intersection')
        return final_gdf

    def plot_and_save(self, final_gdf):
        utils = GdfUtils(final_gdf)
        utils.plot()
        utils.save_geodataframe(self.output_path)
