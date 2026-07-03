import streamlit as st
import school_db
from streamlit.components.v1 import html

# Configure the web page layout (Moet als allereerste Streamlit commando)
st.set_page_config(page_title="School Token Portal", page_icon="🏆", layout="centered")

# Forceer mobiele en desktop toolbar deactivatie
st.set_option("client.toolbarMode", "viewer")

# --- JAVASCRIPT OM WATERMERKEN TE VERWIJDEREN ---
html('''
<script>
    const wipeWatermarks = () => {
        window.top.document.querySelectorAll(`[href*="streamlit.io"]`).forEach(el => {
            el.setAttribute("style", "display: none !important; visibility: hidden !important;");
        });
        window.top.document.querySelectorAll('footer').forEach(footer => {
            footer.setAttribute("style", "display: none !important;");
        });
    };
    wipeWatermarks();
    setInterval(wipeWatermarks, 500);
</script>
''', height=0)

# --- CSS OVERRIDE VOOR SCHONE LAYOUT ---
global_hide_style = """
    <style>
    header[data-testid="stHeader"] { display: none !important; visibility: hidden !important; height: 0px !important; }
    [data-testid="stDecoration"] { display: none !important; }
    div[class*="viewerBadge_container"] { display: none !important; visibility: hidden !important; }
    footer { display: none !important; visibility: hidden !important; height: 0px !important; }
    .block-container { padding-top: 1.5rem !important; }
    </style>
"""
st.markdown(global_hide_style, unsafe_allow_html=True)

st.title("🏆 School Token Portal")

# --- TOAST GEHEUGENSYSTEM ---
# Als er een succesbericht is opgeslagen na de herlaadactie, laat hem nu rustig zien!
if "success_message" in st.session_state and st.session_state.success_message:
    st.toast(st.session_state.success_message, icon="🏆")
    st.session_state.success_message = None

# --- LOGIN REGION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.student_id = ""
    st.session_state.success_message = None

if not st.session_state.logged_in:
    st.subheader("🔐 Please Login")
    user_input = st.text_input("Username (Student ID or 'Teacher')").strip().upper()
    password_input = st.text_input("Password (Staff Only)", type="password").strip()
    
    if st.button("Login", use_container_width=True):
        data = school_db.load_data()
        
        if user_input == "TEACHER" and password_input == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "teacher"
            st.rerun()
        elif user_input in data.get("students", {}):
            st.session_state.logged_in = True
            st.session_state.role = "student"
            st.session_state.student_id = user_input
            st.rerun()
        else:
            st.error("❌ Invalid Login Credentials.")

# --- APPLICATION DASHBOARD ---
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.role.title()}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.student_id = ""
        st.session_state.success_message = None
        st.rerun()

    data = school_db.load_data()

    # --- STUDENT VIEW ---
    if st.session_state.role == "student":
        st.header("🎓 Student Dashboard")
        student_info = data["students"][st.session_state.student_id]
        
        st.metric(label=f"Welcome back, {student_info['name']}!", value=f"{student_info['points']} Tokens")
        
        st.write("---")
        st.subheader("🎁 Redeem Rewards")
        available_rewards = list(data.get("rewards", {}).keys())
        selected_reward = st.selectbox("Choose your reward:", available_rewards)
        
        if st.button("Redeem Reward", type="primary", use_container_width=True):
            success, message = school_db.process_redemption(st.session_state.student_id, selected_reward)
            if success:
                st.session_state.success_message = message
                st.rerun()
            else:
                st.error(message)

    # --- TEACHER VIEW ---
    elif st.session_state.role == "teacher":
        st.header("👨‍🏫 student Management Dashboard")
        
        tab1, tab2, tab3 = st.tabs(["Award Points", "Register Student", "Registered Students"])
        
        with tab1:
            st.subheader("➕ Award Tokens")
            student_list = list(data.get("students", {}).keys())
            if not student_list:
                st.warning("⚠️ No students registered yet. Please go to the Register tab first.")
            else:
                target_student = st.selectbox("Select Student ID:", student_list)
                points_to_add = st.number_input("Number of points to grant:", min_value=1, step=1, value=10)
                
                if st.button("Grant Points", type="primary", use_container_width=True):
                    success, new_balance, name = school_db.add_points_to_student(target_student, points_to_add)
                    if success:
                        # We slaan het bericht eerst op en herladen daarna pas!
                        st.session_state.success_message = f"✅ Granted {points_to_add} points to {name}! New total: {new_balance}"
                        st.rerun()
                    else:
                        st.error("❌ Transaction failed.")
                        
        with tab2:
            st.subheader("📝 Register New Student")
            new_id = st.text_input("Create Student ID (e.g., S101)").strip().upper()
            new_name = st.text_input("Enter Student Name").strip()
            
            if st.button("Register Student", type="primary", use_container_width=True):
                if not new_id or not new_name:
                    st.error("❌ Please fill in both fields.")
                else:
                    success, message = school_db.register_new_student(new_id, new_name)
                    if success:
                        st.session_state.success_message = f"✅ {message}"
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                    
        with tab3:
            st.subheader("📊 Roster Overview")
            if not data.get("students"):
                st.write("*No students registered in the database yet.*")
            else:
                for sid, info in data.get("students", {}).items():
                    st.write(f"🔹 **{sid}**: {info['name']} — `{info['points']} pts`")
