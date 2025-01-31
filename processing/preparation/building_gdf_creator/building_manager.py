import logging
import os

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

from config.config import Config
from processing.preparation.building_gdf_creator.db_b_id_fetcher import BuildingDatabaseFetcher
from processing.preparation.building_gdf_creator.osm_building_extractor import OSMBuildingExtractor
from processing.preparation.building_gdf_creator.user_building_extractor import UserBuildingExtractor


class BuildingManager(Config):
    """
    Manage building extraction and merging from User, OSM, and Database sources,
    with priority: 1. Database, 2. User, 3. OSM.
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

    def _load_boundary(self, boundaries: gpd.GeoDataFrame) -> Polygon:
        """
        Combine and validate all boundary geometries into a single valid Polygon.
        """
        if boundaries.empty:
            raise ValueError("Boundary GeoDataFrame is empty.")

        logging.info(f"Processing {len(boundaries)} boundary geometries...")
        valid_boundaries = boundaries[boundaries.geometry.is_valid].geometry

        if valid_boundaries.empty:
            raise ValueError("No valid boundary geometries found!")

        combined_boundary = unary_union(valid_boundaries)

        # If result is MultiPolygon, choose the largest Polygon
        if isinstance(combined_boundary, MultiPolygon):
            logging.warning("Boundary is a MultiPolygon, selecting the largest polygon.")
            combined_boundary = max(combined_boundary.geoms, key=lambda p: p.area)

        logging.info("Successfully combined boundary geometries.")
        return combined_boundary

    def _remove_overlapping_osm_buildings(self, osm_gdf: gpd.GeoDataFrame,
                                          user_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Remove overlapping OSM geometries, prioritizing user-provided buildings.
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

        logging.info(f"Querying the database for {len(combined_gdf)} geometries...")

        # Ensure "building_source" column exists
        if self.source_column not in combined_gdf.columns:
            combined_gdf[self.source_column] = None

        combined_gdf = combined_gdf[combined_gdf.geometry.notnull()]
        db_results = self.db_id_fetcher.run(combined_gdf)

        if db_results is None or db_results.empty:
            logging.info("No matching buildings found in the database.")
            return combined_gdf

        logging.info(f"Fetched {len(db_results)} building IDs from the database.")

        # Ensure both datasets have a common format
        db_results["geometry_wkb"] = db_results.geometry.apply(lambda geom: geom.wkb)
        combined_gdf["geometry_wkb"] = combined_gdf.geometry.apply(lambda geom: geom.wkb)

        # Merge database results with the combined dataset
        merged_gdf = combined_gdf.merge(
            db_results[["geometry_wkb", "building_id"]],
            how="left",
            on="geometry_wkb"
        ).drop(columns=["geometry_wkb"])

        # Ensure `building_id` exists in merged_gdf
        if "building_id" not in merged_gdf.columns:
            merged_gdf["building_id"] = None

        # Set source priority: 1. Database, 2. User, 3. OSM
        merged_gdf.loc[merged_gdf["building_id"].notna(), self.source_column] = self.source_config.get("db", "Database")
        merged_gdf[self.source_column] = merged_gdf[self.source_column].fillna(self.source_config.get("user", "User"))

        logging.info("Successfully merged database building IDs with correct source prioritization.")
        return merged_gdf

    def _save_buildings(self, buildings_gdf: gpd.GeoDataFrame):
        """
        Save the final GeoDataFrame to a GeoJSON file.
        """
        if buildings_gdf.empty:
            raise ValueError("The final GeoDataFrame is empty and cannot be saved.")

        logging.info(f"Saving {len(buildings_gdf)} buildings to {self.output_file_path}...")

        # Ensure the output directory exists
        output_dir = os.path.dirname(self.output_file_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        buildings_gdf.to_file(self.output_file_path, driver="GeoJSON")
        logging.info("Building data saved successfully.")

    def run(self, boundaries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Main method to process buildings from multiple sources and combine them.
        """
        logging.info("Loading boundaries...")
        boundary_polygon = self._load_boundary(boundaries)

        # Step 1: Extract User buildings
        user_gdf = self.user_extractor.run(boundary_polygon)
        if not user_gdf.empty:
            user_gdf[self.source_column] = self.source_config.get("user", "User")

        # Step 2: Extract OSM buildings
        osm_gdf = self.osm_extractor.run(boundary_polygon)
        if not osm_gdf.empty:
            osm_gdf[self.source_column] = self.source_config.get("osm", "OpenStreetMap")

        # Step 3: Remove overlapping OSM buildings
        osm_gdf = self._remove_overlapping_osm_buildings(osm_gdf, user_gdf)

        # Step 4: Combine User and OSM buildings
        combined_gdf = gpd.GeoDataFrame(pd.concat([user_gdf, osm_gdf], ignore_index=True), crs=user_gdf.crs)

        # Step 5: Fetch and integrate Database building IDs
        final_gdf = self._fetch_database_ids(combined_gdf)

        # Step 6: Save the final output
        self._save_buildings(final_gdf)

        logging.info("Processing completed successfully.")
        return final_gdf
