from matplotlib import pyplot as plt


class GdfUtils:
    def __init__(self, gdf):
        self.gdf = gdf

    def save_geodataframe(self, path):
        self.gdf.to_file(path, driver='GeoJSON')

    def to_crs(self, epsg):
        self.gdf = self.gdf.to_crs(epsg=epsg)
        return self.gdf

    def plot(self):
        self.gdf.plot()
        plt.show()
        return self.gdf
