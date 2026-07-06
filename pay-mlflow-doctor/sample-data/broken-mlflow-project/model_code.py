import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier


def predict(rows):
    frame = pd.DataFrame(rows)
    return xgb.DMatrix(frame)
