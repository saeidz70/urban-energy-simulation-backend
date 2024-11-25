import geopandas as gpd

from config.config import Config


class NetLeasedAreaCalculator(Config):
    """Calculates Net Leased Area (NLA) for buildings."""

    def __init__(self):
        super().__init__()
        self.feature_name = 'net_leased_area'
        self.gross_floor_area_column = 'gross_floor_area'
        self.building_file = self.config.get('building_path')
        self.feature_config = self.config.get('features', {}).get(self.feature_name, {})
        self.data_type = self.feature_config.get("type", "float")

    def load_building_data(self):
        """Loads the building data from the GeoJSON file."""
        try:
            return gpd.read_file(self.building_file)
        except Exception as e:
            raise RuntimeError(f"Error loading building file: {e}")

    def validate_and_calculate_nla(self, buildings_gdf):
        """
        Validates the required columns and calculates the Net Leased Area (NLA).
        Ensures calculated values are rounded to 2 decimal places and match the expected data type.
        """
        if self.gross_floor_area_column not in buildings_gdf.columns:
            raise ValueError(f"Column '{self.gross_floor_area_column}' not found in the data.")

        # Calculate NLA and round to 2 decimal places
        buildings_gdf[self.feature_name] = (
                buildings_gdf[self.gross_floor_area_column] * 0.8
        ).round(2)

        # Ensure data type consistency
        try:
            buildings_gdf[self.feature_name] = buildings_gdf[self.feature_name].astype(self.data_type)
        except Exception as e:
            raise ValueError(f"Error converting '{self.feature_name}' to type {self.data_type}: {e}")

        return buildings_gdf

    def reorder_columns(self, buildings_gdf):
        """
        Reorders columns to place the new NLA column immediately
        after the Gross Floor Area (GFA) column.
        """
        columns = buildings_gdf.columns.tolist()
        area_index = columns.index(self.gross_floor_area_column) + 1
        if self.feature_name in columns:
            columns.insert(area_index, columns.pop(columns.index(self.feature_name)))
        return buildings_gdf[columns]

    def save_updated_data(self, buildings_gdf):
        """Saves the updated GeoJSON data back to the file."""
        try:
            buildings_gdf.to_file(self.building_file, driver='GeoJSON')
            print(f"Updated data with '{self.feature_name}' saved to {self.building_file}")
        except Exception as e:
            raise RuntimeError(f"Error saving data to file: {e}")

    def run(self):
        """Executes the NLA calculation process."""
        try:
            buildings_gdf = self.load_building_data()
            buildings_gdf = self.validate_and_calculate_nla(buildings_gdf)
            buildings_gdf = self.reorder_columns(buildings_gdf)
            self.save_updated_data(buildings_gdf)
        except Exception as e:
            print(f"Error during NLA calculation: {e}")
            raise
