from supabase import create_client, Client

# =========================================================================
# ⚠️ CRUCIAL: COPY THESE TWO STRINGS DIRECTLY FROM YOUR SUPABASE PROJECT!
# Go to Supabase -> Project Settings (Gear icon) -> API -> Project API Keys
# =========================================================================
SUPABASE_URL = "https://iyajpmuprtpsulwkwpvt.supabase.co"
SUPABASE_KEY = "sb_publishable_Q1g2IiG0sjySDscB-yhhuw_oZkPzFNH"

def load_data():
    """Fetches all students dynamically from the cloud database to match your old format."""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("students").select("*").execute()
        
        # Restructure database rows back into a dictionary so app_web.py doesn't break
        formatted_students = {}
        for row in response.data:
            formatted_students[row["id"]] = {"name": row["name"], "points": row["points"]}
            
        # Hardcoded backup rewards since they don't change often
        return {
            "students": formatted_students,
            "rewards": {"movie_ticket": 40, "canteen_coupon": 20}
        }
    except Exception as e:
        print(f"Database Error: {e}")
        return {"students": {}, "rewards": {}}

def add_points_to_student(student_id, amount):
    """Updates points directly in the cloud database table."""
    data = load_data()
    if student_id in data["students"]:
        current_points = data["students"][student_id]["points"]
        new_total = current_points + amount
        
        # Tell the cloud database to update the specific row matching the student's ID
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        supabase.table("students").update({"points": new_total}).eq("id", student_id).execute()
        return True, new_total, data["students"][student_id]["name"]
    return False, 0, ""

def process_redemption(student_id, reward_name):
    """Handles secure cloud validation and balance deduction."""
    data = load_data()
    if student_id not in data["students"] or reward_name not in data["rewards"]:
        return False, "Invalid Student ID or Reward."
        
    student = data["students"][student_id]
    cost = data["rewards"][reward_name]
    
    if student["points"] >= cost:
        new_total = student["points"] - cost
        # Tell the cloud database to update the specific row matching the student's ID
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        supabase.table("students").update({"points": new_total}).eq("id", student_id).execute()
        return True, f"Success! {student['name']} redeemed {reward_name}. Remaining: {new_total} pts"
    else:
        return False, f"Insufficient points. Needs {cost - student['points']} more points."

def register_new_student(student_id, name):
    """Inserts a brand-new row into the cloud database storage."""
    data = load_data()
    if student_id in data["students"]:
        return False, "This Student ID already exists."
    
    # Insert row directly into cloud storage
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    supabase.table("students").insert({"id": student_id, "name": name, "points": 0}).execute()
    return True, f"Successfully registered {name} in the cloud!"

