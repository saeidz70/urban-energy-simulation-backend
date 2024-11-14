import geopandas as gpd
import json
from config.config import Config


class OutputFileGenerator(Config):
    def __init__(self):
        super().__init__()
        self.building_file = self.config.get('building_path')
        self.output_file = self.config.get('output_path')
        self.default_epsg_code = self.config.get("DEFAULT_EPSG_CODE", 32632)
        self.default_crs = f"EPSG:{self.config.get('DEFAULT_CRS', 4326)}"
        self.features = set(self.config["features"].keys())
        self.project_info = self.config.get('project_info', {})  # Ensure default if not specified

    def validate_crs(self, gdf):
        # Check if CRS matches the configured EPSG code
        if gdf.crs is None:
            print("No CRS found in building data; setting to default CRS.")
            gdf.set_crs(self.default_crs, inplace=True)
        elif gdf.crs.to_string() != f"EPSG:{self.default_epsg_code}":
            print(f"CRS mismatch. Reprojecting to EPSG:{self.default_epsg_code}.")
            gdf = gdf.to_crs(epsg=self.default_epsg_code)
        return gdf

    def filter_columns(self, gdf):
        # Keep only the columns that match the features in the config
        matching_columns = self.features.intersection(gdf.columns)
        filtered_gdf = gdf[list(matching_columns)]
        return filtered_gdf

    def generate_output_file(self):
        # Load building data
        buildings_gdf = gpd.read_file(self.building_file)

        # Validate CRS
        buildings_gdf = self.validate_crs(buildings_gdf)

        # Filter columns based on config features
        filtered_gdf = self.filter_columns(buildings_gdf)

        # Convert GeoDataFrame to JSON
        json_result = json.loads(filtered_gdf.to_json())

        # Add project info to the GeoJSON
        json_result['project_info'] = self.project_info

        # Write the final GeoJSON to a file
        with open(self.output_file, 'w') as f:
            json.dump(json_result, f, indent=4)

        print(f"Output file generated and saved to {self.output_file}")
