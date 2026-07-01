import streamlit as st
from utils.api import create_car

st.set_page_config(page_title='List a Car', layout='wide')
st.title('List Your Car')

# -------------------------
# AUTH CHECK
# -------------------------
if not st.session_state.get('token'):
    st.warning('Please log in first')
    st.stop()

# ROLE CHECK (FIXED)
if st.session_state.get('role') != 'seller':
    st.error('Only Sellers can list cars.')
    st.stop()

# -------------------------
# FORM
# -------------------------
with st.form('list_car_form'):
    c1, c2 = st.columns(2)

    brand = c1.text_input('Brand *')
    model = c2.text_input('Model *')

    year = c1.number_input('Year *', 1990, 2025, 2018)
    mileage = c2.number_input('Mileage (km) *', 0, 999999, 50000)

    fuel = c1.selectbox(
        'Fuel Type *',
        ['petrol', 'diesel', 'electric', 'hybrid', 'cng']
    )

    trans = c2.selectbox(
        'Transmission *',
        ['manual', 'automatic']
    )

    engine = c1.number_input(
        'Engine (litres)',
        min_value=0.6,
        max_value=6.0,
        value=1.5
    )

    body = c2.selectbox(
        'Body Type',
        ['Sedan', 'SUV', 'Hatchback', 'Coupe', 'Truck', 'Van', 'None']
    )

    price = st.number_input(
        'Listed Price ($) *',
        min_value=1.0,
        max_value=1000000.0,
        value=15000.0
    )

    images = st.file_uploader(
        "Upload Car Images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    submit = st.form_submit_button('List Car')

# -------------------------
# SUBMIT LOGIC
# -------------------------
if submit:
    if not brand or not model:
        st.error('Brand and Model are required.')
        st.stop()

    payload = {
        'brand': brand,
        'model': model,
        'year': year,
        'mileage': mileage,
        'fuel_type': fuel,
        'transmission': trans,
        'engine': engine,
        'body_type': None if body == 'None' else body,
        'listed_price': price,
    }

    with st.spinner("Listing your car... "):
        r = create_car(payload)

    # -------------------------
    # RESPONSE HANDLING
    # -------------------------
    try:
        response = r.json()
    except:
        response = {}

    if r.status_code == 201:
        st.success('🎉 Car listed successfully!')

        if response.get('predicted_price'):
            st.info(
                f"🤖 AI Predicted Price: ${response['predicted_price']:,.0f}"
            )
    else:
        st.error(response.get('detail', 'Failed to list car.'))