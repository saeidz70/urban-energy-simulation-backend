from random import random

from model_extraction.features_collection.base_feature import BaseFeature


class Saeid(BaseFeature):

    def calculate(self, gdf, rows):
        gdf[self.feature_name] = random(self.min, self.max)
        return gdf