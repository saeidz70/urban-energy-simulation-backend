import os

import geopandas as gpd
import osmnx as ox
from shapely.geometry import Polygon

from config.config import Config


class BuildingExtractor(Config):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.user_file_path = self.config['user_building_file']
        self.output_file_path = self.config['building_path']
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.source_column = "building_source"
        self.source_config = self.config.get('features', {}).get(self.source_column, {}).get("source", {})
        self.boundary_polygon = None

    def _load_boundary(self, boundaries):
        """Load and combine boundary geometries into a single polygon."""
        boundaries_gdf = boundaries
        if boundaries_gdf.empty:
            raise ValueError("Boundary GeoJSON file is empty.")
        boundaries_gdf = boundaries_gdf[boundaries_gdf.geometry.is_valid]
        combined_boundary = boundaries_gdf.unary_union
        if not isinstance(combined_boundary, Polygon):
            raise ValueError("Combined boundary is not a valid polygon.")
        return combined_boundary

    def _read_file(self, file_path, file_type):
        """Read GeoJSON file."""
        gdf = gpd.read_file(file_path)
        if gdf.empty:
            raise ValueError(f"{file_type.capitalize()} file is empty.")
        if 'geometry' not in gdf.columns:
            raise ValueError(f"{file_type.capitalize()} file lacks a geometry column.")
        return gdf

    def _ensure_crs(self, gdf, target_crs):
        """Ensure CRS consistency."""
        if gdf.crs is None or gdf.crs.to_string() != target_crs:
            gdf = gdf.to_crs(target_crs)
        return gdf

    def _user_file_has_valid_geometry(self):
        """Check if user file has valid geometries."""
        user_gdf = self._read_file(self.user_file_path, "user")
        user_gdf = self._ensure_crs(user_gdf, self.default_crs)
        user_gdf = user_gdf[user_gdf.geometry.is_valid]
        return user_gdf.geometry.apply(lambda geom: geom.within(self.boundary_polygon)).any()

    def _extract_from_user_file(self):
        """Extract valid buildings from the user file."""
        user_gdf = self._read_file(self.user_file_path, "user")
        user_gdf = self._ensure_crs(user_gdf, self.default_crs)
        user_gdf = user_gdf[user_gdf.geometry.is_valid]
        user_buildings = user_gdf[user_gdf.geometry.apply(lambda geom: geom.within(self.boundary_polygon))]
        user_buildings[self.source_column] = self.source_config.get('user')
        return user_buildings[['geometry', self.source_column]]

    def _extract_from_osm(self):
        """Extract building footprints from OSM."""
        osm_buildings = ox.features_from_polygon(self.boundary_polygon, tags={'building': True})
        if osm_buildings.empty:
            raise ValueError("No buildings found in the specified boundary.")
        osm_buildings[self.source_column] = self.source_config.get('osm')
        return osm_buildings[['geometry', self.source_column]]

    def _save_buildings(self, buildings_gdf):
        """Save building data to a GeoJSON file."""
        if buildings_gdf is None or buildings_gdf.empty:
            raise ValueError("No valid building data to save.")
        os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
        buildings_gdf.to_file(self.output_file_path, driver='GeoJSON')

    def run(self, boundaries):
        """Main method to extract buildings and save them."""
        self.boundary_polygon = self._load_boundary(boundaries)
        try:
            if os.path.exists(self.user_file_path) and self._user_file_has_valid_geometry():
                buildings_gdf = self._extract_from_user_file()
            else:
                buildings_gdf = self._extract_from_osm()
            self._save_buildings(buildings_gdf)
            return buildings_gdf
        except Exception as e:
            print(f"Error during building extraction: {e}")
