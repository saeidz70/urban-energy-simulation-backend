import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

from config.config import Config
from processing.preparation.building_gdf_creator.osm_building_extractor import OSMBuildingExtractor
from processing.preparation.building_gdf_creator.user_building_extractor import UserBuildingExtractor


class BuildingManager(Config):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.user_extractor = UserBuildingExtractor()
        self.osm_extractor = OSMBuildingExtractor()
        self.output_file_path = self.config['building_path']

    def _remove_overlapping_osm_buildings(self, osm_gdf, user_gdf):
        """Remove overlapping OSM buildings if user buildings exist in the same location."""
        if user_gdf.empty:
            return osm_gdf
        user_union = unary_union(user_gdf.geometry)
        return osm_gdf[~osm_gdf.geometry.intersects(user_union)]

    def _save_buildings(self, buildings_gdf):
        """Save building data to a GeoJSON file."""
        if buildings_gdf.empty:
            raise ValueError("No valid building data to save.")
        buildings_gdf.to_file(self.output_file_path, driver='GeoJSON')

    def run(self, boundaries):
        """Extract buildings from both sources and merge results."""
        boundary_polygon = self._load_boundary(boundaries)

        print("Extracting user buildings...")
        user_gdf = self.user_extractor.run(boundary_polygon)

        print("Extracting OSM buildings...")
        osm_gdf = self.osm_extractor.run(boundary_polygon)

        print("Removing overlapping OSM buildings...")
        osm_gdf = self._remove_overlapping_osm_buildings(osm_gdf, user_gdf)

        print("Merging user and OSM buildings...")
        combined_gdf = gpd.GeoDataFrame(pd.concat([user_gdf, osm_gdf], ignore_index=True))
        self._save_buildings(combined_gdf)

        return combined_gdf

    def _load_boundary(self, boundaries):
        """Load and combine boundary geometries into a single polygon."""
        boundaries_gdf = boundaries
        if boundaries_gdf.empty:
            raise ValueError("Boundary GeoJSON file is empty.")
        boundaries_gdf = boundaries_gdf[boundaries_gdf.geometry.is_valid]
        return boundaries_gdf.unary_union
