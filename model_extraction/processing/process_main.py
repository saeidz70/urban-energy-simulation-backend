from model_extraction.processing.ArchetypeAssigner import BuildingArchetypeAssigner
from model_extraction.processing.built_year.census_built_year import CensusBuiltYear
from model_extraction.processing.built_year.osm_built_year import OsmBuiltYear
from model_extraction.processing.census_information.building_usage import BuildingUsagePredictor
from model_extraction.processing.geometry_calculation.volume_calculator import BuildingVolumeCalculator
from model_extraction.processing.height_processing.building_kriging_filler import BuildingKrigingFiller
from model_extraction.processing.height_processing.height_process import HeightProcess


class ProcessMain:
    def __init__(self, config_path):
        self.config_path = config_path

    def processing_height(self):
        height_process = HeightProcess(self.config_path)
        height_process.process_height()
        # height_process.calculate_heights_from_dtm_dsm()

    def building_kriging_filler(self):
        building_kriging_filler = BuildingKrigingFiller(self.config_path)
        building_kriging_filler.process_filling()

    def process_volume(self):
        volume_calculator = BuildingVolumeCalculator(self.config_path)
        volume_calculator.process_volume_calculation()

    def building_usage(self):
        building_usage = BuildingUsagePredictor(self.config_path)
        building_usage.run()

    def process_census_built_year(self):
        process_census_built_year = CensusBuiltYear(self.config_path)
        process_census_built_year.assign_built_year()

    def process_osm_built_year(self):
        osm_built_year = OsmBuiltYear(self.config_path)
        osm_built_year.run()

    def process_archetype(self):
        archetype_assigner = BuildingArchetypeAssigner(self.config_path)
        processed_buildings_gdf = archetype_assigner.process_buildings()
        print(processed_buildings_gdf.head())



    # def process_areas(self):
    #     process_areas = ProcessAreas(self.config_path)
    #     process_areas.calculate_building_areas()
    #
    # def process_floor(self):
    #     process_floor = FloorProcess(self.config_path)
    #     process_floor.process_floors()

    # def processing_census(self):
    #     census_process = ProcessCensus(self.config_path)
    #     census_process.make_selected_census()
    #     census_process.merge_buildings_census()
    #
