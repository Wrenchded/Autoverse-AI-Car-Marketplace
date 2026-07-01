import streamlit as st
from utils.api import get_car

st.title("Edit Listing")

car_id = st.session_state.get("edit_car_id")

if not car_id:
    st.error("No car selected")
    st.stop()

car = get_car(car_id)

st.subheader(f"{car['brand']} {car['model']}")

# -------------------------
# EDIT FIELDS
# -------------------------
price = st.number_input("Price", value=float(car["listed_price"]))
mileage = st.number_input("Mileage", value=float(car["mileage"]))

# -------------------------
# IMAGE UPLOAD (NEW)
# -------------------------
images = st.file_uploader(
    "Upload New Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# -------------------------
# SAVE BUTTON
# -------------------------
if st.button("Save Changes"):
    payload = {
        "listed_price": price,
        "mileage": mileage
    }

    # TODO: call update API
    st.success("Listing updated successfully!")