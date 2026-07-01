import streamlit as st
from utils.api import get_cars, delete_car

st.set_page_config(page_title="My Listings", layout="wide")
st.title("🚗 My Listed Cars")

# -------------------------
# AUTH CHECK
# -------------------------
if not st.session_state.get("token"):
    st.warning("Please login first")
    st.stop()

if st.session_state.get("role") != "seller":
    st.error("Only sellers can view this page")
    st.stop()

user_id = st.session_state.get("user_id")

# -------------------------
# FETCH ALL CARS
# -------------------------
cars = get_cars()

if not cars:
    st.info("No cars available yet")
    st.stop()

# -------------------------
# FILTER ONLY MY CARS
# -------------------------
my_cars = [
    car for car in cars
    if car.get("seller_id") == user_id
]

# -------------------------
# DISPLAY
# -------------------------
st.subheader(f"Total Listings: {len(my_cars)}")

if not my_cars:
    st.info("You haven't listed any cars yet 🚗")
else:
    for car in my_cars:
        with st.container():
            st.markdown("---")

            c1, c2, c3 = st.columns(3)

            # -------------------------
            # COLUMN 1 (CAR INFO)
            # -------------------------
            with c1:
                st.subheader(f"{car['brand']} {car['model']}")
                st.write(f"📅 Year: {car['year']}")
                st.write(f"⛽ Fuel: {car['fuel_type']}")
                st.write(f"⚙️ Transmission: {car['transmission']}")

            # -------------------------
            # COLUMN 2 (PRICE INFO)
            # -------------------------
            with c2:
                st.write(f"💰 Listed Price: ${car['listed_price']:,.0f}")
                st.write(f"🛣️ Mileage: {car['mileage']} km")
                st.write(f"🔧 Engine: {car['engine']}L")

            # -------------------------
            # COLUMN 3 (ACTIONS)
            # -------------------------
            with c3:

                # ✏️ EDIT LISTING
                if st.button("✏️ Edit Listing", key=f"edit_{car['id']}"):
                    st.session_state["edit_car_id"] = car["id"]
                    st.switch_page("pages/Edit_Car.py")

                # 🔐 CONFIRM DELETE CHECKBOX
                confirm = st.checkbox(
                    "Confirm delete", key=f"confirm_{car['id']}"
                )

                # 🗑️ DELETE BUTTON
                if confirm and st.button("🗑️ Delete", key=f"delete_{car['id']}"):

                    response = delete_car(car["id"])

                    if response.status_code in [200, 204]:
                        st.success("Car deleted successfully 🚗")
                        st.rerun()
                    else:
                        st.error("Failed to delete car")