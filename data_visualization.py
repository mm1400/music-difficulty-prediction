import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import numpy as np


def change_difficulty(num):
  match num:
    case 1:
      return 1
    case 1.5:
      return 1
    case 2:
      return 2
    case 2.5:
      return 2
    case 3:
      return 3
    case 3.5:
      return 4
    case 4:
      return 4
    case 4.5:
      return 5
    case 5:
      return 5
    
# Only numeric columns
df = pd.read_csv('merged.csv')
df['difficulty'] = df['difficulty'].apply(change_difficulty)

print(df.describe())
print(df.head())
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
fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(20, 5))

# Plot our most correclated features with difficulty
sns.lineplot(x='pitch_range', y='difficulty', data=df, ax=ax0)

sns.lineplot(x='unique_note_count', y='difficulty', data=df, ax=ax1)

# Display the plots
plt.show()


for col in numeric_df[['note_count', 'note_density',  'unique_note_count', 'pitch_range', 'notes_per_second', 'tempo_change_count', 'overlapping_notes']].columns:
    sns.scatterplot(x=col, y='difficulty', data=df)
    plt.title(f'Boxplot of {col}')
    plt.show()



