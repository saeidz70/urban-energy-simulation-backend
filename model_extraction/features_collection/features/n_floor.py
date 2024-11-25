import geopandas as gpd

from config.config import Config
from model_extraction.data_manager.utility import UtilityProcess


class FloorProcess(Config):
    def __init__(self):
        super().__init__()
        self.feature_name = 'n_floor'
        self.height_column = 'height'
        self.building_file = self.config['building_path']
        self.n_floor_config = self.config.get("features", {}).get(self.feature_name, {})
        self.avg_floor_height = self.n_floor_config.get("avg_floor_height", 3.3)
        self.min_n_floor = self.n_floor_config.get("min", 1)
        self.max_n_floor = self.n_floor_config.get("max", 100)
        self.data_type = self.n_floor_config.get("type", "int")
        self.utility = UtilityProcess()

    def process_floors(self):
        """Main method to process the number of floors."""
        buildings_gdf = self._load_building_data()

        buildings_gdf = self._initialize_column(buildings_gdf, self.feature_name)

        buildings_gdf = self._retrieve_floors_from_utility(buildings_gdf)

        buildings_gdf = self._calculate_missing_floors(buildings_gdf)

        buildings_gdf = self._validate_floor_values(buildings_gdf)

        self._save_building_data(buildings_gdf)
        return buildings_gdf

    def _load_building_data(self):
        """Load building data from the configured file path."""
        print(f"Loading building data from {self.building_file}")
        return gpd.read_file(self.building_file)

    def _initialize_column(self, gdf, column_name):
        """Ensure a specified column exists in the GeoDataFrame."""
        if column_name not in gdf.columns:
            print(f"Initializing column '{column_name}' with None.")
            gdf[column_name] = None
        return gdf

    def _retrieve_floors_from_utility(self, gdf):
        """Retrieve and update 'n_floor' data using the UtilityProcess."""
        n_floor_gdf = self.utility.process_feature(self.feature_name, gdf)
        if n_floor_gdf is not None and not n_floor_gdf.empty:
            print(f"Merging retrieved '{self.feature_name}' data into the building GeoDataFrame.")
            gdf = gdf.merge(
                n_floor_gdf[['geometry', self.feature_name]],
                on='geometry',
                how='left',
                suffixes=('', '_updated')
            )
            gdf[self.feature_name] = gdf[self.feature_name].fillna(gdf[f"{self.feature_name}_updated"])
            gdf.drop(columns=[f"{self.feature_name}_updated"], inplace=True)
        return gdf

    def _calculate_missing_floors(self, gdf):
        """Calculate missing 'n_floor' values using the 'height' column."""
        if self.height_column in gdf.columns:
            missing_floors = gdf[self.feature_name].isnull()
            if missing_floors.any():
                print(f"Calculating missing {self.feature_name} values from {self.height_column}.")
                gdf.loc[missing_floors, self.feature_name] = (
                        gdf.loc[missing_floors, self.height_column] / self.avg_floor_height
                ).round().fillna(0).astype(int)
        return gdf

    def _validate_floor_values(self, gdf):
        """Ensure 'n_floor' values are within the configured limits."""
        print(f"Validating {self.feature_name} values between {self.min_n_floor} and {self.max_n_floor}.")
        gdf[self.feature_name] = gdf[self.feature_name].clip(self.min_n_floor, self.max_n_floor)
        gdf[self.feature_name] = gdf[self.feature_name].astype(self.data_type)
        return gdf

    def _save_building_data(self, gdf):
        """Save the updated GeoDataFrame to the configured file path."""
        print(f"Saving updated building data to {self.building_file}.")
        columns = [self.feature_name] + [col for col in gdf.columns if col != self.feature_name]
        gdf = gdf[columns]
        gdf.to_file(self.building_file, driver='GeoJSON')
