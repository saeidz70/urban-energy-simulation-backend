import geopandas as gpd

from config.config import Config


class GrossFloorAreaCalculator(Config):
    """
    A class to calculate the Gross Floor Area (GFA) for buildings based on their area and number of floors.
    """

    def __init__(self):
        super().__init__()
        self.feature_name = 'gross_floor_area'
        self.area_column = 'area'
        self.n_floor_column = 'n_floor'
        self.building_file = self.config['building_path']
        self.gross_floor_area_config = self.config.get('features', {}).get(self.feature_name, {})
        self.data_type = self.gross_floor_area_config.get("type", "float")

    def load_building_data(self):
        """Loads the building data from the GeoJSON file."""
        return gpd.read_file(self.building_file)

    def validate_columns(self, buildings_gdf):
        """
        Validates that the required columns exist in the data.
        Raises:
            ValueError: If the required columns are missing.
        """
        missing_columns = [
            col for col in [self.area_column, self.n_floor_column]
            if col not in buildings_gdf.columns
        ]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    def calculate_gfa(self, buildings_gdf):
        """
        Calculates the Gross Floor Area (GFA) based on area and number of floors.
        Ensures the calculation is added to the data as a new column.
        """
        buildings_gdf[self.feature_name] = buildings_gdf[self.area_column] * buildings_gdf[self.n_floor_column]
        return buildings_gdf

    def format_gfa_column(self, buildings_gdf):
        """
        Rounds and ensures the data type of the GFA column is consistent with configuration.
        Helps maintain data integrity.
        """
        buildings_gdf[self.feature_name] = (
            buildings_gdf[self.feature_name].round(2).astype(self.data_type)
        )
        return buildings_gdf

    def reorder_columns(self, buildings_gdf):
        """
        Moves the GFA column next to the area column for logical organization.
        Enhances data readability.
        """
        columns = buildings_gdf.columns.tolist()
        area_index = columns.index(self.area_column) + 1
        columns.insert(area_index, columns.pop(columns.index(self.feature_name)))
        return buildings_gdf[columns]

    def save_data(self, buildings_gdf):
        """
        Saves the updated building data to the specified GeoJSON file.
        """
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"Updated data saved to {self.building_file}")

    def run(self):
        """Executes the GFA calculation workflow in sequential steps."""
        buildings_gdf = self.load_building_data()
        self.validate_columns(buildings_gdf)  # Ensure required columns exist before processing
        buildings_gdf = self.calculate_gfa(buildings_gdf)  # Perform the GFA calculation
        buildings_gdf = self.format_gfa_column(buildings_gdf)  # Format the GFA column
        buildings_gdf = self.reorder_columns(buildings_gdf)  # Reorder columns for better readability
        self.save_data(buildings_gdf)  # Save the processed data
        return buildings_gdf
