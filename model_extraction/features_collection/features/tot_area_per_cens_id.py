import geopandas as gpd

from config.config import Config


class TotalAreaPerCensusCalculator(Config):
    """Calculates the total building area for each census section."""

    def __init__(self):
        super().__init__()
        self.feature_name = "tot_area_per_cens_id"
        self.census_id_column = "census_id"
        self.area_column = "area"
        self.building_file = self.config.get('building_path')
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})
        self.data_type = self.feature_config.get('type', 'float')

    def load_building_data(self):
        """Loads the building GeoDataFrame from the specified file."""
        try:
            return gpd.read_file(self.building_file)
        except Exception as e:
            raise RuntimeError(f"Error loading building file: {e}")

    def validate_columns(self, buildings_gdf):
        """Ensures required columns exist in the GeoDataFrame."""
        missing_columns = [
            col for col in [self.census_id_column, self.area_column]
            if col not in buildings_gdf.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    def calculate_total_area(self, buildings_gdf):
        """Calculates total area per census ID and adds it to the GeoDataFrame."""
        # Remove existing total area column to ensure fresh calculation
        if self.feature_name in buildings_gdf.columns:
            buildings_gdf.drop(columns=[self.feature_name], inplace=True)

        # Group by census ID and sum the area
        total_area = (
            buildings_gdf.groupby(self.census_id_column)[self.area_column]
            .sum()
            .reset_index(name=self.feature_name)
        )

        # Merge the calculated total area back to the original GeoDataFrame
        return buildings_gdf.merge(total_area, on=self.census_id_column, how='left')

    def reorder_columns(self, buildings_gdf):
        """Reorders columns to place the new total area column after the census ID column."""
        columns = buildings_gdf.columns.tolist()
        target_index = columns.index(self.census_id_column) + 1
        columns.insert(target_index, columns.pop(columns.index(self.feature_name)))
        return buildings_gdf[columns]

    def save_updated_data(self, buildings_gdf):
        """Saves the updated GeoDataFrame to the specified file."""
        try:
            buildings_gdf.to_file(self.building_file, driver='GeoJSON')
            print(f"Total area per census section saved to {self.building_file}")
        except Exception as e:
            raise RuntimeError(f"Error saving data to file: {e}")

    def run(self):
        """Executes the process of calculating total area per census ID."""
        try:
            buildings_gdf = self.load_building_data()
            self.validate_columns(buildings_gdf)
            buildings_gdf = self.calculate_total_area(buildings_gdf)
            buildings_gdf = self.reorder_columns(buildings_gdf)
            self.save_updated_data(buildings_gdf)
        except Exception as e:
            print(f"Error during calculation: {e}")
            raise
