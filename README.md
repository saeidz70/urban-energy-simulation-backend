# Urban Energy Co-Simulation Backend

**A Modular Backend for Urban Energy Scenario Creation**

This repository contains the codebase for a scalable, modular backend system developed as part of the thesis
“Development of a Modular Backend for an Urban Energy Co-simulation Platform” at Politecnico di Torino. The system is
designed to automate urban energy scenario creation by integrating heterogeneous geospatial and urban datasets through a
microservice architecture.

## Overview

Urban energy systems are critical for achieving sustainable urban development. This backend system addresses the
challenges of data accessibility, heterogeneity, and scalability in urban energy modelling. Key research contributions
include:

- **Automated Data Processing:** Streamlining the retrieval, validation, and enrichment of diverse datasets (e.g.,
  OpenStreetMap, census records, and digital elevation models) to generate simulation-ready data.
- **Modular Microservices Architecture:** Implementing a flexible and scalable framework that separates geospatial
  processing, scenario generation, and configuration management into independent services.
- **Standardised Information Model:** Producing output in standardized formats (primarily GeoJSON) that can be directly
  integrated into urban energy co-simulation platforms.
- **Case Study Validation:** Demonstrated effectiveness using real-world datasets from Turin, Italy.

## System Architecture

The backend is built on a robust microservice architecture with the following core components:

### RESTful API Endpoints

- **PolygonServer (`/polygonArray`):** Processes user-defined polygon arrays to delineate project areas and run
  corresponding energy scenarios.
- **BuildingServer (`/buildingGeometry`):** Accepts GeoJSON data representing building geometries, converts them into
  enriched building polygons, and initiates scenario processing.
- **UpdateBuildingServer (`/updateBuildings`):** Allows updating of existing building data, reprocessing features when
  new or modified data is submitted.

These endpoints are implemented using [CherryPy](https://cherrypy.org/), which provides a lightweight, high-performance
web framework with built-in support for RESTful API design and CORS.

### Data Processing and Scenario Management

- **Geospatial Operations:** Utilizing [GeoPandas](https://geopandas.org/) and related geospatial libraries, the system
  performs crucial operations like CRS verification, spatial joins, and geometric validations.
- **Advanced Data Enrichment:** Incorporates interpolation techniques (e.g., via PyKrige) to estimate missing building
  attributes and ensure high-quality data output.
- **Scenario Generation:** A dedicated `ScenarioManager` orchestrates the creation of energy scenarios, integrating user
  inputs with external data sources to produce a standardized dataset for co-simulation.

### Configuration and Scalability

- **Centralised Configuration Management:** All system parameters (e.g., CRS, file paths, feature thresholds) are
  managed through an external JSON configuration file, enabling dynamic adjustments without code changes.
- **Containerisation:** The project is containerised using Docker, ensuring consistent deployment across various
  environments and simplifying scaling.
- **Modular Design:** Each component is designed to operate independently, allowing easy maintenance, updates, and
  integration with external systems.

## Thesis Background

The development of this backend is grounded in the research presented in the thesis, which addresses persistent
challenges in urban energy modelling. Key points from the thesis include:

- **Integration of Diverse Datasets:** The thesis identifies the need to harmonize disparate data sources—ranging from
  GIS datasets to census records—to create a unified and reliable urban energy model.
- **Automation and Standardisation:** By reducing manual preprocessing through automation, the system improves
  simulation efficiency and ensures that the output is consistent and ready for co-simulation.
- **Real-World Application:** The system’s effectiveness is demonstrated through a case study on the Turin urban area,
  where it successfully generated high-quality, simulation-ready datasets that support multi-energy system analyses.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/saeidz70/urban-energy-simulation-backend.git
   cd urban-energy-simulation-backend
   ```

2. **Install Dependencies:**
   All required packages are listed in the `requirements.txt` file. Install them using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration:**
   - Review and update the configuration file (typically located in the `config` folder) to set your preferred CRS, file
     paths, and other operational parameters.

4. **Run the Server:**
   Launch the backend using:
   ```bash
   python webservice.py
   ```
   By default, the server starts on port `8080`.

## Usage

Once the server is running, you can interact with the system via its RESTful API endpoints using tools
like [Postman](https://www.postman.com/) or `curl`:

- **POST /polygonArray:** Send a JSON payload with a `polygonArray` key to define your project area.
- **POST /buildingGeometry:** Submit GeoJSON data under the `buildingGeometry` key to process building footprints.
- **POST /updateBuildings:** Update building geometries by sending a JSON payload with the updated `buildingGeometry`
  data.

Each API call returns a JSON response containing project and scenario information (such as project IDs, scenario names,
and status messages).

## Contributing

This project is currently not open to external contributions. If you have any questions or suggestions, feel free to
reach out to the repository maintainer.

## Contact

For inquiries or further information, please open an issue on this repository. Alternatively, you can
visit [my GitHub profile](https://github.com/saeidz70) for updates and other projects.

## License

This project is available under the [MIT License](LICENSE).