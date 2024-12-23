import uuid

from config.config import Config


class ProjectId(Config):
    def __init__(self):
        super().__init__()

    def generate_project_id(self):
        # Generate a unique project ID
        project_id = str(uuid.uuid4())

        # Load the config file
        self.load_config()

        # Update the project_info with the new project ID
        if "project_info" not in self.config:
            self.config["project_info"] = {}
        self.config["project_info"]["project_id"] = project_id

        # Save the updated config
        self.save_config()

        print(f"Generated unique project ID: {project_id} and saved to config.")
        return project_id

    def run(self):
        """Run the project ID generation process."""
        try:
            project_id = self.generate_project_id()
            print("Project ID generation process completed successfully.")
            return project_id
        except Exception as e:
            print(f"Error during project ID generation: {e}")
            raise
