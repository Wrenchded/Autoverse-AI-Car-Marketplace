import requests
import streamlit as st
import os
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

def _headers():
    token = st.session_state.get('token')   
    return {'Authorization': f'Bearer {token}'} if token else {}

def _safe_request(method, url, **kwargs):
    """
    Wrapper to prevent the 'JSONDecodeError' by checking the 
    response status before attempting to parse JSON.
    """
    try:
        response = method(url, **kwargs)
        # If the status is 4xx or 5xx, this raises an HTTPError
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.HTTPError:
        # Try to get the error message from the backend's JSON response
        try:
            return {"detail": response.json().get('detail', 'Server Error')}
        except:
            return {"detail": f"Backend Error: {response.status_code}"}
    except requests.exceptions.JSONDecodeError:
        return {"detail": "Backend sent non-JSON data (check backend logs)."}
    except Exception as e:
        return {"detail": f"Connection failed: {str(e)}"}

def register(name, email, password, role):
    return requests.post(f'{BASE_URL}/auth/register',
json={'name': name, 'email': email, 'password': password, 'role': role},
timeout=10)

def login(email, password):
    return requests.post(f'{BASE_URL}/auth/login',
data={'username': email, 'password': password}, timeout=10)

def get_me():
    return requests.get(f'{BASE_URL}/users/me', headers=_headers(), timeout=10)

def get_cars(**filters):
    params = {k: v for k, v in filters.items() if v}
    return requests.get(f'{BASE_URL}/cars', params=params, timeout=10).json()

def create_car(data: dict):
    return requests.post(f'{BASE_URL}/cars', json=data, headers=_headers(), timeout=10)

def get_car(car_id: str):
    return requests.get(f'{BASE_URL}/cars/{car_id}', timeout=10).json()

def predict_price(data: dict):
    # Using the safe wrapper instead of direct .json()
    return _safe_request(requests.post, f'{BASE_URL}/price/predict', json=data, timeout=15)

def detect_damage(car_id: str, file_bytes: bytes, filename: str):
    return requests.post(
f'{BASE_URL}/damage/detect/{car_id}',
files={'file': (filename, file_bytes, 'image/jpeg')},
headers=_headers(), timeout=30,
).json()

def get_recommendations(car_id: str):
    return requests.get(f'{BASE_URL}/recommendations/{car_id}', timeout=10).json()

def create_booking(car_id: str, booking_date: str):
    return requests.post(f'{BASE_URL}/bookings',

json={'car_id': car_id, 'booking_date': booking_date},
headers=_headers(), timeout=10)

def create_rental(car_id: str, start: str, end: str):
    return requests.post(f'{BASE_URL}/rentals',
json={'car_id': car_id, 'start_date': start, 'end_date': end},
headers=_headers(), timeout=10)

def get_analytics():
    return requests.get(f'{BASE_URL}/analytics/summary',
headers=_headers(), timeout=10).json()

def delete_car(car_id):
    return requests.delete(
        f'{BASE_URL}/cars/{car_id}',
        headers=_headers(),
        timeout=10
    )