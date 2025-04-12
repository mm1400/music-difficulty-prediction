import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics
from yellowbrick.cluster import KElbowVisualizer
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt


df = pd.read_csv('merged.csv')
print(df.shape)
df.drop(['file', 'average_tempo'], axis=1, inplace=True)
print(df.info())


model = KMeans()

visualizer = KElbowVisualizer(model, k=(1, len(df)+1), metric='distortion', timing=True)
visualizer.fit(df)
visualizer.show()

optimal_clusters = visualizer.elbow_value_
print(f"Optimal number of clusters: {optimal_clusters}")

kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
kmeans.fit(df)

df['cluster'] = kmeans.labels_
print(df['cluster'].value_counts())

df.to_csv('clustered_data.csv', index=False)