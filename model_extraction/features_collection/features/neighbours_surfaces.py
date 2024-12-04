from model_extraction.features_collection.base_feature import BaseFeature


class NeighboursSurfaces(BaseFeature):
    def __init__(self):
        super().__init__()
        self.feature_name = 'neighbours_surfaces'
        pass
