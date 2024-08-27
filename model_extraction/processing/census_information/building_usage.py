import json

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


class BuildingUsagePredictor:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.input_file = config['kriging_output_path']
        self.df = None
        self.model = None
        self.features = ['osm_building_use', 'E3', 'E4']
        self.target = 'building_use'  # This will be created, not loaded

    def load_data(self):
        # Load the data from the input file
        with open(self.input_file, 'r') as f:
            geojson_data = json.load(f)
        # Convert geojson to DataFrame
        self.df = pd.json_normalize(geojson_data['features'])
        self.df.columns = self.df.columns.str.replace('properties.', '')
        self.df.rename(columns={'building': 'osm_building_use'}, inplace=True)

        # Debugging print to check the columns
        print("Columns after loading data:", self.df.columns)

    def preprocess_data(self):
        # Encode categorical features
        label_encoder = LabelEncoder()
        self.df['osm_building_use'] = label_encoder.fit_transform(self.df['osm_building_use'].astype(str))
        self.df['E3'] = self.df['E3'].astype(float)
        self.df['E4'] = self.df['E4'].astype(float)

        # 'building_use' column will be created during prediction, not encoded here
        print("Columns after preprocessing data:", self.df.columns)

    def train_model(self):
        # Split the data into training and test sets
        X = self.df[self.features]
        y = self.df[self.target] if self.target in self.df else pd.Series(
            [0] * len(self.df))  # Dummy target if not present
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train a Random Forest Classifier
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

    def predict_building_usage(self):
        # Predict the building usage
        self.df[self.target] = self.model.predict(self.df[self.features])
        print(f"Created column '{self.target}' with predicted values.")

    def save_data(self):
        # Save the updated data back to the file
        with open(self.input_file, 'w') as f:
            json.dump(self.df.to_dict(orient='records'), f, indent=4)

    def run(self):
        self.load_data()
        self.preprocess_data()
        self.train_model()
        self.predict_building_usage()
        self.save_data()
