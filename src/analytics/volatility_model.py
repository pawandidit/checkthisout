import numpy as np
from sklearn.cluster import KMeans

def classify_volatility(vol_series):
    if len(vol_series) < 3:
        return ["MEDIUM"] * len(vol_series)

    X = vol_series.values.reshape(-1, 1)
    kmeans = KMeans(n_clusters=3, n_init=10).fit(X)
    labels = kmeans.labels_

    mapping = {
        np.argmin(kmeans.cluster_centers_): "LOW",
        np.argmax(kmeans.cluster_centers_): "HIGH"
    }

    return [mapping.get(l, "MEDIUM") for l in labels]
