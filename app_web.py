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

                # --- SEARCH FILTER FOR CLAIMS ---
                if student_search:
                    open_claims = [
                        claim for claim in open_claims
                        if student_search in str(claim.get("student_name", "")).lower()
                    ]

                if not open_claims:
                    if student_search:
                        st.info("🔎 Geen openstaande aanvragen gevonden voor deze student.")
                    else:
                        st.info("Er zijn momenteel geen openstaande aanvragen. Goed gedaan!")
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
                            if st.button("Gegeven ✔️", key=f"claim_{claim['id']}"):
                                supabase_local.table("claims").update({"status": "Given"}).eq("id", claim['id']).execute()
                                st.success("Aanvraag succesvol bijgewerkt!")
                                st.rerun()

            except Exception as e:
                st.error(f"Fout bij het verbinden met de database: {e}")

            with tab5:
                st.subheader("📋 Logboek studentenactiviteiten en taakverificatie")
                
                # 1. Quietly refresh this panel every 5 seconds to listen for new student requests
                from streamlit_autorefresh import st_autorefresh
                st_autorefresh(interval=5000, key="live_teacher_tasks_sync")
    
                try:
                    # 2. Fetch active requested student tasks from Supabase
                    from supabase import create_client
                    url = "https://iyajpmuprtpsulwkwpvt.supabase.co"
                    key = "sb_publishable_Q1g2IiG0sjySDscB-yhhuw_oZkPzFNH"
                    supabase_local = create_client(url, key)
    
                    task_query = supabase_local.table("tasks").select("*").eq("status", "requested").order("created_at").execute()
                    pending_tasks = task_query.data

                    # --- SEARCH FILTER FOR ACTIVITY REQUESTS ---
                    if student_search:
                        pending_tasks = [
                            requested_job for requested_job in pending_tasks
                            if student_search in str(requested_job.get("student_name", "")).lower()
                        ]
    
                    if not pending_tasks:
                        if student_search:
                            st.info("🔎 Geen actieve aanvragen gevonden voor deze student.")
                        else:
                            st.info("Er zijn momenteel geen actieve aanvragen voor klassendiensten.")
                    else:
                        st.write("### Actieve aanvragen voor klassendiensten")
                        for requested_job in pending_tasks:
                            with st.container(border=True):
                                t_col1, t_col2, t_col3 = st.columns(spec=3)
                                
                                with t_col1:
                                    st.markdown(f"👤 **{requested_job['student_name']}** wil het volgende doen:")
                                    st.markdown(f"### {requested_job['task_name']}")
                                with t_col2:
                                    st.markdown(f"🪙 **Waarde:** `{requested_job['points_value']} Tokens`")
                                with t_col3:
                                    # 3. Secure Verification Trigger Action Button
                                    approve_key = f"approve_task_{requested_job['id']}"
                                    if st.button("Taak voltooid ✔️", key=approve_key, use_container_width=True):
                                        
                                        # A. Update the task status block inside Supabase to 'approved'
                                        supabase_local.table("tasks").update({"status": "approved"}).eq("id", requested_job['id']).execute()
                                        
                                        # B. Fetch current student wallet profile row to add their points
                                        profile_query = supabase_local.table("profiles").select("tokens").eq("username", requested_job['student_name']).single().execute()
                                        current_tokens = profile_query.data.get("tokens", 0)
                                        new_token_total = current_tokens + requested_job['points_value']
                                        
                                        # C. Push the updated token balance directly into their student wallet
                                        supabase_local.table("profiles").update({"tokens": new_token_total}).eq("username", requested_job['student_name']).execute()
                                        
                                        st.success(f"Taak geverifieerd! `{requested_job['points_value']}` tokens zijn bijgeschreven voor {requested_job['student_name']}.")
                                        st.rerun()
                                        
                except Exception as e:
                    st.error(f"Fout bij het verbinden met de database: {e}")
