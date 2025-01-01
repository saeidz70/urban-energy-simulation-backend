import geopandas as gpd
import osmnx as ox

class OSMCheck:
    def __init__(self, config):
        self.config = config
        self.tags = self.config['OSM_tags']
        self.default_crs = "EPSG:4326"

        selected_boundaries_path = self.config.get('selected_boundaries')
        self.selected_boundaries = None
        if selected_boundaries_path:
            try:
                self.selected_boundaries = gpd.read_file(selected_boundaries_path).to_crs(self.default_crs)
                print("Selected boundaries loaded successfully.")
            except Exception as e:
                print(f"Error loading boundaries: {e}")

    def get_data_from_osm(self, feature, buildings_gdf):
        feature_tag = self.tags.get(feature)
        if not feature_tag:
            print(f"No OSM tag found for feature '{feature}'. Skipping query.")
            return None

        polygon = self.get_polygon()
        if polygon is None:
            print("No valid polygon data found for the OSM query.")
            return None

        osm_gdf = self.fetch_osm_data(feature_tag, polygon)
        if osm_gdf is None or osm_gdf.empty:
            print("No valid OSM data retrieved.")
            return None

        osm_gdf = osm_gdf.to_crs(buildings_gdf.crs)
        return self.spatial_join(osm_gdf, buildings_gdf, feature, feature_tag)

    def fetch_osm_data(self, feature_tag, polygon):
        print("Fetching OSM data using osmnx...")
        tags = {"building": True, feature_tag: True}
        osm_gdf = ox.features_from_polygon(polygon, tags=tags)
        print(f"Retrieved {len(osm_gdf)} records from OSM.")
        return osm_gdf

    def spatial_join(self, osm_gdf, buildings_gdf, feature, feature_tag):
        print("Performing spatial join between OSM data and user_building_file...")
        try:
            matched_gdf = gpd.sjoin(
                osm_gdf,
                buildings_gdf,
                how="inner",
                predicate="intersects",
                lsuffix='_osm',
                rsuffix='_bld'
            )
            print("Spatial join successful.")

            # Check for the OSM feature column
            osm_feature_column = feature_tag
            if osm_feature_column in matched_gdf.columns:
                # Rename the OSM column to match the feature in buildings_gdf
                matched_gdf = matched_gdf[['geometry', osm_feature_column]].rename(
                    columns={osm_feature_column: feature})
            elif f"{osm_feature_column}__osm" in matched_gdf.columns:
                # If the column has the "__osm" suffix, use it
                matched_gdf = matched_gdf[['geometry', f"{osm_feature_column}__osm"]].rename(
                    columns={f"{osm_feature_column}__osm": feature})
            else:
                print(
                    f"Expected OSM feature column '{osm_feature_column}' or '{osm_feature_column}__osm' not found. "
                    f"Available columns: {matched_gdf.columns}")
                return None

            # Drop rows with NaN values in the feature column
            matched_gdf.dropna(subset=[feature], inplace=True)

            if matched_gdf.empty:
                print("No matching records found after join.")
                return None

            return matched_gdf
        except Exception as e:
            print(f"Error during spatial join: {e}")
            return None

    def get_polygon(self):
        if self.selected_boundaries is not None:
            return self.selected_boundaries.iloc[0].geometry
        print("No polygon data available.")
        return None
