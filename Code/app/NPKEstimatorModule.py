import warnings
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings("ignore")


class NPKEstimator:

    def __init__(self, data="nutrient_recommendation_full-2.csv"):

        # Load dataset
        self.df = pd.read_csv(data)

        self.df.columns = [
            "Crop",
            "Temperature",
            "Humidity",
            "Rainfall",
            "Label_N",
            "Label_P",
            "Label_K"
        ]

        # Normalize crop names
        self.df["Crop"] = self.df["Crop"].str.strip().str.lower()

        # Encode crop ONLY
        self.crop_encoder = LabelEncoder()
        self.df["Crop_Encoded"] = self.crop_encoder.fit_transform(self.df["Crop"])

        # Feature set
        X = self.df[["Crop_Encoded", "Temperature", "Humidity", "Rainfall"]]

        # Train models once
        self.model_N = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_P = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_K = RandomForestRegressor(n_estimators=100, random_state=42)

        self.model_N.fit(X, self.df["Label_N"])
        self.model_P.fit(X, self.df["Label_P"])
        self.model_K.fit(X, self.df["Label_K"])

    # ✅ THIS IS WHAT app.py CALLS
    def get_npk_values(self, crop, temperature, humidity, rainfall):

        crop = crop.strip().lower()

        if crop not in self.crop_encoder.classes_:
            raise ValueError(f"Unknown crop: {crop}")

        crop_encoded = self.crop_encoder.transform([crop])[0]

        X_input = [[
            crop_encoded,
            temperature,
            humidity,
            rainfall
        ]]

        return {
            "Label_N": int(self.model_N.predict(X_input)[0]),
            "Label_P": int(self.model_P.predict(X_input)[0]),
            "Label_K": int(self.model_K.predict(X_input)[0])
        }
