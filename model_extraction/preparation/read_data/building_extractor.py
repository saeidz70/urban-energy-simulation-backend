import os

import geopandas as gpd
from shapely.ops import unary_union

from config.config import Config
from model_extraction.preparation.read_data.osm_building_extractor import OSMBuildingExtractor


class BuildingExtractor(Config):
    def __init__(self):
        super().__init__()
        self.user_file_path = self.config['user_building_file']
        self.output_file_path = self.config['building_path']
        self.boundary_geojson_path = self.config['selected_boundaries']
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.boundary_polygon = self._load_boundary()
        self.osm_extractor = OSMBuildingExtractor(self.config)

    def _load_boundary(self):
        """Load and prepare the boundary polygon from the GeoJSON file."""
        boundary_gdf = self._read_file(self.boundary_geojson_path, "boundary")
        boundary_gdf = self._ensure_crs(boundary_gdf, self.default_crs)

        # Combine geometries into a single boundary
        return unary_union(boundary_gdf.geometry)

    def extract_and_save_buildings(self):
        """Main method to extract and save building geometries."""
        buildings_gdf = self._extract_from_user_file() if self._user_file_has_valid_geometry() else self.osm_extractor.extract_buildings()

        if buildings_gdf is not None and not buildings_gdf.empty:
            self._save_buildings(buildings_gdf)
        else:
            print("No valid building data to save.")

    def _user_file_has_valid_geometry(self):
        """Validate geometries in the user-provided file."""
        try:
            user_gdf = self._read_file(self.user_file_path, "user")
            user_gdf = self._ensure_crs(user_gdf, self.default_crs)

            # Clean and validate geometries
            user_gdf = user_gdf[user_gdf.geometry.is_valid]
            return user_gdf.geometry.apply(lambda geom: geom.within(self.boundary_polygon)).any()
        except Exception as e:
            print(f"Error validating user file: {e}")
            return False

    def _extract_from_user_file(self):
        """Extract valid buildings from the user-provided file."""
        try:
            user_gdf = self._read_file(self.user_file_path, "user")
            user_gdf = self._ensure_crs(user_gdf, self.default_crs)

            # Filter geometries within the boundary
            user_gdf = user_gdf[user_gdf.geometry.is_valid]
            buildings_within_boundary = user_gdf[
                user_gdf.geometry.apply(lambda geom: geom.within(self.boundary_polygon))]

            print(f"Extracted {len(buildings_within_boundary)} buildings from the user file.")
            return buildings_within_boundary[['geometry']]
        except Exception as e:
            print(f"Error extracting buildings from user file: {e}")
            return None

    def _save_buildings(self, buildings_gdf):
        """Save the buildings GeoDataFrame to a GeoJSON file."""
        try:
            os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
            buildings_gdf.to_file(self.output_file_path, driver='GeoJSON')
            print(f"Building geometries saved to {self.output_file_path}.")
        except Exception as e:
            print(f"Error saving building data: {e}")

    def _read_file(self, file_path, file_type):
        """Read a GeoJSON file."""
        try:
            gdf = gpd.read_file(file_path)
            if gdf.empty:
                raise ValueError(f"{file_type.capitalize()} file is empty.")
            if 'geometry' not in gdf.columns:
                raise ValueError(f"{file_type.capitalize()} file lacks a geometry column.")
            return gdf
        except Exception as e:
            raise RuntimeError(f"Error reading {file_type} file: {e}")

    def _ensure_crs(self, gdf, target_crs):
        """Ensure the GeoDataFrame is in the target CRS."""
        try:
            if gdf.crs is None or gdf.crs.to_string() != target_crs:
                print(f"Reprojecting to {target_crs}.")
                gdf = gdf.to_crs(target_crs)
            return gdf
        except Exception as e:
            raise RuntimeError(f"Error ensuring CRS: {e}")
