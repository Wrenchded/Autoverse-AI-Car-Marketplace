import streamlit as st
from utils.api import get_cars, get_recommendations

st.set_page_config(page_title='Recommendations', layout='wide')
st.title('Car Recommendations')

cars = get_cars()
if not cars:
    st.info('No cars available.')
    st.stop()

car_options = {f"{c['brand']} {c['model']} ({c['year']})": c['id'] for c in cars}
selected = st.selectbox('Pick a car you like:', list(car_options.keys()))
car_id = car_options[selected]

if st.button('Find Similar Cars'):  
    with st.spinner('Finding recommendations...'):
        recs = get_recommendations(car_id)

    if isinstance(recs, list) and recs:
        st.success(f'Top {len(recs)} similar cars:')
        for car in recs:
            with st.container(border=True):
                c1, c2 = st.columns([3, 2])
                c1.subheader(f"{car['brand']} {car['model']} ({car['year']})")
                c1.write(f"{car['fuel_type']} | {car['transmission']} | {car['mileage']:,.0f} km")
                c2.metric('Price', f"${car['listed_price']:,.0f}")
    elif isinstance(recs, dict):
        st.error(recs.get('detail', 'Recommendation failed.'))  
    else:
        st.info('No similar cars found.')