import geopandas as gpd

from config.config import Config


class ConstructionType(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = 'construction_type'
        self.year_of_construction_column = 'year_of_construction'
        # Load configurations
        self.building_file = self.config.get('building_path')
        self.construction_config = self.config.get('features', {}).get(self.feature_name, {})
        self.construction_periods = self.construction_config.get('construction_period', {})

    def run(self):
        """Assigns a construction type based on the year of construction."""
        buildings_gdf = self._load_building_data()

        # Ensure the year_of_construction column exists
        if self.year_of_construction_column not in buildings_gdf.columns:
            raise ValueError(f"{self.year_of_construction_column} column not found in the building data.")

        # Assign construction type based on year_of_construction
        buildings_gdf[self.feature_name] = buildings_gdf[self.year_of_construction_column].apply(
            self._get_construction_type
        )

        # Save the updated data back to the GeoJSON file
        self._save_updated_data(buildings_gdf)
        print(
            f"{self.feature_name} attribute assigned based on {self.year_of_construction_column} in {self.building_file}")

    def _load_building_data(self):
        """Loads the building data from the specified GeoJSON file."""
        if not self.building_file:
            raise ValueError("Building file path is not set in the configuration.")
        return gpd.read_file(self.building_file)

    def _get_construction_type(self, year):
        """Determines the construction type based on the year of construction."""
        for period, construction_type in self.construction_periods.items():
            start_year, end_year = map(int, period.split('-'))
            if start_year <= year <= end_year:
                return construction_type
        return None  # Return None if no matching period is found

    def _save_updated_data(self, gdf):
        """Saves the updated GeoDataFrame back to the GeoJSON file."""
        gdf.to_file(self.building_file, driver='GeoJSON')
