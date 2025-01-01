import os

import geopandas as gpd

from config.config import Config
from processing.preparation.building_gdf_creator.db_b_id_fetcher import BuildingDatabaseFetcher


class UserBuildingExtractor(Config):
    """
    Extracts user-provided buildings and augments with database building IDs if necessary.
    """
    def __init__(self):
        super().__init__()
        self.load_config()
        self.user_file_path = self.config['user_building_file']
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.source_column = "building_source"
        self.source_config = self.config.get('features', {}).get(self.source_column, {}).get("sources", {})
        self.fetcher = BuildingDatabaseFetcher()

    def _read_file(self):
        """Read GeoJSON file."""
        gdf = gpd.read_file(self.user_file_path)
        if gdf.empty:
            raise ValueError("User file is empty.")
        if 'geometry' not in gdf.columns:
            raise ValueError("User file lacks a geometry column.")
        return gdf

    def _ensure_crs(self, gdf):
        """Ensure CRS consistency."""
        if gdf.crs is None or gdf.crs.to_string() != self.default_crs:
            gdf = gdf.to_crs(self.default_crs)
        return gdf

    def _fetch_building_ids(self, user_gdf):
        """Fetch building IDs from the database if conditions are met."""
        scenario_list = self.config.get("project_info", {}).get("scenarioList", [])
        if "baseline" not in scenario_list and "update" not in scenario_list:
            print("Fetching building IDs from the database...")
            db_gdf = self.fetcher.run(user_gdf)
            if db_gdf is not None and not db_gdf.empty:
                # Update source column for database results
                db_gdf[self.source_column] = self.source_config.get("db", "Database")

                # Merge database results with user buildings
                user_gdf = user_gdf.merge(
                    db_gdf[["geometry", "building_id", self.source_column]],
                    on="geometry",
                    how="left"
                )

                # Fill missing sources with "User" for unmatched user buildings
                user_gdf[self.source_column] = user_gdf[self.source_column].fillna(
                    self.source_config.get("user", "User"))
            else:
                print("No valid response from the database for building IDs. Skipping...")
                user_gdf[self.source_column] = self.source_config.get("user", "User")
        return user_gdf

    def run(self, boundary_polygon):
        """Extract buildings from the user file and fetch building IDs."""
        if not os.path.exists(self.user_file_path):
            return gpd.GeoDataFrame(columns=["geometry", self.source_column, "building_id"])

        try:
            # Read and filter user file
            user_gdf = self._read_file()
            user_gdf = self._ensure_crs(user_gdf)
            user_gdf = user_gdf[user_gdf.geometry.is_valid]
            user_gdf = user_gdf[user_gdf.geometry.apply(lambda geom: geom.within(boundary_polygon))]
            user_gdf[self.source_column] = self.source_config.get('user', 'User')

            # Fetch building IDs if needed and update the source column
            user_gdf = self._fetch_building_ids(user_gdf)

            # Return the result with required columns
            return user_gdf[['geometry', self.source_column, 'building_id']]
        except Exception as e:
            print(f"Error during user building extraction: {e}")
            return gpd.GeoDataFrame(columns=["geometry", self.source_column, "building_id"])
