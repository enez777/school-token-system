import customtkinter as ctk
import school_db

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SchoolTokenApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("School Token Portal")
        self.geometry("450x300")  # Start with a small window for login
        self.resizable(False, False)
        
        # Track logged-in state
        self.current_user_role = None  # Will be "student" or "teacher"
        self.logged_in_student_id = None
        
        # --- LOGIN SCREEN ELEMENTS ---
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.welcome_label = ctk.CTkLabel(self.login_frame, text="🏆 School Token Portal", font=ctk.CTkFont(size=22, weight="bold"))
        self.welcome_label.pack(pady=15)
        
        self.user_input = ctk.CTkEntry(self.login_frame, placeholder_text="Student ID or 'Teacher'", width=220)
        self.user_input.pack(pady=10)
        
        self.pass_input = ctk.CTkEntry(self.login_frame, placeholder_text="Password (Teachers only)", show="*", width=220)
        self.pass_input.pack(pady=10)
        
        self.login_btn = ctk.CTkButton(self.login_frame, text="Login", command=self.handle_login)
        self.login_btn.pack(pady=15)
        
        # --- DASHBOARD ELEMENTS (Hidden initially) ---
        self.dash_frame = ctk.CTkFrame(self)
        
    def handle_login(self):
        username = self.user_input.get().strip().upper()
        password = self.pass_input.get().strip()
        
        data = school_db.load_data()
        
        # Check Teacher Login
        if username == "TEACHER":
            if password == "admin123":
                self.current_user_role = "teacher"
                self.setup_dashboard()
            else:
                self.show_error_popup("❌ Incorrect staff password.")
        
        # Check Student Login
        elif username in data.get("students", {}):
            self.current_user_role = "student"
            self.logged_in_student_id = username
            self.setup_dashboard()
        
        else:
            self.show_error_popup("❌ Invalid User ID or Account Not Found.")

    def show_error_popup(self, text):
        # Temporarily repurpose welcome text for quick error alerts
        self.welcome_label.configure(text=text, text_color="red")

    def setup_dashboard(self):
        """Destroys the login screen layout and builds the personalized view."""
        self.login_frame.pack_forget() # Hide login view
        self.geometry("500x550")        # Resize to full application dashboard size
        self.dash_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title Label
        role_title = "👨‍🏫 student management Dashboard" if self.current_user_role == "teacher" else "🎓 Student Portal"
        self.title_label = ctk.CTkLabel(self.dash_frame, text=role_title, font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=15)
        
        # Input Box: Student ID
        self.id_label = ctk.CTkLabel(self.dash_frame, text="Student Target ID:")
        self.id_label.pack(pady=2)
        
        self.id_entry = ctk.CTkEntry(self.dash_frame, width=200)
        self.id_entry.pack(pady=5)
        
        if self.current_user_role == "student":
            self.id_entry.insert(0, self.logged_in_student_id)
            self.id_entry.configure(state="disabled") # LOCK entry so students can't view others!
            
        # Button: Check Balance
        self.balance_btn = ctk.CTkButton(self.dash_frame, text="Check My Balance", command=self.gui_check_balance)
        self.balance_btn.pack(pady=5)
        
        # Section Divider
        self.divider1 = ctk.CTkLabel(self.dash_frame, text="----------------------------------------", text_color="gray")
        self.divider1.pack(pady=5)
        
        # Dropdown Menu
        self.reward_label = ctk.CTkLabel(self.dash_frame, text="Select a Reward to Redeem:")
        self.reward_label.pack(pady=2)
        
        db_data = school_db.load_data()
        available_rewards = list(db_data.get("rewards", {}).keys())
        if not available_rewards: available_rewards = ["No Rewards Found"]
            
        self.reward_dropdown = ctk.CTkOptionMenu(self.dash_frame, values=available_rewards, width=200)
        self.reward_dropdown.pack(pady=5)
        
        # Button: Redeem Reward
        self.redeem_btn = ctk.CTkButton(self.dash_frame, text="Redeem Selected Reward", fg_color="orange", hover_color="darkorange", command=self.gui_redeem_reward)
        self.redeem_btn.pack(pady=5)
        
        # --- CONDITIONAL STAFF SECTION ---
        if self.current_user_role == "teacher":
            self.divider2 = ctk.CTkLabel(self.dash_frame, text="----------------------------------------", text_color="gray")
            self.divider2.pack(pady=5)
            
            self.points_label = ctk.CTkLabel(self.dash_frame, text="Staff Control: Points to Add")
            self.points_label.pack(pady=2)
            self.points_entry = ctk.CTkEntry(self.dash_frame, placeholder_text="e.g., 10", width=200)
            self.points_entry.pack(pady=5)
            
            self.award_btn = ctk.CTkButton(self.dash_frame, text="Award Points", fg_color="green", hover_color="darkgreen", command=self.gui_award_points)
            self.award_btn.pack(pady=5)
            
        # Log Box for Outputs
        self.log_label = ctk.CTkLabel(self.dash_frame, text="System Notification:")
        self.log_label.pack(pady=(15, 2))
        self.log_box = ctk.CTkTextbox(self.dash_frame, width=400, height=80, state="disabled")
        self.log_box.pack(pady=5)

    def update_log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", ctk.END)
        self.log_box.insert("1.0", text)
        self.log_box.configure(state="disabled")

    def gui_check_balance(self):
        student_id = self.id_entry.get().strip().upper()
        data = school_db.load_data()
        if student_id in data.get("students", {}):
            student = data["students"][student_id]
            self.update_log(f"📊 Student Profile: {student['name']}\nCurrent Balance: {student['points']} tokens")
        else:
            self.update_log("❌ Error: Target Student ID not found.")

    def gui_award_points(self):
        if self.current_user_role != "teacher": return # Safety latch
        student_id = self.id_entry.get().strip().upper()
        try:
            points = int(self.points_entry.get().strip())
            success, new_balance, name = school_db.add_points_to_student(student_id, points)
            if success:
                self.update_log(f"✅ Awarded {points} points to {name}!\nNew Account Balance: {new_balance} tokens")
                self.points_entry.delete(0, ctk.END)
            else:
                self.update_log("❌ Error: Target Student ID not found.")
        except ValueError:
            self.update_log("❌ Error: Please input an integer point amount.")

    def gui_redeem_reward(self):
        student_id = self.id_entry.get().strip().upper()
        selected_reward = self.reward_dropdown.get()
        if selected_reward == "No Rewards Found" or not student_id:
            return
            
        success, message = school_db.process_redemption(student_id, selected_reward)
        if success:
            self.update_log(f"✅ {message}")
        else:
            self.update_log(f"❌ {message}")

if __name__ == "__main__":
    app = SchoolTokenApp()
    app.mainloop()
