from sklearn import clone
from sklearn.base import RegressorMixin, TransformerMixin, BaseEstimator
import numpy as np

class AveragingModels(BaseEstimator, RegressorMixin, TransformerMixin):
    def __init__(self, models, scaler):
        self.models = models
        self.scaler = scaler

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