import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.pipeline import Pipeline

def load_and_clean(path='data/premium_cars_dataset.csv'):
    df = pd.read_csv(path)
    print(f'Loaded: {df.shape[0]} rows, {df.shape[1]} cols')
    print('Columns:', df.columns.tolist())
    print('Missing values:\n', df.isnull().sum())

# Feature engineering
    df['car_age'] = 2024 - df['Year']
    df = df.drop(columns=['Car_Name', 'Year'])

# Drop missing values
    df = df.dropna()
    print(f'After cleaning: {df.shape[0]} rows')
    return df

def encode_categoricals(df):
    encoders = {}
    for col in ['Fuel_Type', 'Seller_Type', 'Transmission']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
        print(f'{col} encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}')
    return df, encoders

def train_and_compare(X_train, X_test, y_train, y_test):
    models = {
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, max_depth=4, random_state=42),
    }
    results = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        results[name] = {'model': model, 'RMSE': rmse, 'MAE': mae, 'R2': r2}
        print(f'{name:25s} RMSE={rmse:.4f} MAE={mae:.4f} R2={r2:.4f}')
    return results

def main():
    df = load_and_clean()
    df, encoders = encode_categoricals(df)

    feature_cols = [c for c in df.columns if c != 'Selling_Price_INR']
    X = df[feature_cols]
    y = df['Selling_Price_INR']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f'Train: {X_train.shape[0]} Test: {X_test.shape[0]}')

    results = train_and_compare(X_train, X_test, y_train, y_test)

    # Pick best model by lowest RMSE
    best_name = min(results, key=lambda k: results[k]['RMSE'])
    best_model = results[best_name]['model']
    print(f'\nBest model: {best_name}')

    # Build pipeline (scaler + best model) and refit on full training data
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', best_model),
    ])
    pipeline.fit(X_train, y_train)
    
    # Save
    os.makedirs('app/ml_models', exist_ok=True)
    joblib.dump(pipeline, 'app/ml_models/price_model.pkl')
    joblib.dump(feature_cols, 'app/ml_models/price_features.pkl')
    joblib.dump(encoders, 'app/ml_models/price_encoders.pkl')
    print('Saved: app/ml_models/price_model.pkl')
    print('Saved: app/ml_models/price_features.pkl')
    print('Saved: app/ml_models/price_encoders.pkl')

if __name__ == '__main__':
    main()