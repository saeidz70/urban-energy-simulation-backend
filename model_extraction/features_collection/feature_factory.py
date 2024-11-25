from config.config import Config
from model_extraction.features_collection.features.area import BuildingAreaCalculator
from model_extraction.features_collection.features.building_id import BuildingIDAssigner
from model_extraction.features_collection.features.census_id import CensusIdCalculator
from model_extraction.features_collection.features.construction_type import ConstructionType
from model_extraction.features_collection.features.cooling import Cooling
from model_extraction.features_collection.features.feature_helpers.volume import BuildingVolumeCalculator
from model_extraction.features_collection.features.gross_floor_area import GrossFloorAreaCalculator
from model_extraction.features_collection.features.heating import Heating
from model_extraction.features_collection.features.height import HeightProcess
from model_extraction.features_collection.features.hvac_type import HVACType
from model_extraction.features_collection.features.n_family import FamilyCalculator
from model_extraction.features_collection.features.n_floor import FloorProcess
from model_extraction.features_collection.features.neighbours_ids import NeighboursIds
from model_extraction.features_collection.features.net_leased_area import NetLeasedAreaCalculator
from model_extraction.features_collection.features.project_id import ProjectIdGenerator
from model_extraction.features_collection.features.tabula_id import TabulaID
from model_extraction.features_collection.features.tabula_type import TabulaType
from model_extraction.features_collection.features.tot_area_per_cens_id import TotalAreaPerCensusCalculator
from model_extraction.features_collection.features.usage import BuildingUsageProcessor
from model_extraction.features_collection.features.w2w import W2W
from model_extraction.features_collection.features.year_of_construction import YearOfConstruction


class FeatureFactory(Config):

    def project_id(self):
        project_id = ProjectIdGenerator()
        project_id.generate_project_id()

    def building_id(self):
        building_id = BuildingIDAssigner()
        building_id.assign_unique_id()

    def census_id(self):
        census_id = CensusIdCalculator()
        census_id.calculate_census_id()

    def area(self):
        filter_area = BuildingAreaCalculator()
        filter_area.process_buildings()

    def height(self):
        height_process = HeightProcess()
        height_process.process_heights()

    def volume(self):
        volume_calculator = BuildingVolumeCalculator()
        volume_calculator.process_volume_calculation()

    def n_floor(self):
        process_floor = FloorProcess()
        process_floor.process_floors()

    def gross_floor_area(self):
        gross_floor_area = GrossFloorAreaCalculator()
        gross_floor_area.run()

    def net_leased_area(self):
        net_leased_area = NetLeasedAreaCalculator()
        net_leased_area.run()

    def tot_area_per_cens_id(self):
        area_census_id = TotalAreaPerCensusCalculator()
        area_census_id.run()

    def construction_type(self):
        construction_type = ConstructionType()
        construction_type.run()

    def w2w(self):
        w2w = W2W()
        w2w.run()

    def heating(self):
        heating = Heating()
        heating.run()

    def cooling(self):
        cooling = Cooling()
        cooling.run()

    def hvac_type(self):
        hvac_type = HVACType()
        hvac_type.run()

    def tabula_type(self):
        tabula_type = TabulaType()
        tabula_type.run()

    def usage(self):
        building_usage = BuildingUsageProcessor()
        building_usage.run()

    def n_family(self):
        family_calculation = FamilyCalculator()
        family_calculation.run()

    def year_of_construction(self):
        year_of_construction = YearOfConstruction()
        year_of_construction.run()

    def neighbours_ids(self):
        neighbours_ids = NeighboursIds()
        neighbours_ids.add_neighbour_ids()

    def tabula_id(self):
        tabula_id = TabulaID()
        tabula_id.run()

    def neighbours_surfaces(self):
        pass

