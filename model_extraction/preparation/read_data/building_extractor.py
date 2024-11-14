import os
import os
import geopandas as gpd
from config.config import Config
from model_extraction.preparation.read_data.osm_building_extractor import \
    OSMBuildingExtractor


class BuildingExtractor(Config):
    def __init__(self):
        super().__init__()

        # Paths and boundary loading
        self.user_file_path = self.config['user_file_path']
        self.output_file_path = self.config['building_path']
        self.boundary_geojson_path = self.config['selected_boundaries']
        self.boundary_polygon = self._load_boundary()

        # Initialize the OSMBuildingExtractor
        self.osm_extractor = OSMBuildingExtractor(self.config)  # Pass the config dictionary

    def _load_boundary(self):
        """Load the boundary polygon from the GeoJSON file."""
        try:
            boundary_gdf = gpd.read_file(self.boundary_geojson_path)
            print("Boundary polygon loaded successfully.")
            return boundary_gdf.unary_union
        except Exception as e:
            print(f"Error loading boundary polygon: {e}")
            return None

    def extract_and_save_buildings(self):
        """Main method to extract buildings either from the user file or OSM."""
        if self._user_file_has_valid_geometry():
            print("Valid user file found. Extracting buildings from the user file.")
            buildings_gdf = self._extract_from_user_file()
        else:
            print("User file invalid or not provided. Extracting buildings from OSM.")
            buildings_gdf = self.osm_extractor.extract_buildings()  # Use OSMBuildingExtractor

        if buildings_gdf is not None and not buildings_gdf.empty:
            self._save_buildings(buildings_gdf)
        else:
            print("No valid building data to save.")

    def _user_file_has_valid_geometry(self):
        """Check if the user file has valid geometry."""
        try:
            user_gdf = gpd.read_file(self.user_file_path)
            if user_gdf is not None and not user_gdf.empty and 'geometry' in user_gdf.columns:
                # TODO: Check if the CRS is EPSG:4326
                user_gdf = user_gdf.set_crs(epsg=4326, allow_override=True)
                # Check if geometries are within the boundary
                within_boundary = user_gdf.within(self.boundary_polygon).any()
                print(f"Geometries within boundary: {within_boundary}")
                return within_boundary
        except Exception as e:
            print(f"Error reading user file: {e}")
        return False

    def _extract_from_user_file(self):
        """Extract buildings from the user-provided file."""
        try:
            user_gdf = gpd.read_file(self.user_file_path)
            # Filter buildings within the boundary
            buildings_within_boundary = user_gdf[user_gdf.within(self.boundary_polygon)]
            print(f"Extracted {len(buildings_within_boundary)} buildings from the user file.")
            return buildings_within_boundary[['geometry']]  # Keep only the geometry column
        except Exception as e:
            print(f"Error extracting buildings from user file: {e}")
            return None

    def _save_buildings(self, buildings_gdf):
        """Save the buildings GeoDataFrame to a GeoJSON file."""
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)

        # Keep only the geometry column
        buildings_gdf = buildings_gdf[['geometry']]  # Ensure only the geometry column is kept

        try:
            buildings_gdf.to_file(self.output_file_path, driver='GeoJSON')
            print(f"Building geometries saved to {self.output_file_path}.")
        except Exception as e:
            print(f"Error saving building data: {e}")
