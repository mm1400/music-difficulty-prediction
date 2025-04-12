from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Ridge, LinearRegression, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.pipeline import make_pipeline
from xgboost import XGBRegressor
import pandas as pd

df = pd.read_csv('clustered_data.csv')

# makes models perform worse
# df['difficulty_transform'], lambda_value = stats.boxcox(df['difficulty'])

X = df.drop(columns=['difficulty', 'cluster'])
y = df['difficulty']

print(df.head())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


models = {
    'Linear Regression': LinearRegression(),
    'Ridge': Ridge(),
    'Lasso': Lasso(),
    'Random Forest': RandomForestRegressor(),
    'Gradient Boosting': GradientBoostingRegressor(),
    'XGBoost': XGBRegressor(),
    'SVR (RBF)': make_pipeline(StandardScaler(), SVR(kernel='rbf'))
}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"Model: {name}")
    print("Mean squared error:", mean_squared_error(y_test, y_pred))
    print("Mean absolute error:", mean_absolute_error(y_test, y_pred))
    print("R^2 score:", r2_score(y_test, y_pred))
    scores = cross_val_score(model, X, y, cv=5)
    print("Mean R^2 score from cross-validation:", scores.mean())
    print("======================")