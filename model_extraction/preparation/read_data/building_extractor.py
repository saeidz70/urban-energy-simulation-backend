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
        self.boundary_geojson_path = self.config['selected_boundaries']
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.boundary_polygon = self._load_boundary()

    def _load_boundary(self):
        """Load and combine boundary geometries into a single polygon."""
        try:
            print(f"Loading boundary from: {self.boundary_geojson_path}")
            gdf = gpd.read_file(self.boundary_geojson_path)
            if gdf.empty:
                raise ValueError("Boundary GeoJSON file is empty.")
            gdf = gdf[gdf.geometry.is_valid]
            combined_boundary = gdf.unary_union
            if not isinstance(combined_boundary, Polygon):
                raise ValueError("Combined boundary is not a valid polygon.")
            print("Boundary loaded successfully.")
            return combined_boundary
        except Exception as e:
            raise RuntimeError(f"Error loading boundary: {e}")

    def extract_and_save_buildings(self):
        """Main method to extract buildings and save them."""
        try:
            # Check user file
            if not os.path.exists(self.user_file_path):
                print(f"User file not found at: {self.user_file_path}")
            elif not self._user_file_has_valid_geometry():
                print("User file exists but has no valid geometries.")
            else:
                print("User file is valid. Extracting buildings from user file.")
                buildings_gdf = self._extract_from_user_file()
                self._save_buildings(buildings_gdf)
                return

            # If user file is not valid, fallback to OSM
            print("User file is missing or invalid. Extracting buildings from OSM.")
            buildings_gdf = self._extract_from_osm()
            self._save_buildings(buildings_gdf)

        except Exception as e:
            print(f"Error during building extraction: {e}")

    def _user_file_has_valid_geometry(self):
        """Check if user file has valid geometries."""
        try:
            print(f"Validating geometries in user file: {self.user_file_path}")
            user_gdf = self._read_file(self.user_file_path, "user")
            user_gdf = self._ensure_crs(user_gdf, self.default_crs)
            user_gdf = user_gdf[user_gdf.geometry.is_valid]
            return user_gdf.geometry.apply(lambda geom: geom.within(self.boundary_polygon)).any()
        except Exception as e:
            print(f"Error validating user file: {e}")
            return False

    def _extract_from_user_file(self):
        """Extract valid buildings from the user file."""
        try:
            print(f"Extracting buildings from user file: {self.user_file_path}")
            user_gdf = self._read_file(self.user_file_path, "user")
            user_gdf = self._ensure_crs(user_gdf, self.default_crs)
            user_gdf = user_gdf[user_gdf.geometry.is_valid]
            user_gdf = user_gdf[user_gdf.geometry.apply(lambda geom: geom.within(self.boundary_polygon))]
            print(f"Extracted {len(user_gdf)} buildings from user file.")
            return user_gdf[['geometry']]
        except Exception as e:
            print(f"Error extracting from user file: {e}")
            return None

    def _extract_from_osm(self):
        """Extract building footprints from OSM."""
        try:
            print("Extracting building footprints from OSM...")
            buildings = ox.features_from_polygon(self.boundary_polygon, tags={'building': True})
            if buildings.empty:
                raise ValueError("No buildings found in the specified boundary.")
            print(f"Extracted {len(buildings)} buildings from OSM.")
            return buildings[['geometry']]
        except Exception as e:
            raise RuntimeError(f"Error extracting buildings from OSM: {e}")

    def _save_buildings(self, buildings_gdf):
        """Save building data to a GeoJSON file."""
        try:
            if buildings_gdf is None or buildings_gdf.empty:
                raise ValueError("No valid building data to save.")
            os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
            print(f"Saving buildings to: {self.output_file_path}")
            buildings_gdf.to_file(self.output_file_path, driver='GeoJSON')
            print(f"Building data saved to: {self.output_file_path}")
        except Exception as e:
            print(f"Error saving building data: {e}")

    def _read_file(self, file_path, file_type):
        """Read GeoJSON file."""
        try:
            print(f"Reading {file_type} file: {file_path}")
            gdf = gpd.read_file(file_path)
            if gdf.empty:
                raise ValueError(f"{file_type.capitalize()} file is empty.")
            if 'geometry' not in gdf.columns:
                raise ValueError(f"{file_type.capitalize()} file lacks a geometry column.")
            return gdf
        except Exception as e:
            raise RuntimeError(f"Error reading {file_type} file: {e}")

    def _ensure_crs(self, gdf, target_crs):
        """Ensure CRS consistency."""
        try:
            if gdf.crs is None or gdf.crs.to_string() != target_crs:
                print(f"Reprojecting GeoDataFrame to {target_crs}.")
                gdf = gdf.to_crs(target_crs)
            return gdf
        except Exception as e:
            raise RuntimeError(f"Error ensuring CRS: {e}")
