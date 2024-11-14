from config.config import Config
from features_collection.features.area import BuildingAreaCalculator
from features_collection.features.building_id import BuildingIDAssigner
from features_collection.features.census_id import CensusIdCalculator
from features_collection.features.construction_type import ConstructionType
from features_collection.features.cooling import Cooling
from features_collection.features.feature_helpers.volume import BuildingVolumeCalculator
from features_collection.features.gross_floor_area import GrossFloorAreaCalculator
from features_collection.features.heating import Heating
from features_collection.features.height import HeightProcess
from features_collection.features.hvac_type import HVACType
from features_collection.features.n_family import FamilyCalculator
from features_collection.features.n_floor import FloorProcess
from features_collection.features.net_leased_area import NetLeasedAreaCalculator
from features_collection.features.project_id import ProjectIdGenerator
from features_collection.features.tabula_id import TabulaAssigner
from features_collection.features.tabula_type import TabulaType
from features_collection.features.tot_area_per_cens_id import TotalAreaPerCensusCalculator
from features_collection.features.usage import BuildingUsageProcessor
from features_collection.features.w2w import W2W
from features_collection.features.year_of_construction import CensusBuiltYear


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
        # height_process.calculate_heights_from_dtm_dsm()

    def volume(self):
        volume_calculator = BuildingVolumeCalculator()
        volume_calculator.process_volume_calculation()

    def n_floor(self):
        process_floor = FloorProcess()
        process_floor.process_floors()

    def gross_floor_area(self):
        gross_floor_area = GrossFloorAreaCalculator()
        gross_floor_area.calculate_gfa()

    def net_leased_area(self):
        net_leased_area = NetLeasedAreaCalculator()
        net_leased_area.calculate_nla()

    def tot_area_per_cens_id(self):
        area_census_id = TotalAreaPerCensusCalculator()
        area_census_id.calculate_total_area_per_census()

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
        building_usage.process()
        pass

    def n_family(self):
        family_calculation = FamilyCalculator()
        family_calculation.run()
        pass

    def year_of_construction(self):
        # year_of_construction = CensusBuiltYear()
        # year_of_construction.run()
        pass

    def neighbours_ids(self):
        pass

    def neighbours_surfaces(self):
        pass

    def tabula_id(self):
        # tabula_id = TabulaAssigner()
        # tabula_id.assign_tabula_data()
        pass
