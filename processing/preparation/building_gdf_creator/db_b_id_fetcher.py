import logging

import geopandas as gpd
import requests
from shapely.geometry import shape, mapping

from config.config import Config


class BuildingDatabaseFetcher(Config):
    """Fetch building IDs from the database and update sources while keeping GeoJSON format."""

    def __init__(self):
        super().__init__()
        self.load_config()
        self.db_url = self.config.get("db_building_id_url")
        self.headers = self.config.get("database_headers", {})
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"

        # Load building source configurations
        building_source_config = self.config.get("building_source", {})
        self.source_config = building_source_config.get("sources", {
            "osm": "OpenStreetMap",
            "user": "User",
            "db": "Database"
        })

        logging.basicConfig(level=logging.INFO)

    def run(self, buildings_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Fetch building IDs, merge results, update source, and return a GeoDataFrame."""

        if buildings_gdf.empty or "geometry" not in buildings_gdf.columns:
            logging.warning("Input GeoDataFrame is empty or missing geometry.")
            return buildings_gdf  # Return original GeoDataFrame as is

        # Ensure valid geometries and correct CRS
        buildings_gdf = buildings_gdf[buildings_gdf.geometry.notnull()]
        if buildings_gdf.crs and buildings_gdf.crs.to_string() != self.default_crs:
            buildings_gdf = buildings_gdf.to_crs(self.default_crs)

        # Ensure "building_source" column exists
        if "building_source" not in buildings_gdf.columns:
            buildings_gdf["building_source"] = None  # Default to None

        # Prepare API payload
        payload = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": mapping(geom)} for geom in buildings_gdf.geometry]
        }

        logging.debug("Sending request to database...")
        try:
            response = requests.post(self.db_url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            results = response.json().get("results", [])

            if not results:
                logging.info("No matching buildings found in the database.")
                return buildings_gdf  # Return original GeoDataFrame if no matches found

            # Process valid results
            db_results = gpd.GeoDataFrame([
                {"geometry": shape(res["geometry"]), "building_id": res.get("building_id")}
                for res in results if res.get("geometry")
            ], crs=self.default_crs)

            # Ensure `building_id` column exists in db_results
            if "building_id" not in db_results.columns:
                db_results["building_id"] = None
            db_results["building_id"] = db_results["building_id"].astype("string")

            if db_results.empty:
                return buildings_gdf  # No valid results, return original data

            # Merge using Well-Known Binary (WKB) for accurate geometry comparison
            db_results["geometry_wkb"] = db_results.geometry.apply(lambda geom: geom.wkb)
            buildings_gdf["geometry_wkb"] = buildings_gdf.geometry.apply(lambda geom: geom.wkb)

            merged_gdf = buildings_gdf.merge(
                db_results[["geometry_wkb", "building_id"]],
                how="left",
                on="geometry_wkb"
            ).drop(columns=["geometry_wkb"])

            # Ensure `building_id` always exists in merged_gdf
            if "building_id" not in merged_gdf.columns:
                merged_gdf["building_id"] = None

            # Assign "Database" source where building_id is found
            merged_gdf.loc[merged_gdf["building_id"].notna(), "building_source"] = self.source_config.get("db",
                                                                                                          "Database")

            logging.info(f"Merged {len(db_results)} buildings with database IDs and updated sources.")

            return merged_gdf  # ✅ Returns a valid GeoDataFrame following GeoJSON rules

        except requests.exceptions.RequestException as e:
            logging.error(f"Database request failed: {e}")
            return buildings_gdf  # Return original GeoDataFrame on failure
