import os
import geopandas as gpd
from config.config import Config
from features_collection.features.feature_helpers.dsm_height_calculator import DtmDsmHeightCalculator
from model_extraction.data_manager.utility import UtilityProcess
from features_collection.features.feature_helpers.kriging_filler import KrigingFiller


class HeightProcess(Config):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.building_file = self.config.get('building_path')
        self.utility = UtilityProcess()
        self.kriging_filler = KrigingFiller()

    def process_heights(self):
        # Load building data and check for existence
        print(f"Attempting to load building file from path: {self.building_file}")
        if not os.path.exists(self.building_file):
            raise FileNotFoundError(f"Building file not found at path: {self.building_file}")

        buildings_gdf = gpd.read_file(self.building_file)
        print("Building data loaded successfully.")

        # Ensure 'height' column exists
        if 'height' not in buildings_gdf.columns:
            print("No 'height' column found; initializing it to None.")
            buildings_gdf['height'] = None

        # Process height using DTM/DSM if in baseline scenario
        scenario_list = self.config.get("project_info", {}).get("scenarioList", [])
        print(f"Scenario list from config: {scenario_list}")
        # if "baseline" in scenario_list:
        #     buildings_gdf = self.process_dtm_dsm_height(buildings_gdf)

        # Retrieve 'height' data using UtilityProcess if needed
        height_gdf = self.utility.process_feature('height', buildings_gdf) if buildings_gdf[
            'height'].isnull().any() else None
        if height_gdf is not None and not height_gdf.empty:
            print("Updating heights using UtilityProcess data.")
            buildings_gdf = self.update_height_column(buildings_gdf, height_gdf)

        # Fill remaining missing heights using KrigingFiller
        print("Filling any remaining missing height values.")
        self.fill_missing_heights(buildings_gdf)

        # Reorder and save the file
        print("Saving the processed building data.")
        self.save_building_data(buildings_gdf)
        return buildings_gdf

    def process_dtm_dsm_height(self, buildings_gdf):
        dtm_file = self.config.get("dtm_path")
        dsm_file = self.config.get("dsm_path")

        # Check DTM/DSM paths
        print(f"Checking DTM and DSM file paths:\nDTM: {dtm_file}\nDSM: {dsm_file}")
        if dtm_file and dsm_file and os.path.exists(dtm_file) and os.path.exists(dsm_file):
            print("Both DTM and DSM files found. Proceeding with height calculation.")
            dtm_dsm_calculator = DtmDsmHeightCalculator()

            # Load DTM and DSM data before calculating building heights
            dtm_dsm_calculator.load_data()

            # Calculate heights
            return dtm_dsm_calculator.calculate_building_heights(buildings_gdf)
        else:
            print("DTM or DSM path missing or invalid; skipping DTM/DSM height processing.")
            return buildings_gdf

    def update_height_column(self, buildings_gdf, height_gdf):
        # Merge the 'height' values from height_gdf into buildings_gdf
        print("Merging UtilityProcess height data into buildings_gdf.")
        buildings_gdf = buildings_gdf.merge(
            height_gdf[['geometry', 'height']], on='geometry', how='left', suffixes=('', '_updated')
        )
        buildings_gdf['height'] = buildings_gdf['height'].fillna(buildings_gdf['height_updated'])
        buildings_gdf.drop(columns=['height_updated'], inplace=True)
        return buildings_gdf

    def fill_missing_heights(self, buildings_gdf):
        missing_height_mask = buildings_gdf['height'].isnull()
        if missing_height_mask.any():
            print("Filling missing height values using Kriging interpolation...")
            interpolated_values = self.kriging_filler.fill_missing_values(buildings_gdf, 'height')
            if interpolated_values is not None:
                buildings_gdf.loc[missing_height_mask, 'height'] = interpolated_values
                print("Kriging interpolation successful.")
            else:
                print("Kriging interpolation failed; consider alternative filling methods.")
        else:
            print("No missing height values found; skipping Kriging interpolation.")

    def save_building_data(self, buildings_gdf):
        # Ensure 'height' column is first and save the file
        columns = ['height'] + [col for col in buildings_gdf.columns if col != 'height']
        buildings_gdf = buildings_gdf[columns]
        buildings_gdf.to_file(self.building_file, driver='GeoJSON')
        print(f"Height data processed and saved to {self.building_file}.")