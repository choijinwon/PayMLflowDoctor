import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def model_flavor():
    return mlflow.pyfunc
