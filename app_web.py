import streamlit as st
import school_db
from streamlit.components.v1 import html
st.set_page_config(initial_sidebar_state="expanded")
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

st.title("🏆 School punten portal")

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
    st.subheader("🔐 Login a.u.b")
    user_input = st.text_input("gebruiker's naam (leerlingen nummer of 'docent')").strip().upper()
    password_input = st.text_input("wachtwoord (alleen voor docenten)", type="password").strip()
    
    if st.button("Login", use_container_width=True):
        data = school_db.load_data()
        
        if user_input == "DOCENT" and password_input == "password":
            st.session_state.logged_in = True
            st.session_state.role = "teacher"
            st.rerun()
        elif user_input in data.get("students", {}):
            st.session_state.logged_in = True
            st.session_state.role = "student"
            st.session_state.student_id = user_input
            st.rerun()
        else:
            st.error("❌ verkeerde login info.")

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
        st.header("🎒 leerling Dashboard")
        student_info = data["students"][st.session_state.student_id]

        st.metric(label=f"welkom terug, {student_info['name']}!", value=f"{student_info['points']} Tokens")

        st.write("---")
        st.subheader("🎁 beloning inwisselen")
        available_rewards = list(data.get("beloningen", {}).keys())
        selected_reward = st.selectbox("kies je beloning:", available_rewards)

        if st.button("beloning inwisselen", type="primary", use_container_width=True):
            success, message = school_db.process_redemption(st.session_state.student_id, selected_reward)
            if success:
                from supabase import create_client
                url = "https://iyajpmuprtpsulwkwpvt.supabase.co"
                key = "sb_publishable_Q1g2IiG0sjySDscB-yhhuw_oZkPzFNH"
                supabase = create_client(url, key)
                # 🟢 Logs the transaction automatically inside your Supabase claims table
                try:
                    supabase.table("claims").insert({
                        "student_name": student_info['name'],
                        "reward_name": selected_reward,
                        "status": "open"
                    }).execute()
                except Exception as e:
                    st.warning(f"punten genomen maar docent krijg het niet door ga naar docent vraag om een test of het systeem niet lukt: {e}")
                    
                st.session_state.success_message = message
                st.rerun()
            else:
                st.error(message)
        st.write("---")
        st.subheader("🎒 Verdien extra punten: Klasopdrachten")
        st.info("💡 Zo werkt het: vraag hieronder een opdracht aan. Zodra je docent deze goedkeurt en je de opdracht hebt voltooid, ga je naar de docent; hij of zij geeft je dan het aantal punten dat bij de opdracht hoort!")

        # 1. Define available tasks, token values, and descriptions
        available_tasks = [
            {"name": "🧹 Klaslokaal opruimen", "punten": 15, "beschrijving": "Veeg de vloer van het klaslokaal, ruim de bureaus op en maak de whiteboards schoon."},
            {"name": "🧮 Wiskundige-vergelijkingsassistent", "punten": 20, "beschrijving": "Help de leerkracht bij het uitleggen of opzetten van een wiskundige oplossing op het bord."},
            {"name": "📚 jonge helper", "punten": 10, "beschrijving": "help leraren hun klaslokaal klaar te zetten maar maak zorg dat je heb toesteming van de docenten."},
            {"name": "🗑️ Taken rond recycling en afval", "punten": 10, "omschrijving": "Leeg de papierbak uit het klaslokaal in de container in de gang."},
            {"name": "sterke bezorger","punten":20, "omschrijving": " help bij het bezorgen van zware spullen zoals dozen, stoelen, tafels en misschien meer."}
         ]

        # 2. Render each task in a clean grid card layout container
        for task in available_tasks:
            with st.container(border=True):
                col1, col2 = st.columns(spec=2)
                with col1:
                    st.markdown(f"### {task['name']}")
                    st.write(task['desc'])
                    st.markdown(f"🪙 **Payout:** `{task['points']} Tokens`")
                with col2:
# Dynamic string formatting ensures unique widget key profiles
                    button_key = f"req_{task['name'].lower().replace(' ', '_')}"

                    if st.button("taak aanvragen 📝", key=button_key, use_container_width=True):
                        try:
                            from supabase import create_client
                            url = "https://iyajpmuprtpsulwkwpvt.supabase.co"
                            key = "sb_publishable_Q1g2IiG0sjySDscB-yhhuw_oZkPzFNH"
                            supabase_local = create_client(url, key)

# 3. Check for existing active requests to prevent student spam
                            check_query = supabase_local.table("tasks").select("*").eq("student_name", student_info['name']).eq("task_name", task['name']).eq("status", "requested").execute()

                            if check_query.data:
                                st.warning("Er loopt al een actief, nog niet afgehandeld verzoek voor deze taak!")
                            else:
# 4. Push structural metadata row down to your Supabase tasks table
                                task_record = {
                                    "student_name": student_info['name'],
                                    "task_name": task['name'],
                                    "points_value": task['points'],
                                    "status": "requested"
                                }
                                supabase_local.table("tasks").insert(task_record).execute()
                                st.success("Taak succesvol aangevraagd! Laat je docent weten dat je klaar bent om te beginnen.")
                                st.rerun()

                        except Exception as e:
                            st.error(f"Task portal registry synchronization failure: {e}")

                
                    


    # --- TEACHER VIEW ---
elif st.session_state.role == "teacher":
        st.header("👨‍🏫 leerling Management Dashboard")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["punten aangeven", "leerlingen registreren", "geregistreerde leerlingen", "beweringen", "activiteitenverzoek"])
        
        with tab1:
            st.subheader("➕ punten aangeven")
            student_list = list(data.get("students", {}).keys())
            if not student_list:
                st.warning("⚠️ geen geregistreerde leerlingen ga naar die  tab en maak een leerling aan.")
            else:
                target_student = st.selectbox("kies leerling id:", student_list)
                points_to_add = st.number_input("totaal punten aangeven:", min_value=1, step=1, value=10)
                
                if st.button("geef punten aan", type="primary", use_container_width=True):
                    success, new_balance, name = school_db.add_points_to_student(target_student, points_to_add)
                    if success:
                        # We slaan het bericht eerst op en herladen daarna pas!
                        st.session_state.success_message = f"✅ Gegeven {points_to_add} punten naar {name}! nieuwe totaal: {new_balance}"
                        st.rerun()
                    else:
                        st.error("❌ Transactie mislukt.")
                        
        with tab2:
            st.subheader("📝 Registreer nieuw leerling")
            new_id = st.text_input("maak leerling ID ( voorbeeld, 12345)").strip().upper()
            new_name = st.text_input("typ leerling naam in").strip()
        
            if st.button("registreer leerling", type="primary", use_container_width=True):
                if not new_id or not new_name:
                    st.error("❌ vull elke veld a.u.b.")
                else:
                    success, message = school_db.register_new_student(new_id, new_name)
                    if success:
                        st.session_state.success_message = f"✅ {message}"
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
        with tab3:
            st.subheader("📊 Rooster view")
            if not data.get("students"):
                st.write("*geen leerlingen in database.*")
            else:
                for sid, info in data.get("students", {}).items():
                    st.write(f"🔹 **{sid}**: {info['name']} — `{info['points']} pts`")


        with tab4:
            st.subheader("📝 Openstaande claims voor beloningen voor leerlingen")

            # 1. Quietly refresh this tab every 5 seconds to look for new student claims
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=5000, key="live_claims_refresh")

            import pandas as pd
            from supabase import create_client

            # 2. Your working database credentials
            url = "https://iyajpmuprtpsulwkwpvt.supabase.co"
            key = "sb_publishable_Q1g2IiG0sjySDscB-yhhuw_oZkPzFNH"
            supabase_local = create_client(url, key)

            try:
                # 3. Fetch open claims from Supabase
                query = supabase_local.table("claims").select("*")
                response = query.eq("status", "open").order("created_at").execute()
                open_claims = response.data

                if not open_claims:
                    st.info("Er zijn momenteel geen openstaande claims. Goed gedaan!")
                else:
                    for claim in open_claims:
                        # Clean up the timestamp layout format
                        raw_time = str(claim.get("created_at", ""))
                        clean_time = raw_time.split(".")[0].replace("T", " ") if "T" in raw_time else raw_time


                        # 4. Your working 4-column alignment layout
                        col1, col2, col3, col4 = st.columns(spec=4)

                        with col1:
                            st.write(f"👤 **{claim['student_name']}**")
                        with col2:
                            st.write(f"🎟️ {claim['reward_name']}")
                        with col3:
                            st.write(f"📅 {clean_time}")
                        with col4:
                            # 5. When clicked, this now safely updates Supabase and makes the row disappear
                            if st.button("Given ✔️", key=f"claim_{claim['id']}"):
                                supabase_local.table("claims").update({"status": "Given"}).eq("id", claim['id']).execute()
                                st.success("Claim succesvol bijgewerkt!")
                                st.rerun()

            except Exception as e:
                st.error(f"Database connection trace error: {e}")

            with tab5:
                st.subheader("📋 Logboeken voor verificatie van leerlingen activiteiten en taken")
                
                # 1. Quietly refresh this panel every 5 seconds to listen for new student requests
                from streamlit_autorefresh import st_autorefresh
                st_autorefresh(interval=5000, key="live_teacher_tasks_sync")
    
                try:
                    # 2. Fetch active requested student tasks from Supabase
                    from supabase import create_client
                    url = "https://iyajpmuprtpsulwkwpvt.supabase.co"
                    key = "sb_publishable_Q1g2IiG0sjySDscB-yhhuw_oZkPzFNH"
                    supabase_local = create_client(url, key)
    
                    task_query = supabase_local.table("tasks").select("*").eq("status", "gevraagd").order("created_at").execute()
                    pending_tasks = task_query.data
    
                    if not pending_tasks:
                        st.info("Er zijn momenteel geen actieve serviceaanvragen voor klaslokalen in behandeling.")
                    else:
                        st.write("### Actieve serviceverzoeken voor het klaslokaal")
                        for requested_job in pending_tasks:
                            with st.container(border=True):
                                t_col1, t_col2, t_col3 = st.columns(spec=3)
                                
                                with t_col1:
                                    st.markdown(f"👤 **{requested_job['student_name']}** wilt:")
                                    st.markdown(f"### {requested_job['task_name']}")
                                with t_col2:
                                    st.markdown(f"🪙 **Value:** `{requested_job['points_value']} Tokens`")
                                with t_col3:
                                    # 3. Secure Verification Trigger Action Button
                                    approve_key = f"approve_task_{requested_job['id']}"
                                    if st.button(" klaar! ✔️", key=approve_key, use_container_width=True):
                                        
                                        # A. Update the task status block inside Supabase to 'approved'
                                        supabase_local.table("tasks").update({"status": "approved"}).eq("id", requested_job['id']).execute()
                                        
                                        # B. Fetch current student wallet profile row to add their points
                                        profile_query = supabase_local.table("profiles").select("tokens").eq("username", requested_job['student_name']).single().execute()
                                        current_tokens = profile_query.data.get("tokens", 0)
                                        new_token_total = current_tokens + requested_job['points_value']
                                        
                                        # C. Push the updated token balance directly into their student wallet
                                        supabase_local.table("profiles").update({"tokens": new_token_total}).eq("username", requested_job['student_name']).execute()
                                        
                                        st.success(f"Task verified! `{requested_job['points_value']}` tokens credited to {requested_job['student_name']}.")
                                        st.rerun()
                                        
                except Exception as e:
                    st.error(f"Database connection trace error: {e}")
