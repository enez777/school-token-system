import streamlit as st
import school_db

# Configure the web page layout
st.set_page_config(page_title="School Token Portal", page_icon="🏆", layout="centered")
# --- CUSTOM CSS TO FORCE-HIDE ALL WATERMARKS ---
hide_branding_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    </style>
"""
st.markdown(hide_branding_style, unsafe_allow_html=True)

st.title("🏆 School Token Portal")
st.write("Welcome to the school rewards system. PC or phone, this layout responds automatically!")

# --- LOGIN REGION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.student_id = ""

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
    # Sidebar logout option (looks like an app menu on mobile phones)
    st.sidebar.write(f"Logged in as: **{st.session_state.role.title()}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.student_id = ""
        st.rerun()

    data = school_db.load_data()

    # STUDENT PORTAL VIEW
    if st.session_state.role == "student":
        st.header("🎓 Student Dashboard")
        student_info = data["students"][st.session_state.student_id]
        
        # Display balance inside a clean visual box
        st.metric(label=f"Welcome back, {student_info['name']}!", value=f"{student_info['points']} Tokens")
        
        st.write("---")
        st.subheader("🎁 Redeem Rewards")
        available_rewards = list(data.get("rewards", {}).keys())
        selected_reward = st.selectbox("Choose your reward:", available_rewards)
        
        if st.button("Redeem Reward", type="primary", use_container_width=True):
            success, message = school_db.process_redemption(st.session_state.student_id, selected_reward)
            if success:
                st.success(message)
            else:
                st.error(message)

    # TEACHER PORTAL VIEW
    elif st.session_state.role == "teacher":
        st.header("👨‍🏫 Teacher Management Dashboard")
        
        # Streamlit automatically sorts this side-by-side on PCs, stack vertically on mobile phones!
        tab1, tab2 = st.tabs(["Award Points", "Registered Students"])
        
        with tab1:
            st.subheader("➕ Award Tokens")
            student_list = list(data.get("students", {}).keys())
            target_student = st.selectbox("Select Student ID:", student_list)
            points_to_add = st.number_input("Number of points to grant:", min_value=1, step=1, value=10)
            
            if st.button("Grant Points", type="primary", use_container_width=True):
                success, new_balance, name = school_db.add_points_to_student(target_student, points_to_add)
                if success:
                    st.success(f"✅ Granted {points_to_add} points to {name}! New total: {new_balance}")
                else:
                    st.error("❌ Transaction failed.")
                    
        with tab2:
            st.subheader("📊 Roster Overview")
            # Loop and print student point tallies nicely
            for sid, info in data.get("students", {}).items():
                st.write(f"🔹 **{sid}**: {info['name']} — `{info['points']} pts`")

