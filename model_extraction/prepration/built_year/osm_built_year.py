import requests


class OSMDataFetcher:
    def __init__(self, base_url="https://www.openstreetmap.org/api/0.6/way/"):
        self.base_url = base_url

    def fetch_construction_year(self, osm_id):
        osm_id_numeric = osm_id[1] if isinstance(osm_id, tuple) else osm_id
        # Fetch construction year from OSM API
        url = f"{self.base_url}{osm_id_numeric}.json"
        print(f"Fetching data from URL: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {data}")
            if 'elements' in data and len(data['elements']) > 0:
                element = data['elements'][0]
                tags = element.get('tags', {})
                built_year = (
                        tags.get('start_date') or
                        tags.get('building:year') or
                        tags.get('construction') or
                        tags.get('year_built') or
                        tags.get('completed') or
                        tags.get('opening_date') or
                        tags.get('date')
                )
                print(f"OSM ID: {osm_id_numeric}, Built Year: {built_year}")
                return built_year
        else:
            print(f"Failed to fetch data for OSM ID: {osm_id_numeric}, Status Code: {response.status_code}")
        return None
