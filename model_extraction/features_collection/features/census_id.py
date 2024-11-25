import geopandas as gpd

from config.config import Config


class CensusIdCalculator(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = 'census_id'
        # Load necessary paths and configuration
        self.building_file = self.config.get('building_path')
        self.census_config = self.config.get('features', {}).get(self.feature_name, {})
        self.census_id_column = self.census_config.get('census_id_column',
                                                       'SEZ2011')  # Default column name is 'SEZ2011'

    def calculate_census_id(self):
        """Calculates and updates the census_id in the GeoJSON file."""
        # Load building data
        buildings_gdf = self._load_buildings()

        # Validate the census_id column existence
        self._validate_column_exists(buildings_gdf, self.census_id_column)

        # Extract census_id into a new column
        buildings_gdf[self.feature_name] = buildings_gdf[self.census_id_column]

        # Reorder columns to make 'census_id' the first column
        buildings_gdf = self._reorder_columns(buildings_gdf, self.feature_name)

        # Save the updated GeoJSON file
        self._save_updated_file(buildings_gdf)
        print(f"{self.feature_name} data saved to {self.building_file}")

        return buildings_gdf

    def _load_buildings(self):
        """Loads the building data from the specified GeoJSON file."""
        if not self.building_file:
            raise ValueError("Building file path is not set in the configuration.")
        return gpd.read_file(self.building_file)

    def _validate_column_exists(self, gdf, column_name):
        """Ensures the specified column exists in the GeoDataFrame."""
        if column_name not in gdf.columns:
            raise ValueError(f"'{column_name}' column not found in the building data.")

    def _reorder_columns(self, gdf, target_column):
        """Reorders the columns to make the target column the first column."""
        columns = [target_column] + [col for col in gdf.columns if col != target_column]
        return gdf.reindex(columns=columns)

    def _save_updated_file(self, gdf):
        """Saves the updated GeoDataFrame back to the GeoJSON file."""
        gdf.to_file(self.building_file, driver='GeoJSON')
