import json

import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import Polygon

from model_extraction.prepration.built_year.osm_built_year import OSMDataFetcher
from model_extraction.prepration.read_data.osm_data import ProcessOsm
from model_extraction.prepration.read_data.shapefile_data import ProcessShapefile


class GeoDataProcessor:
    """Class to process geospatial data from OSM and Shapefiles."""

    def __init__(self, config_path):
        """Initialize the GeoDataProcessor with configuration file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            raise Exception(f"Configuration file {config_path} not found.")
        except json.JSONDecodeError:
            raise Exception(f"Error decoding JSON from {config_path}.")

        self.shapefile_path = config['shapefile_path']
        self.output_path = config['building_path']
        self.bbox_coords = config['study_case']
        self.default_epsg_code = config['DEFAULT_EPSG_CODE']
        self.osm_processor = ProcessOsm()
        self.shapefile_processor = ProcessShapefile()
        self.osm_data_fetcher = OSMDataFetcher()
        self.gdf = None

    def save_geodataframe(self, path):
        """Save the GeoDataFrame to a file."""
        try:
            self.gdf.to_file(path, driver='GeoJSON')
        except Exception as e:
            raise Exception(f"Error saving GeoDataFrame to {path}: {e}")

    def convert_crs(self, epsg):
        """Convert the GeoDataFrame to a specified CRS."""
        self.gdf = self.gdf.to_crs(epsg=epsg)
        return self.gdf

    def plot_geodataframe(self):
        """Plot the GeoDataFrame."""
        self.gdf.plot()
        plt.show()
        return self.gdf

    def process_data(self):
        """Process the data from OSM and Shapefiles and return the final GeoDataFrame."""
        try:
            bounding_box = Polygon(self.bbox_coords)
            osm_gdf = self.osm_processor.fetch_osm_data(bounding_box)
            shapefile_gdf = self.shapefile_processor.process_shapefile(self.shapefile_path, bounding_box)
            osm_gdf = osm_gdf.to_crs(epsg=self.default_epsg_code)
            shapefile_gdf = shapefile_gdf.to_crs(epsg=self.default_epsg_code)

            osm_gdf['osm_id'] = osm_gdf.index.map(lambda x: x[1] if isinstance(x, tuple) else x)

            final_gdf = gpd.overlay(osm_gdf, shapefile_gdf, how='intersection')

            if 'osm_id' in final_gdf.columns:
                final_gdf['built_year'] = final_gdf['osm_id'].apply(self.osm_data_fetcher.fetch_construction_year)
            else:
                print("osm_id is not present in the final_gdf. Intersection might have dropped the column.")

            final_gdf.insert(0, 'b_id', range(1, len(final_gdf) + 1))
            built_years = final_gdf.pop('built_year')
            final_gdf.insert(1, 'built_year', built_years)

            self.gdf = final_gdf

            # Plot and save the GeoDataFrame
            self.plot_geodataframe()
            self.save_geodataframe(self.output_path)

            return self.gdf
        except Exception as e:
            raise Exception(f"Error processing data: {e}")
