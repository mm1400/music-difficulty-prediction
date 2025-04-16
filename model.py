from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import Ridge, LinearRegression, Lasso
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.feature_selection import r_regression, SelectPercentile
from xgboost import XGBRegressor
import pandas as pd

df = pd.read_csv('merged.csv')

# makes models perform worse
# df['difficulty_transform'], lambda_value = stats.boxcox(df['difficulty'])

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
    
df['difficulty'] = df['difficulty'].apply(change_difficulty)

# Delete non numeric columns
df.drop(columns=['file'], inplace=True)
print(df.head())

# Define features

X = df.drop(columns=['difficulty'])
y = df['difficulty']

features_names = X.columns

# Keep the best features
selector = SelectPercentile(r_regression, percentile=35)
X = selector.fit_transform(X, y)

print("Features kept:", features_names[selector.get_support()])

# Scale data as features have large differences in scale
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

models = {
    'Random Forest': RandomForestRegressor(n_estimators=100),
    # 'SVR (RBF)': make_pipeline(SVR(kernel='rbf'))
}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f"Model: {name}")
    print("Mean squared error:", mean_squared_error(y_test, y_pred))
    print("Mean absolute error:", mean_absolute_error(y_test, y_pred))
    print("R^2 score:", r2_score(y_test, y_pred))
    scores = cross_val_score(model, X, y, cv=5)
    print(":", scores.mean())
    print("======================")
    
