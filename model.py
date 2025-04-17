from sklearn import clone
from sklearn.base import RegressorMixin, TransformerMixin, BaseEstimator
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.feature_selection import r_regression, SelectPercentile
from sklearn.model_selection import KFold, GridSearchCV
from xgboost import XGBRegressor
import pandas as pd
import pickle
import numpy as np

df = pd.read_csv('processed.csv')

# makes models perform worse
# df['difficulty_transform'], lambda_value = stats.boxcox(df['difficulty'])

print(df.head())

# Define features

X = df.drop(columns=['difficulty'])
y = df['difficulty']

features_names = X.columns

# Keep the best features
selector = SelectPercentile(r_regression, percentile=40)
X = selector.fit_transform(X, y)

print("Features kept:", features_names[selector.get_support()])

# Scale data as features have large differences in scale
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

# Removes randomness from the model across runs
rng = np.random.RandomState(0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=rng)

# params = {
#         'n_estimators': [100, 200, 500, 1000],
#         'gamma': [0.005, 0.01, 0.1, 0],
#         'max_depth': [1, 2, 3, 6, 9],
#         'learning_rate': [0.001, 0.01, 0.1, 0.015, 1],
#         'min_child_weight': [1, 2, 3],
#         }

# grid_search = GridSearchCV(XGBRegressor(), params, scoring= 'neg_mean_squared_error')

# grid_search.fit(X_train, y_train)

# print("Best parameters:", grid_search.best_params_)
# print("Best cross-validation score:", grid_search.best_score_)

# df = pd.DataFrame(grid_search.cv_results_)
# df.to_csv('grid_search_results.csv', index=False)

# Best parameters for XGB: {'gamma': 0.01, 'learning_rate': 0.1, 'max_depth': 9, 'min_child_weight': 3, 'n_estimators': 500}

models = {
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=rng),
    'SVR (RBF)': make_pipeline(SVR(kernel='rbf')),
    'XGB':  XGBRegressor(gamma=0.01, learning_rate=0.01, max_depth=9, min_child_weight=3, n_estimators=500, random_state=rng),
}

#Validation function
n_folds = 5

def rmse_cross_validation(model):
    kf = KFold(n_folds, shuffle=True, random_state=42)
    rmse= np.sqrt(-cross_val_score(model, X_train, y_train, scoring="neg_mean_squared_error", cv = kf))
    return(rmse)

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"Model: {name}")
    # Round and clip to ensure valid difficulty levels
    y_pred_rounded = np.clip(np.round(y_pred), 1, 5)
    print("Mean squared error:", mean_squared_error(y_test, y_pred))
    print("Mean absolute error:", mean_absolute_error(y_test, y_pred))
    print("R^2 score:", r2_score(y_test, y_pred))
    print("Root mean squared error:", rmse_cross_validation(model).mean())
    print("======================")
    

    # Save the model to disk
    with open('saved_model.pkl', 'wb') as file:
      pickle.dump(model, file)
    
# referenced from https://www.kaggle.com/code/serigne/stacked-regressions-top-4-on-leaderboard
class AveragingModels(BaseEstimator, RegressorMixin, TransformerMixin):
    def __init__(self, models):
        self.models = models
        
    # we define clones of the original models to fit the data in
    def fit(self, X, y):
        self.models_ = [clone(x) for x in self.models]
        
        # Train cloned base models
        for model in self.models_:
            model.fit(X, y)

        return self
    
    #Now we do the predictions for cloned models and average them
    def predict(self, X):
        predictions = np.column_stack([
            model.predict(X) for model in self.models_
        ])
        return np.mean(predictions, axis=1)   
    
averaged_models = AveragingModels(models=list(models.values()))
score = rmse_cross_validation(averaged_models)
print(" Averaged base models score: {:.4f} ({:.4f})\n".format(score.mean(), score.std()))

averaged_models.fit(X_train, y_train)
y_pred = averaged_models.predict(X_test)
print("Mean squared error:", mean_squared_error(y_test, y_pred))
print("Mean absolute error:", mean_absolute_error(y_test, y_pred))
print("R^2 score:", r2_score(y_test, y_pred))