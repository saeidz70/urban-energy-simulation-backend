import logging

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

from config.config import Config
from processing.preparation.building_gdf_creator.db_b_id_fetcher import BuildingDatabaseFetcher
from processing.preparation.building_gdf_creator.osm_building_extractor import OSMBuildingExtractor
from processing.preparation.building_gdf_creator.user_building_extractor import UserBuildingExtractor


class BuildingManager(Config):
    """
    Manage building extraction and merging from User, OSM, and Database sources,
    prioritizing: 1. Database, 2. User, 3. OSM.
    """

    def __init__(self):
        super().__init__()
        self.load_config()

        # Extractors for building sources
        self.user_extractor = UserBuildingExtractor()
        self.osm_extractor = OSMBuildingExtractor()
        self.db_id_fetcher = BuildingDatabaseFetcher()

        # Configuration and defaults
        building_source_config = self.config.get("building_source", {})
        self.source_config = building_source_config.get("sources", {
            "osm": "OpenStreetMap",
            "user": "User",
            "db": "Database"
        })
        self.output_file_path = self.config.get("building_path", "output_buildings.geojson")
        self.source_column = self.config.get("source_config", {}).get("column_name", "building_source")

        logging.basicConfig(level=logging.INFO)

    def _remove_overlapping_osm_buildings(self, osm_gdf: gpd.GeoDataFrame,
                                          user_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Remove overlapping OSM geometries to give priority to user geometries.
        """
        if user_gdf.empty:
            logging.info("No user-provided buildings; keeping all OSM buildings.")
            return osm_gdf

        user_union = unary_union(user_gdf.geometry)
        filtered_osm_gdf = osm_gdf[~osm_gdf.geometry.intersects(user_union)]
        logging.info(f"Removed {len(osm_gdf) - len(filtered_osm_gdf)} overlapping OSM buildings.")
        return filtered_osm_gdf

    def _fetch_database_ids(self, combined_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Query the database for building IDs and prioritize the `Database` source.
        """
        if combined_gdf.empty or 'geometry' not in combined_gdf.columns:
            raise ValueError("The combined GeoDataFrame is empty or missing a geometry column.")

        # Ensure "building_source" column exists
        if self.source_column not in combined_gdf.columns:
            combined_gdf[self.source_column] = None

        combined_gdf = combined_gdf[combined_gdf.geometry.notnull()]
        db_results = self.db_id_fetcher.run(combined_gdf)

        if db_results is None or db_results.empty:
            logging.info("No matching buildings found in the database.")
            return combined_gdf

        logging.info(f"Fetched {len(db_results)} building IDs from the database.")

        # Merge using Well-Known Binary (WKB) for accurate geometry comparison
        db_results["geometry_wkb"] = db_results.geometry.apply(lambda geom: geom.wkb)
        combined_gdf["geometry_wkb"] = combined_gdf.geometry.apply(lambda geom: geom.wkb)

        merged_gdf = combined_gdf.merge(
            db_results[["geometry_wkb", "building_id"]],
            how="left",
            on="geometry_wkb"
        ).drop(columns=["geometry_wkb"])

        # Ensure `building_id` always exists in merged_gdf
        if "building_id" not in merged_gdf.columns:
            merged_gdf["building_id"] = None

        # Priority: Database > User > OSM
        merged_gdf.loc[merged_gdf["building_id"].notna(), self.source_column] = self.source_config.get("db", "Database")
        merged_gdf[self.source_column] = merged_gdf[self.source_column].fillna(self.source_config.get("user", "User"))

        logging.info("Successfully merged database building IDs with correct source prioritization.")
        return merged_gdf

    def run(self, boundaries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Main method to process buildings from multiple sources and combine them.
        """
        logging.info("Loading boundaries...")

        # Extract User buildings
        user_gdf = self.user_extractor.run(boundaries)
        if not user_gdf.empty:
            user_gdf[self.source_column] = self.source_config.get("user", "User")

        # Extract OSM buildings
        osm_gdf = self.osm_extractor.run(boundaries)
        if not osm_gdf.empty:
            osm_gdf[self.source_column] = self.source_config.get("osm", "OpenStreetMap")

        # Remove overlapping OSM buildings
        osm_gdf = self._remove_overlapping_osm_buildings(osm_gdf, user_gdf)

        # Combine User and OSM buildings
        combined_gdf = gpd.GeoDataFrame(pd.concat([user_gdf, osm_gdf], ignore_index=True), crs=user_gdf.crs)

        # Fetch and integrate Database building IDs
        final_gdf = self._fetch_database_ids(combined_gdf)

        logging.info("Processing completed successfully.")
        return final_gdf
