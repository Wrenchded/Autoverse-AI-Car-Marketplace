import streamlit as st
import requests
from PIL import Image

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="AutoVerse AI Damage Detection",
    layout="wide",
    page_icon="🚗"
)

API_URL = "http://127.0.0.1:8000"

# -----------------------------
# CUSTOM STYLE (premium feel)
# -----------------------------


# -----------------------------
# HEADER
# -----------------------------
st.title("AutoVerse AI Damage Detection")
st.caption("Upload a vehicle image and let AI instantly detect damage")

# -----------------------------
# AUTH CHECK
# -----------------------------
if "token" not in st.session_state or not st.session_state.token:
    st.warning("⚠️ Please login from Home page first")
    st.stop()

headers = {
    "Authorization": f"Bearer {st.session_state.token}"
}

# -----------------------------
# UI LAYOUT
# -----------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Vehicle Image")
    uploaded_file = st.file_uploader(
        "Drop image here",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview", use_column_width=True)

with col2:
    st.subheader("🧠 AI Analysis Panel")

    st.info("Click below to analyze damage detection")

    predict = st.button("🔍 Analyze Damage")

    if predict:

        if not uploaded_file:
            st.error("Please upload an image first")
            st.stop()

        with st.spinner("AI is scanning vehicle... 🚗💥"):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            response = requests.post(
                f"{API_URL}/damage/detect",
                headers=headers,
                files=files
            )

            if response.status_code == 200:
                data = response.json()

                st.success("Analysis Complete 🎯")

                # -----------------------------
                # RESULT CARDS
                # -----------------------------
                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    st.metric("Damage Status", data["damage_label"].upper())

                with col_b:
                    st.metric("Confidence", f"{data['damage_confidence']:.2f}")

                with col_c:
                    st.metric("Damage Score", f"{data['damage_score']}%")

                # -----------------------------
                # VISUAL OUTPUT
                # -----------------------------
                st.markdown("---")

                if data["damage_label"] == "damaged":
                    st.error("⚠️ Vehicle shows signs of structural damage")
                    st.progress(min(int(data["damage_score"]), 100))
                else:
                    st.success("✅ Vehicle appears to be in good condition")
                    st.progress(100)

                st.markdown("---")
                st.caption("AI Model: MobileNetV2 | Status: Active 🟢")

            else:
                st.error(f"API Error: {response.text}")