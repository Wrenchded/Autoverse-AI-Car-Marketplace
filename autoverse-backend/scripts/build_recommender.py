'''
Builds and saves the cosine similarity matrix from current car inventory.
Run this: python scripts/build_recommender.py
Re-run whenever the car inventory changes significantly.
'''
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import joblib, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import SessionLocal
from app import models

def build():
    db = SessionLocal()
    cars = db.query(models.Car).filter(models.Car.status == 'available').all()
    db.close()

    if len(cars) < 5:
        print(f'Only {len(cars)} cars — need at least 5. Add more cars first.')
        return
    rows = []
    for c in cars:
        rows.append({
            'id': str(c.id),
            'year': c.year or 2015,
            'mileage': c.mileage or 0,
            'listed_price': c.listed_price or 0,    
            'engine': c.engine or 1.5,
            'fuel_type': c.fuel_type.value if c.fuel_type else 'petrol',
            'transmission': c.transmission.value if c.transmission else 'manual',
        })

    df = pd.DataFrame(rows)

    # Encode categoricals
    le_fuel = LabelEncoder()
    le_trans = LabelEncoder()
    df['fuel_enc'] = le_fuel.fit_transform(df['fuel_type'])
    df['trans_enc'] = le_trans.fit_transform(df['transmission'])

    features = ['year', 'mileage', 'listed_price', 'engine', 'fuel_enc', 'trans_enc']

    scaler = StandardScaler()
    matrix = scaler.fit_transform(df[features])
    sim = cosine_similarity(matrix)
    artifact = {
        'ids': df['id'].tolist(),
        'matrix': sim,
        'scaler': scaler,
    }
    os.makedirs('app/ml_models', exist_ok=True) 
    joblib.dump(artifact, 'app/ml_models/recommender.pkl')
    print(f'Recommender built for {len(cars)} cars. Saved.')

if __name__ == '__main__':
    build()