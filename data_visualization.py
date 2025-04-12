import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Only numeric columns
df = pd.read_csv('merged.csv')
numeric_df = df.drop(columns=['file'])

# Get correlation
plt.figure(figsize=(14, 10))
sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f", cmap="coolwarm", square=True)
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.show()


# Get distribution of difficulty
numerical_features = ['difficulty']
df[numerical_features].hist(bins=30, figsize=(12, 8))
plt.suptitle('Histograms of Numerical Features')
plt.show()


# Create a figure with three subplots
fig, (ax0, ax1) = plt.subplots(1, 3, figsize=(20, 5))

# Plot our most correclated features with difficulty
sns.lineplot(x='pitch_range', y='difficulty', data=df, ax=ax0)

sns.lineplot(x='unique_note_count', y='difficulty', data=df, ax=ax1)

# Display the plots
plt.show()