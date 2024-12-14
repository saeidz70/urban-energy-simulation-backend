from config.config import Config
from model_extraction.features_collection.features.area import Area
from model_extraction.features_collection.features.building_id import BuildingID
from model_extraction.features_collection.features.census_id import CensusId
from model_extraction.features_collection.features.construction_type import ConstructionType
from model_extraction.features_collection.features.cooling import Cooling
from model_extraction.features_collection.features.feature_helpers.volume import Volume
from model_extraction.features_collection.features.gross_floor_area import GrossFloorArea
from model_extraction.features_collection.features.heating import Heating
from model_extraction.features_collection.features.height import Height
from model_extraction.features_collection.features.hvac_type import HVACType
from model_extraction.features_collection.features.n_family import NumberOfFamily
from model_extraction.features_collection.features.n_floor import NumberOfFloors
from model_extraction.features_collection.features.neighbours_ids import NeighboursIds
from model_extraction.features_collection.features.net_leased_area import NetLeasedArea
from model_extraction.features_collection.features.tabula_id import TabulaID
from model_extraction.features_collection.features.tabula_type import TabulaType
from model_extraction.features_collection.features.tot_area_per_cens_id import TotalAreaPerCensusId
from model_extraction.features_collection.features.usage import Usage
from model_extraction.features_collection.features.w2w import W2W
from model_extraction.features_collection.features.year_of_construction import YearOfConstruction


class FeatureFactory(Config):
    def __init__(self):
        super().__init__()
        self.feature_classes = {
            "building_id": BuildingID,
            "census_id": CensusId,
            "area": Area,
            "height": Height,
            "volume": Volume,
            "n_floor": NumberOfFloors,
            "gross_floor_area": GrossFloorArea,
            "net_leased_area": NetLeasedArea,
            "tot_area_per_cens_id": TotalAreaPerCensusId,
            "construction_type": ConstructionType,
            "w2w": W2W,
            "heating": Heating,
            "cooling": Cooling,
            "hvac_type": HVACType,
            "tabula_type": TabulaType,
            "usage": Usage,
            "n_family": NumberOfFamily,
            "year_of_construction": YearOfConstruction,
            "neighbours_ids": NeighboursIds,
            "tabula_id": TabulaID,
        }

    def run_feature(self, feature_name, gdf):
        feature_class = self.feature_classes.get(feature_name)
        if not feature_class:
            print(f"Warning: Feature '{feature_name}' not found.")
            return gdf

        try:
            # Instantiate the feature class and call its `run` method
            feature_instance = feature_class()
            print(f"Running feature extraction for '{feature_name}'.")

            # Dynamically call the run method
            if hasattr(feature_instance, 'run'):
                return feature_instance.run(gdf, feature_name)
            else:
                # Fallback to BaseFeature's run
                return super(feature_class, feature_instance).run(gdf, feature_name)
        except Exception as e:
            print(f"Error while running feature '{feature_name}': {e}")
            raise
