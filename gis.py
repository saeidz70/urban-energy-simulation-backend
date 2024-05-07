import geopandas as gpd


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

    def convert(self, new_name):
        self.my_data.to_file(f"Files/{new_name}.geojson", driver="GeoJSON")
        return "Converted to GeoJson"

    def plot(self):
        self.my_data.plot()
        return "Plotting"


if __name__ == "__main__":
    file_path = "Files/R01_11_WGS84.shp"
    gis = Gis(file_path)
    print(gis.file_info())
