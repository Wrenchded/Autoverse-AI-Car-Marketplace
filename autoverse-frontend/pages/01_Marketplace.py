import streamlit as st
import pandas as pd
from utils.api import create_booking, create_rental

# ------------------ CONFIG ------------------
st.set_page_config(page_title='Marketplace', layout='wide')
st.title('AutoVerse Marketplace')

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/luxury_cars.csv")

cars_df = load_data()

# ------------------ LOCAL IMAGE MAPPING ------------------
def get_local_image(brand):
    brand = brand.lower()

    if "lamborghini" in brand:
        return "assets/images/Lamborghini.png"
    elif "ferrari" in brand:
        return "assets/images/ferrari.png"
    elif "bmw" in brand:
        return "assets/images/bmw.jpeg"
    elif "audi" in brand:
        return "assets/images/audi.jpg"
    elif "mercedes" in brand:
        return "assets/images/mercedes.jpeg"
    elif "porsche" in brand:
        return "assets/images/porsche.jpg"
    else:
        return "assets/images/default.jpg"

# ------------------ FILTERS ------------------
with st.expander('🔍 Filters', expanded=True):
    c1, c2, c3, c4 = st.columns(4)

    brand = c1.selectbox("Brand", ["All"] + sorted(cars_df["brand"].unique()))
    fuel = c2.selectbox("Fuel", ["All"] + sorted(cars_df["fuel_type"].unique()))
    
    max_price = c3.slider(
        "Max Price (₹)",
        0,
        int(cars_df["listed_price"].max()),
        int(cars_df["listed_price"].max())
    )

    min_year = c4.slider(
        "Min Year",
        int(cars_df["year"].min()),
        int(cars_df["year"].max()),
        int(cars_df["year"].min())
    )

# ------------------ APPLY FILTERS ------------------
filtered_df = cars_df.copy()

if brand != "All":
    filtered_df = filtered_df[filtered_df["brand"] == brand]

if fuel != "All":
    filtered_df = filtered_df[filtered_df["fuel_type"] == fuel]

filtered_df = filtered_df[filtered_df["listed_price"] <= max_price]
filtered_df = filtered_df[filtered_df["year"] >= min_year]

cars = filtered_df.to_dict(orient="records")

# ------------------ PAGINATION ------------------
items_per_page = 12
total_pages = max(1, (len(cars) - 1) // items_per_page + 1)

page = st.number_input("📄 Page", min_value=1, max_value=total_pages, step=1)

start = (page - 1) * items_per_page
end = start + items_per_page

cars = cars[start:end]

# ------------------ COUNT ------------------
st.markdown(f"### 🚗 {len(cars)} Cars Showing (Page {page} of {total_pages})")

# ------------------ MOBILE VIEW TOGGLE ------------------
mobile_view = st.checkbox("📱 Mobile View")

if mobile_view:
    cols = st.columns(1)
else:
    cols = st.columns(3)

# ------------------ GRID DISPLAY ------------------
for idx, car in enumerate(cars):
    with cols[idx % len(cols)]:

        # -------- IMAGE --------
        image_path = get_local_image(car["brand"])
        st.image(image_path, width=300)

        # -------- TITLE --------
        st.markdown(f"### {car['brand']} {car['model']}")

        # -------- PRICE --------
        st.markdown(f"💰 **₹{int(car['listed_price']):,}**")

        # -------- DETAILS --------
        st.write(f"📅 {car['year']} | {int(car['mileage']):,} km")
        st.write(f"⚙️ {car['engine']}L | {car['transmission']}")
        st.write(f"⛽ {car['fuel_type']} | 🎨 {car['color']}")
        st.write(f"🏁 {car['top_speed']} km/h | ⚡ {car['horsepower']} HP")
        st.write(f"📍 {car['location']}")

        # -------- ACTION BUTTONS --------
        