import streamlit as st
import base64
from utils.api import login, register

# Helper function to allow local images in HTML
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

st.set_page_config(
    page_title="AutoVerse",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session state initialization
for key, default in [("token", None), ("role", None), ("user_name", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- HIDE SIDEBAR BEFORE LOGIN ----------
if not st.session_state["token"]:
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display:none;}
    [data-testid="collapsedControl"] {display:none;}
    [data-testid="stSidebar"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

# ---------- CENTERED LAYOUT ----------
left, center, right = st.columns([1,2,1])

with center:
    # --- FIX STARTS HERE ---
    try:
        logo_base64 = get_base64("assets/AutoVerse_logo.png")
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="250" style="display:block; margin:-180px auto -60px auto;">'
    except Exception:
        # Fallback if file is missing
        logo_html = '<div style="font-size:50px; margin-bottom:10px;">🚗</div>'

    st.markdown(f"""
    <div style="text-align:center; margin-bottom:30px;">
        {logo_html}
    </div>
    """, unsafe_allow_html=True)
    # --- FIX ENDS HERE ---

    if st.session_state["token"]:
        st.success(
            f'Logged in as {st.session_state["user_name"]} '
            f'({st.session_state["role"]})'
        )

        if st.button("Logout"):
            st.session_state.update({
                "token": None,
                "role": None,
                "user_name": ""
            })
            st.rerun()

    else:
        tab1, tab2 = st.tabs(["Login", "Register"])

        # ---------- LOGIN ----------
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="Enter your email")
                pw = st.text_input("Password", type="password", placeholder="Enter your password")
                st.write("")
                sub = st.form_submit_button("Login")

            if sub:
                r = login(email, pw)
                if r.status_code == 200:
                    data = r.json()

                    st.session_state["token"] = data["access_token"]

                    from utils.api import get_me
                    me = get_me().json()

                    st.session_state["role"] = me["role"]
                    st.session_state["user_name"] = me["name"]

                    # 🔥 ADD THIS LINE (IMPORTANT)
                    st.session_state["user_id"] = me["id"]

                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        # ---------- REGISTER ----------
        with tab2:
            with st.form("reg_form"):
                name = st.text_input("Full Name", placeholder="Enter your name")
                email = st.text_input("Email", placeholder="Enter your email")
                pw = st.text_input("Password", type="password", placeholder="Min 8 chars & include a number")
                role = st.selectbox("I am a", ["buyer", "seller"])
                st.write("")
                sub = st.form_submit_button("Create Account")

            if sub:
                r = register(name, email, pw, role)
                if r.status_code == 201:
                    st.success("Account created! Please log in.")
                else:
                    st.error(r.json().get("detail", "Registration failed."))