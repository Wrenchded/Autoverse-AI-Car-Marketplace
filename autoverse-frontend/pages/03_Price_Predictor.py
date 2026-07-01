import streamlit as st
from utils.api import predict_price

st.set_page_config(page_title='Price Predictor', layout='centered')
st.title('AI Price Predictor')

with st.form('price_form'): 
    c1, c2 = st.columns(2)
    brand = c1.text_input('Brand', 'Porsche')
    model = c2.text_input('Model', 'Taycan')
    
    # NEW: Present Price is required by your model
    present_price = st.number_input('Current New Price (INR)', 500000, 50000000, 15000000)
    
    year = c1.number_input('Year of Purchase', 2000, 2025, 2020)
    mileage = c2.number_input('Distance Driven (km)', 0, 500000, 20000)
    
    fuel = c1.selectbox('Fuel Type', ['Petrol', 'Diesel', 'Electric'])
    trans = c2.selectbox('Transmission', ['Automatic', 'Manual'])
    
    # Added defaults for Seller and Owner to match dataset
    seller = c1.selectbox('Seller Type', ['Individual', 'Dealer'])
    owner = c2.selectbox('Previous Owners', [0, 1, 2, 3])
    
    sub = st.form_submit_button('■ Predict Market Price')

if sub:
    with st.spinner('Calculating...'):
        # Send data with keys matching what we'll handle in the backend
        result = predict_price({
            'present_price': present_price,
            'year': year,
            'mileage': mileage,
            'fuel_type': fuel,
            'transmission': trans,
            'seller_type': seller,
            'owner': owner
        })
        
    if 'predicted_price' in result:
        st.success(f"Estimated Selling Price: ₹{result['predicted_price']:,.2f}")
        st.balloons()
    else:
        st.error(result.get('detail', 'Prediction failed.'))