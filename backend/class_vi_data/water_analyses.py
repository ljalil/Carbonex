import pandas as pd

war = pd.read_csv("backend/class_vi_data/water_analyses.csv")
war = war[
    [
        "API Number",
        "Formation",
        "Latitude",
        "Longitude",
        "Sodium (mg/L)",
        "Potassium (mg/L)",
        "Magnesium (mg/L)",
        "Calcium (mg/L)",
        "Chloride (mg/L)",
        "Sulfate (mg/L)",
        "Bicarbonate (mg/L)",
        "Carbonate (mg/L)",
        "pH",
    ]
]
