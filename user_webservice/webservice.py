import cherrypy
import json
from cherrypy import response
from config.config import Config
from user_webservice.helper import DataHelper  # Assuming helper is correctly set up here


# Base server class with shared configuration and helper
class BaseServer(Config):
    exposed = True

    def __init__(self):
        super().__init__()
        self.helper = DataHelper(self.config_path)

    def OPTIONS(self, *args, **kwargs):
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        cherrypy.response.headers['Access-Control-Max-Age'] = '3600'
        cherrypy.response.headers['Content-Type'] = 'text/plain'


# Polygon Server: Handles requests specific to polygonArray
class PolygonServer(BaseServer):
    @cherrypy.tools.json_out()
    def POST(self):
        try:
            body = cherrypy.request.body.read().decode('utf-8')
            json_body = json.loads(body)
            print("Received JSON data for polygonArray:", json_body)
        except json.JSONDecodeError:
            response.status = 400
            return {"status_code": 400, "message": "Invalid or missing JSON data"}

        if 'polygonArray' in json_body:
            self.helper.process_data('polygonArray', json_body)
            self.load_config()
            project_id = self.config["project_info"]["project_id"]
            project_name = self.config["project_info"]["projectName"]

            return {"status_code": 200, "message": "polygonArray Data processed successfully",
                    "project_name": project_name, "project_id": project_id}
        else:
            raise cherrypy.HTTPError(400, 'No polygonArray provided in the request.')

    def GET(self):
        return "GET request received on PolygonServer"


# Building Server: Handles requests specific to buildingGeometry
class BuildingServer(BaseServer):
    @cherrypy.tools.json_out()
    def POST(self):
        try:
            body = cherrypy.request.body.read().decode('utf-8')
            json_body = json.loads(body)
            print("Received JSON data for buildingGeometry:", json_body)
        except json.JSONDecodeError:
            response.status = 400
            return {"status_code": 400, "message": "Invalid or missing JSON data"}

        if 'buildingGeometry' in json_body:
            print("Processing buildingGeometry data...")
            self.helper.process_data('buildingGeometry', json_body)
            self.load_config()
            project_id = self.config["project_info"]["project_id"]
            project_name = self.config["project_info"]["projectName"]
            return {"status_code": 200, "message": "buildingGeometry Data processed successfully",
                    "project_name": project_name, "project_id": project_id}
        else:
            raise cherrypy.HTTPError(400, 'No buildingGeometry provided in the request.')

    def GET(self):
        return "GET request received on BuildingServer"


# CORS setup function
def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"


# Server configuration and startup
if __name__ == '__main__':
    config = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.CORS.on': True,
        }
    }

    cherrypy.server.socket_host = '127.0.0.1'
    # cherrypy.server.socket_host = '172.25.12.24'
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)

    # Mount each endpoint on a specific path
    cherrypy.tree.mount(PolygonServer(), '/polygonArray', config)
    cherrypy.tree.mount(BuildingServer(), '/buildingGeometry', config)

    cherrypy.engine.start()
    cherrypy.engine.block()
