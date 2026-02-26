import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.cluster import KMeans
from scipy.stats.mstats import winsorize

def winsorize_data(
        X, 
        limits=[0.05, 0.05]
        ):
    return np.apply_along_axis(lambda x: winsorize(x, limits=limits), axis=0, arr=X)

def create_pipeline(
        clusters: int, 
        winsor: float = 0.05
        ) -> Pipeline:
    return Pipeline([
        ('winsorizer', FunctionTransformer(winsorize_data, kw_args={'limits': [winsor, winsor]})),
        ('scaler', StandardScaler()),
        ('kmeans', KMeans(n_clusters=clusters, random_state=42, n_init=20))
    ])




