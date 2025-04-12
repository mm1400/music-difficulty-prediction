import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Load the clustered data
df = pd.read_csv('clustered_data.csv')

# Compare average difficulty per cluster
cluster_difficulty = df.groupby('cluster')['difficulty'].mean().sort_values()
print(cluster_difficulty)

# Boxplot to see the spread of difficulties within each cluster
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='cluster', y='difficulty', palette='viridis')
plt.title('Difficulty Distribution by Cluster')
plt.xlabel('Cluster')
plt.ylabel('Difficulty')
plt.show()