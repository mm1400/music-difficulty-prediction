import pandas as pd

difficulty_df = pd.read_csv('difficulty.csv')

features_df = pd.read_csv('features.csv')

merged_df = pd.merge(difficulty_df, features_df, on='file', how='inner')

merged_df.to_csv('merged.csv', index=False)
