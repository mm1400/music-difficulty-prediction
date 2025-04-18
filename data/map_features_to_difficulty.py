import pandas as pd

difficulty_df = pd.read_csv('./data/difficulty.csv')

features_df = pd.read_csv('./data/features.csv')

merged_df = pd.merge(difficulty_df, features_df, on='file', how='inner')

merged_df.to_csv('./data/features_difficulty_merged.csv', index=False)
