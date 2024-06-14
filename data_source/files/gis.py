import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt


class Gis:
    def __init__(self, file_path):
        self.file = file_path
        self.my_data = gpd.read_file(self.file)

    def file_columns(self):
        column = self.my_data.columns
        return column

    def file_head(self):
        head = self.my_data.head()
        return head

    def file_info(self):
        info = self.my_data.info()
        return info

    def crs_info(self):
        crs = self.my_data.crs
        return crs

    # WGS84 (EPSG:4326)
    def crs_change(self, crs):
        self.my_data.to_crs(crs)
        return "CRS Changed"

    def convert_file_format(self, new_name):
        self.my_data.to_file(f"data_source/input_files/{new_name}.geojson", driver="GeoJSON")
        return "Converted to GeoJson"

    def plot(self):
        self.my_data.plot()
        plt.show()

    def area(self):
        area = self.my_data.area
        return area

    def clip(self, polygon):
        clip_poly = gpd.GeoDataFrame.from_features(polygon)
        clipped_gdf = gpd.clip(self.my_data, clip_poly)
        print(clipped_gdf.head())
        return clipped_gdf

    def save(self, file_name):
        self.my_data.to_file(f"data_source/input_files/{file_name}.geojson", driver="GeoJSON", crs="EPSG:32632")
        return "File Saved"

if __name__ == "__main__":
    file_path1 = "data_source/input_files/Turin_1.geojson"
    # file_path2 = "data_source/input_files/polygon.geojson"
    gis1 = Gis(file_path1)
    # gis1.crs_change("EPSG:4326")
    gis1.file_columns()
    # gis2 = Gis(file_path2)
    # gis2.crs_change("EPSG:4326")
    # gis1.clip(gis2.my_data)